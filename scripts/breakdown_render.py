#!/usr/bin/env python3
"""
Phase B of the Mugi director video-shot-breakdown skill.

Takes the Phase-A manifest (per-shot timecode + strip path) plus the breakdown
rows Mugi filled in the middle vision step, and produces a Schema-v8 (audio cut,
10-col) xlsx with the trajectory strip embedded inline on each shot row. Then it
creates a PER-JOB Drive folder under the docgen folder and uploads the xlsx +
every strip + manifest.json into it, so the team can browse the raw contact
sheets and re-render without re-extracting.

It does NOT clean the work dir -- the playbook does that AFTER this step uploads
the folder, because the strips must still exist on disk to be uploaded here.

Pipeline (deterministic, no reasoning):
  1. Load manifest.json (shots + strip paths + title) and rows.json (Mugi's
     filled columns, keyed by shot number).
  2. Build the workbook: header row + one row per shot. Shot # / Timecode come
     from the manifest; the 8 description columns come from rows.json; the strip
     is scaled down and embedded inline.
  3. Save the xlsx into the work dir.
  4. Unless --no-upload: create_folder(<job name>) under docgen, upload xlsx +
     all strips + manifest.json into it, return the folder + xlsx links.

Usage (CLI):
  python3 scripts/breakdown_render.py --manifest <manifest.json> --rows <rows.json> \
      [--title NAME] [--folder-name NAME] [--out <xlsx path>] \
      [--parent <drive-folder-id>] [--no-upload]

rows.json = a JSON array of objects, one per shot:
  [{"shot": 1, "subject": "...", "live_action": "...", "framing": "...",
    "editing": "...", "vfx": "...", "mg_text": "...", "transition": "...",
    "note": ""}, ...]
Shots missing from rows.json still get a row (strip + timecode from manifest,
description cells blank) -- never silently dropped.

Output: single line JSON to stdout. On error: {"status":"error","error":...},
exit code 0 (caller parses status). Never prints secret values.
"""

import argparse
import json
import os
import re
import tempfile
from pathlib import Path

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from PIL import Image as PILImage

# Schema v8 minus the two audio columns. The strip is an extra visual column
# (the dreamlin76 thread's embedded-thumbnail idea); it is not one of the 10.
# Display header  ->  rows.json key
COLUMNS = [
    ("Shot #",                     None),          # from manifest
    ("Strip",                      None),          # embedded image
    ("Timecode(s)",                None),          # from manifest
    ("Subject",                    "subject"),
    ("Live Action Description",    "live_action"),
    ("Framing, Angle & Motion",    "framing"),
    ("Editing effects",            "editing"),
    ("VFX & Behavior",             "vfx"),
    ("MG, Text & Animation",       "mg_text"),
    ("Transition out",             "transition"),
    ("Kary's Note",                "note"),
]

# Per-column Excel width (chars). Strip is wide to fit the embedded contact sheet.
COL_WIDTHS = [7, 100, 17, 20, 34, 30, 20, 24, 24, 18, 22]

EMBED_W = 700          # px width the strip is scaled to before embedding
HEADER_FILL = "1F2430"
HEADER_FONT = "FFFFFF"
THIN = Side(style="thin", color="D0D0D0")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def _safe_name(s, fallback="breakdown"):
    s = re.sub(r"[^\w\-. ]+", "", (s or "").strip()).strip()
    s = re.sub(r"\s+", " ", s)
    return s[:80] or fallback


def _scaled_strip(strip_path, tmp_dir):
    """Write a width-EMBED_W copy of the strip for inline embed. Returns (path, w, h)."""
    im = PILImage.open(strip_path)
    if im.mode != "RGB":
        im = im.convert("RGB")
    w, h = im.size
    if w > EMBED_W:
        h = int(h * EMBED_W / w)
        w = EMBED_W
        im = im.resize((w, h), PILImage.LANCZOS)
    out = Path(tmp_dir) / (Path(strip_path).stem + "_embed.jpg")
    im.save(out, quality=85)
    return str(out), w, h


def build_workbook(manifest, rows_by_shot, embed_tmp):
    wb = Workbook()
    ws = wb.active
    ws.title = "Shot Breakdown"

    head_fill = PatternFill("solid", fgColor=HEADER_FILL)
    head_font = Font(bold=True, color=HEADER_FONT, size=11)
    for c, (label, _) in enumerate(COLUMNS, 1):
        cell = ws.cell(row=1, column=c, value=label)
        cell.fill = head_fill
        cell.font = head_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
        ws.column_dimensions[get_column_letter(c)].width = COL_WIDTHS[c - 1]
    ws.row_dimensions[1].height = 28
    ws.freeze_panes = "A2"

    wrap_top = Alignment(horizontal="left", vertical="top", wrap_text=True)
    center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    strip_col_letter = get_column_letter(2)

    r = 2
    for shot in manifest["shots"]:
        sn = shot["shot"]
        row = rows_by_shot.get(sn, {})
        timecode = f"{shot['start_tc']} → {shot['end_tc']}  ({shot['duration_sec']}s)"

        ws.cell(row=r, column=1, value=sn).alignment = center
        ws.cell(row=r, column=3, value=timecode).alignment = wrap_top
        for c, (_, key) in enumerate(COLUMNS, 1):
            if key is None:
                continue
            ws.cell(row=r, column=c, value=row.get(key, "")).alignment = wrap_top

        # Embed the scaled strip inline; size the row + col to it.
        strip_path = shot.get("strip")
        row_h = 90
        if strip_path and os.path.exists(strip_path):
            embed_path, ew, eh = _scaled_strip(strip_path, embed_tmp)
            img = XLImage(embed_path)
            img.width, img.height = ew, eh
            img.anchor = f"{strip_col_letter}{r}"
            ws.add_image(img)
            row_h = eh * 0.75 + 8          # px -> points, plus a little padding
        ws.row_dimensions[r].height = max(row_h, 60)

        for c in range(1, len(COLUMNS) + 1):
            ws.cell(row=r, column=c).border = BORDER
        r += 1

    return wb


def render(manifest_path, rows_path, title, folder_name, out_path, parent, do_upload):
    with open(manifest_path) as f:
        manifest = json.load(f)
    rows = []
    if rows_path and os.path.exists(rows_path):
        with open(rows_path) as f:
            rows = json.load(f)
    rows_by_shot = {int(r["shot"]): r for r in rows if "shot" in r}

    work_dir = Path(manifest.get("work_dir") or os.path.dirname(manifest_path))
    job_title = title or manifest.get("source", {}).get("title") or "breakdown"
    if not out_path:
        out_path = str(work_dir / f"{_safe_name(job_title)} - breakdown.xlsx")

    embed_tmp = tempfile.mkdtemp(prefix="breakdown_embed_", dir=str(work_dir))
    wb = build_workbook(manifest, rows_by_shot, embed_tmp)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    wb.save(out_path)

    result = {
        "status": "ok",
        "xlsx_path": os.path.abspath(out_path),
        "n_shots": len(manifest["shots"]),
        "n_rows_filled": len(rows_by_shot),
        "uploaded": False,
    }

    if do_upload:
        # Lazy import so a --no-upload render needs no Drive creds.
        from breakdown_gdrive import create_folder, upload_file, get_drive_service
        svc = get_drive_service()
        fname = _safe_name(folder_name or job_title)
        folder = create_folder(fname, parent_id=parent, service=svc)
        fid = folder["id"]

        up_xlsx = upload_file(out_path, parent_id=fid, service=svc)
        uploaded = [os.path.basename(out_path)]
        # All strips + the manifest, so the team can re-render without re-extracting.
        strips_dir = work_dir / "strips"
        if strips_dir.is_dir():
            for strip in sorted(strips_dir.glob("*.jpg")):
                upload_file(str(strip), parent_id=fid, service=svc)
                uploaded.append(strip.name)
        if os.path.exists(manifest_path):
            upload_file(manifest_path, parent_id=fid, name="manifest.json", service=svc)
            uploaded.append("manifest.json")

        result.update({
            "uploaded": True,
            "folder": {"id": fid, "name": folder.get("name"), "link": folder.get("link")},
            "xlsx": {"id": up_xlsx["id"], "link": up_xlsx["link"]},
            "uploaded_files": uploaded,
        })

    return result


def _cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--rows", default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--folder-name", default=None, dest="folder_name")
    ap.add_argument("--out", default=None)
    ap.add_argument("--parent", default=None)
    ap.add_argument("--no-upload", action="store_true", dest="no_upload")
    a = ap.parse_args()
    result = render(a.manifest, a.rows, a.title, a.folder_name, a.out,
                    a.parent, not a.no_upload)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try:
        _cli()
    except Exception as e:  # noqa: BLE001 - CLI surfaces all errors as JSON
        print(json.dumps({"status": "error", "error": f"{type(e).__name__}: {e}"},
                         ensure_ascii=False))
