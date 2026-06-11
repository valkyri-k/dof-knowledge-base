#!/usr/bin/env python3
"""
Phase A of the Mugi director video-shot-breakdown skill.

Pipeline (deterministic, no reasoning — that happens in the middle vision step):
  1. Download source video from a URL
       - YouTube  -> yt-dlp
       - Google Drive -> breakdown_gdrive.download_drive (auth as dof.internal)
  2. Shot detection (scenedetect ContentDetector) + optional pHash same-shot merge
     -- ported from Shotnest (016) so boundaries match the local power-user tool.
  3. For EACH final shot, sample N equidistant frames within the shot and stitch
     a horizontal "trajectory strip" (left->right = time). The strip is what Mugi
     reads with native vision to fill the breakdown columns -- a strip recovers
     motion that a single representative frame loses.
  4. Write manifest.json (per-shot timecode + strip path) into the work dir.

This script does NOT call any vision model. It outputs strips + a manifest; the
playbook then has Mugi read each strip and fill the 10 Schema-v8 columns, and
breakdown_render.py (Phase B) turns that into the xlsx.

Usage (CLI):
  python3 scripts/breakdown_extract.py <youtube-or-drive-url> [options]

Options:
  -s, --sensitivity {coarse,normal,fine,max}   detection preset (default normal=18)
                                               coarse=27 normal=18 fine=10 max=5
  --threshold FLOAT      explicit ContentDetector threshold (overrides -s)
  --n-frames INT         force N frames per shot strip (default adaptive 4-8)
  --source {auto,youtube,drive}   override URL auto-detection (default auto)
  --work-dir DIR         where to put the download + frames + manifest
                         (default: a fresh /tmp/breakdown_* dir)

Output: single line JSON to stdout. On error: {"status":"error","error":...},
exit code 0 (caller parses status). Strips + manifest.json live in the work dir.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from scenedetect import detect, ContentDetector
from PIL import Image, ImageDraw, ImageFont

# pHash same-shot merge is a quality refinement, not a hard requirement. If
# imagehash is absent we fall back to raw scenedetect boundaries and flag
# phash_merge:false in the manifest. (imagehash is installed on the container's
# persistent volume, so this fallback only fires in a stripped env.)
try:
    import imagehash
    HAVE_IMAGEHASH = True
except ImportError:
    HAVE_IMAGEHASH = False

SENS = {"coarse": 27.0, "normal": 18.0, "fine": 10.0, "max": 5.0}


# ---------- source download ----------

def detect_source(url):
    """Classify a URL as 'youtube' or 'drive'. Raises on anything else."""
    u = url.lower()
    if "youtube.com" in u or "youtu.be" in u:
        return "youtube"
    if "drive.google.com" in u or "docs.google.com" in u:
        return "drive"
    raise ValueError(
        "Cannot auto-detect source from URL; pass --source youtube|drive. "
        "Only YouTube and Google Drive URLs are supported."
    )


def yt_cookies_file(override=None):
    """Path to a dof.internal YouTube cookies.txt, or None if not provisioned.

    yt-dlp on a Zeabur datacenter IP gets 'Sign in to confirm you're not a bot'
    without cookies. The file lives on the PERSISTENT volume (NOT in the git
    repo -- it's a credential) and must be re-exported when it expires. Resolve
    order: explicit --cookies override > $YOUTUBE_COOKIES_FILE > default path.
    """
    p = override or os.environ.get("YOUTUBE_COOKIES_FILE") \
        or "/home/node/.config/yt-dlp/cookies.txt"
    return p if os.path.exists(p) else None


def js_runtime_args():
    """yt-dlp needs a JS runtime to solve YouTube's 'n' challenge (EJS), else
    'No video formats found'. Only deno is enabled by default; node/bun must be
    named explicitly via --js-runtimes. Pick the first one actually on PATH.
    Requires the yt-dlp-ejs solver scripts (pip --user) to be installed too.
    """
    import shutil
    for rt in ("node", "bun", "deno"):
        if shutil.which(rt):
            return ["--js-runtimes", rt]
    return []


def download_youtube(url, work_dir, cookies=None):
    """Download a YouTube video with yt-dlp. Returns (path, title)."""
    out_tmpl = str(work_dir / "source.%(ext)s")
    cookie_args = ["--cookies", cookies] if cookies else []
    js_args = js_runtime_args()
    # mp4-preferred, single progressive/merged file, capped at 1080p to keep
    # frame grabs fast -- breakdown only needs legible stills, not master quality.
    subprocess.run(
        ["yt-dlp", "-q", "--no-warnings", *cookie_args, *js_args,
         "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio/best[height<=1080]/best",
         "--merge-output-format", "mp4",
         "-o", out_tmpl, url],
        check=True,
    )
    files = sorted(work_dir.glob("source.*"))
    if not files:
        raise RuntimeError("yt-dlp produced no output file")
    video = files[0]
    title = subprocess.run(
        ["yt-dlp", "-q", "--no-warnings", *cookie_args, *js_args,
         "--print", "%(title)s", url],
        capture_output=True, text=True,
    ).stdout.strip() or video.stem
    return video, title


def download_drive(url, work_dir):
    """Download a Drive video as dof.internal. Returns (path, title)."""
    # Imported lazily so detection-only test runs don't require Drive creds.
    from breakdown_gdrive import download_drive as gdrive_download
    dest = work_dir / "source_drive.bin"
    meta = gdrive_download(url, str(dest))
    name = meta.get("name") or "drive_video"
    # Give the file its real extension so ffmpeg/scenedetect demux it cleanly.
    ext = Path(name).suffix or ".mp4"
    video = work_dir / f"source{ext}"
    os.replace(dest, video)
    return video, Path(name).stem


# ---------- shot detection (ported from Shotnest shotcut.py) ----------

def tc(sec, fps):
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = int(sec % 60)
    f = int(round((sec - int(sec)) * fps))
    return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"


def probe_fps_duration(video):
    """ffprobe fallback for fps + duration when scenedetect finds no cuts."""
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_streams", "-show_format", str(video)],
        capture_output=True, text=True).stdout
    d = json.loads(out)
    vs = next(s for s in d["streams"] if s["codec_type"] == "video")
    num, den = vs["r_frame_rate"].split("/")
    fps = float(num) / float(den)
    dur = float(vs.get("duration") or d["format"]["duration"])
    return fps, dur


def grab_frame(video, ts_sec, out_path):
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y",
        "-ss", f"{ts_sec:.3f}", "-i", str(video),
        "-frames:v", "1", "-q:v", "3", str(out_path)
    ], check=True)


def phash(path):
    return imagehash.phash(Image.open(path), hash_size=16)  # 256-bit hash


def _font(size):
    for cand in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/System/Library/Fonts/PingFang.ttc"):
        try:
            return ImageFont.truetype(cand, size)
        except Exception:
            continue
    return ImageFont.load_default()


def detect_shots(video, threshold, phash_merge, tmp):
    """Return (fps, merged_shots, n_raw). merged_shots = list of {start,end,sub_count}."""
    scenes = detect(str(video), ContentDetector(threshold=threshold, min_scene_len=5))
    if scenes:
        fps = scenes[0][0].framerate
        shots_sec = [(s.seconds, e.seconds) for s, e in scenes]
    else:
        # No cuts -> whole video is one continuous shot (single-shot clip).
        fps, dur = probe_fps_duration(video)
        shots_sec = [(0.0, dur)]
    n_raw = len(shots_sec)

    if not HAVE_IMAGEHASH or n_raw <= 1:
        merged = [{"start": s, "end": e, "sub_count": 1} for s, e in shots_sec]
        return fps, merged, n_raw

    # pHash chain-merge: collapse consecutive shots whose mid frames look alike
    # (prefer under-merge; missed splits get fixed in UI, false positives don't).
    probes = []
    for i, (s_sec, e_sec) in enumerate(shots_sec):
        mid = s_sec + (e_sec - s_sec) / 2
        probe = tmp / f"probe_{i:03d}.jpg"
        grab_frame(video, mid, probe)
        probes.append(probe)
    hashes = [phash(p) for p in probes]
    merged = [{"start": shots_sec[0][0], "end": shots_sec[0][1], "sub_count": 1}]
    for i in range(1, len(shots_sec)):
        if hashes[i] - hashes[i - 1] <= phash_merge:
            merged[-1]["end"] = shots_sec[i][1]
            merged[-1]["sub_count"] += 1
        else:
            merged.append({"start": shots_sec[i][0], "end": shots_sec[i][1], "sub_count": 1})
    return fps, merged, n_raw


# ---------- trajectory strips ----------

def traj_positions(duration, n_override=None):
    """Relative-second sample points within a shot (adaptive N=4-8, padded off cuts)."""
    n = n_override if n_override else max(4, min(8, round(duration / 1.2)))
    n = max(n, 2)
    pad = min(max(0.1, duration * 0.05), duration * 0.25)
    us, ue = pad, duration - pad
    if n == 1:
        return [duration / 2]
    step = (ue - us) / (n - 1)
    return [us + k * step for k in range(n)]


def build_strip(path, frames_list, shot_idx, g, fps):
    """One horizontal strip per shot: N thumbs left->right = time progression."""
    n = len(frames_list)
    thumb_w, pad, header_h, label_h = 360, 10, 40, 40
    first = Image.open(frames_list[0]["path"])
    thumb_h = int(thumb_w * first.height / first.width)
    cell_w = thumb_w + pad
    W = cell_w * n + pad
    H = header_h + thumb_h + label_h + pad * 2
    strip = Image.new("RGB", (W, H), (20, 20, 24))
    draw = ImageDraw.Draw(strip)
    font, font_sm = _font(18), _font(15)
    dur = round(g["end"] - g["start"], 2)
    draw.text((pad, pad),
              f"SHOT {shot_idx:03d}   {tc(g['start'], fps)} -> {tc(g['end'], fps)}   ({dur}s)   {n} frames",
              fill=(255, 180, 80), font=font)
    for k, fr in enumerate(frames_list):
        x = pad + k * cell_w; y = header_h + pad
        img = Image.open(fr["path"]).resize((thumb_w, thumb_h), Image.LANCZOS)
        strip.paste(img, (x, y))
        draw.text((x, y + thumb_h + 4), f"f{k+1:02d}  +{fr['rel']:.1f}s",
                  fill=(230, 230, 235), font=font_sm)
    strip.save(path, quality=88)


# ---------- main ----------

def run(url, threshold, phash_merge, n_override, source, work_dir, cookies=None):
    work_dir = Path(work_dir)
    frames_dir = work_dir / "frames"
    strips_dir = work_dir / "strips"
    frames_dir.mkdir(parents=True, exist_ok=True)
    strips_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="breakdown_probe_", dir=str(work_dir)))

    src_type = source if source != "auto" else detect_source(url)
    if src_type == "youtube":
        video, title = download_youtube(url, work_dir, cookies=yt_cookies_file(cookies))
    else:
        video, title = download_drive(url, work_dir)

    fps, merged, n_raw = detect_shots(video, threshold, phash_merge, tmp)

    shots = []
    for i, g in enumerate(merged, 1):
        dur = g["end"] - g["start"]
        rels = traj_positions(dur, n_override)
        frames_list = []
        for k, rel in enumerate(rels, 1):
            abs_ts = g["start"] + rel
            fp = frames_dir / f"shot_{i:03d}_f{k:02d}.jpg"
            grab_frame(video, abs_ts, fp)
            frames_list.append({"rel": rel, "path": fp})
        strip_path = strips_dir / f"shot_{i:03d}_strip.jpg"
        build_strip(strip_path, frames_list, i, g, fps)
        shots.append({
            "shot": i,
            "start_tc": tc(g["start"], fps),
            "end_tc": tc(g["end"], fps),
            "start_sec": round(g["start"], 3),
            "end_sec": round(g["end"], 3),
            "duration_sec": round(dur, 2),
            "sub_shots": g["sub_count"],
            "n_frames": len(frames_list),
            "strip": str(strip_path),
        })

    manifest = {
        "status": "ok",
        "source": {
            "type": src_type, "url": url, "title": title,
            "video_path": str(video), "fps": round(fps, 3),
        },
        "detection": {
            "threshold": threshold, "phash_merge": HAVE_IMAGEHASH,
            "n_raw": n_raw, "n_shots": len(shots),
        },
        "work_dir": str(work_dir),
        "manifest_path": str(work_dir / "manifest.json"),
        "shots": shots,
    }
    with (work_dir / "manifest.json").open("w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    return manifest


def _cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("-s", "--sensitivity", choices=list(SENS), default=None)
    ap.add_argument("--threshold", type=float, default=None)
    ap.add_argument("--n-frames", type=int, default=None, dest="n_frames")
    ap.add_argument("--source", choices=["auto", "youtube", "drive"], default="auto")
    ap.add_argument("--phash", type=int, default=90)
    ap.add_argument("--work-dir", default=None, dest="work_dir")
    ap.add_argument("--cookies", default=None,
                    help="YouTube cookies.txt path (overrides $YOUTUBE_COOKIES_FILE)")
    a = ap.parse_args()

    threshold = a.threshold if a.threshold is not None \
        else (SENS[a.sensitivity] if a.sensitivity else 18.0)
    work_dir = a.work_dir or tempfile.mkdtemp(prefix="breakdown_")

    manifest = run(a.url, threshold, a.phash, a.n_frames, a.source, work_dir,
                   cookies=a.cookies)
    # Emit the full manifest as one line so Mugi parses the shot list + strip
    # paths directly; manifest.json on disk is the same payload for re-reads.
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    try:
        _cli()
    except Exception as e:  # noqa: BLE001 - CLI surfaces all errors as JSON
        print(json.dumps({"status": "error", "error": f"{type(e).__name__}: {e}"},
                         ensure_ascii=False))
