#!/usr/bin/env python3
"""
Backward-from-final-anchor timeline generator for Mugi producer skill.

Usage:
  python3 scripts/timeline_backward.py \
    --final-output 2026-06-15 \
    --shoot-mode standard \
    --shoot-date 2026-05-19 \
    --has-vo true \
    --has-style-frame true \
    --project "J26015 ProjectName"

Output: single line JSON to stdout. All diagnostics via JSON `warnings` array.
On error: JSON with `status: "error"` + `error` field. Exit code 0 (Mugi parses
status field).

This script is the single source of truth for timeline math. Mugi's job is to
parse user input → build args → invoke this script → parse JSON → compose Discord
reply. No inline Python scripting from Mugi anymore.
"""

import argparse
import glob
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path


# ---------- Holiday loading ----------

def load_holidays(holidays_dir: str) -> tuple[set, dict]:
    """Auto-glob hk-*.json under holidays_dir, return (set of date, name map)."""
    holiday_dates: set = set()
    holiday_names: dict = {}
    pattern = os.path.join(holidays_dir, "hk-*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        return holiday_dates, holiday_names
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            for h in data.get("holidays", []):
                dstr = h.get("date")
                if not dstr:
                    continue
                try:
                    d = date.fromisoformat(dstr)
                except ValueError:
                    continue
                holiday_dates.add(d)
                holiday_names[d] = h.get("name_en", "Public Holiday")
        except (OSError, json.JSONDecodeError):
            continue
    return holiday_dates, holiday_names


# ---------- Working day helpers ----------

WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def is_wd(d: date, holidays: set) -> bool:
    return d.weekday() < 5 and d not in holidays


def push_to_wd(d: date, holidays: set) -> date:
    while not is_wd(d, holidays):
        d += timedelta(days=1)
    return d


def add_wd(d: date, n: int, holidays: set) -> date:
    """Add n working days. add_wd(d, 0) returns d itself (no shift)."""
    if n == 0:
        return d
    step = 1 if n > 0 else -1
    remaining = abs(n)
    while remaining > 0:
        d += timedelta(days=step)
        if is_wd(d, holidays):
            remaining -= 1
    return d


def sub_wd(d: date, n: int, holidays: set) -> date:
    return add_wd(d, -n, holidays)


def wd_count(start: date, end: date, holidays: set) -> int:
    """Working days from start (exclusive) to end (inclusive). 0 if start >= end."""
    if end <= start:
        return 0
    n = 0
    cur = start
    while cur < end:
        cur += timedelta(days=1)
        if is_wd(cur, holidays):
            n += 1
    return n


def fmt(d: date) -> dict:
    return {"date": d.isoformat(), "weekday": WEEKDAY_NAMES[d.weekday()]}


# ---------- Milestone construction ----------

def m(order: int, name: str, d: date, color: str, party: str, calendar_title: str) -> dict:
    return {
        "order": order,
        "name": name,
        "date": d.isoformat(),
        "weekday": WEEKDAY_NAMES[d.weekday()],
        "colorId": color,
        "party": party,
        "calendar_title": calendar_title,
    }


# ---------- Backward tail (Step B) ----------

def backward_tail(final_output: date, has_vo: bool, holidays: set) -> dict:
    """Compute C/S, VO window, Picture Lock from Final Output."""
    cs = sub_wd(final_output, 1, holidays)
    if has_vo:
        vo_end = sub_wd(cs, 1, holidays)
        vo_start = sub_wd(vo_end, 1, holidays)  # length 2 wd: start + 1 wd = end
        picture_lock = sub_wd(vo_start, 1, holidays)
    else:
        vo_start = vo_end = None
        picture_lock = sub_wd(cs, 1, holidays)
    return {
        "cs": cs,
        "vo_start": vo_start,
        "vo_end": vo_end,
        "picture_lock": picture_lock,
    }


# ---------- Standard cut chain forward from Shoot ----------

def cut_chain_forward(start_anchor: date, cut_count: int, mode: str, holidays: set) -> list:
    """
    mode = "standard" | "compressed" | "extreme"
    standard: shoot→1stCut 5wd, FB 3wd MIN, cut→FB 3wd MIN
    compressed: shoot→1stCut 4wd, FB 1wd, cut→FB 1wd, FB→cut 3wd MIN (CompressionRules)
    Returns list of (label, date) pairs.
    """
    shoot_to_1st = {"standard": 5, "compressed": 4, "extreme": 2}[mode]
    fb_gap = {"standard": 3, "compressed": 1, "extreme": 1}[mode]
    cut_gap = {"standard": 3, "compressed": 3, "extreme": 2}[mode]

    chain: list = []
    d = add_wd(start_anchor, shoot_to_1st, holidays)
    chain.append(("1st Cut", d))
    if cut_count >= 1:
        d = add_wd(d, fb_gap, holidays)
        chain.append(("Client FB 1", d))
    if cut_count >= 2:
        d = add_wd(d, cut_gap, holidays)
        chain.append(("2nd Cut", d))
        d = add_wd(d, fb_gap, holidays)
        chain.append(("Client FB 2", d))
    if cut_count >= 3:
        d = add_wd(d, cut_gap, holidays)
        chain.append(("3rd Cut", d))
        d = add_wd(d, fb_gap, holidays)
        chain.append(("Client FB 3", d))
    return chain


# ---------- Slack distribution (Step E) ----------

def distribute_slack_v2(
    start_anchor: date, picture_lock: date, cut_count: int, mode: str, holidays: set
) -> tuple:
    """
    Build cut chain forward from start_anchor, target last FB ≤ picture_lock - 1 wd.

    Slack distribution priority: shoot_1st > cut2 > cut3 > fb1 > fb2 > fb3.
    Per-mode caps for each gap kind:
      standard:   shoot_1st 5+3=8, cut 3+5=8, fb 3+2=5
      compressed: shoot_1st 4+2=6, cut 3+3=6, fb 1+2=3
      extreme:    shoot_1st 2+3=5, cut 2+3=5, fb 1+2=3

    Danger flag: any cut whose incoming gap (shoot→1st, FB1→2nd, FB2→3rd) ≤ 3 wd.

    Returns (chain, cut_warnings, infeasible, deficit_wd) where:
      chain = list of (label, date) pairs
      cut_warnings = list of warning strings for cuts ≤ 3 wd
      infeasible = True if even MIN doesn't fit
      deficit_wd = wd by which MIN exceeds available (0 if feasible)
    """
    mins = {
        "standard":   {"shoot_1st": 5, "cut": 3, "fb": 3},
        "compressed": {"shoot_1st": 4, "cut": 3, "fb": 1},
        "extreme":    {"shoot_1st": 2, "cut": 2, "fb": 1},
    }[mode]
    cap_extra = {
        "standard":   {"shoot_1st": 3, "cut": 5, "fb": 2},
        "compressed": {"shoot_1st": 2, "cut": 3, "fb": 2},
        "extreme":    {"shoot_1st": 3, "cut": 3, "fb": 2},
    }[mode]

    target_last_fb = sub_wd(picture_lock, 1, holidays)
    available = wd_count(start_anchor, target_last_fb, holidays)
    min_span = (
        mins["shoot_1st"]
        + cut_count * mins["fb"]
        + max(0, cut_count - 1) * mins["cut"]
    )
    infeasible = available < min_span
    deficit = max(0, min_span - available)
    slack = max(0, available - min_span)

    # Slot priority order for slack fill
    priority: list = [("shoot_1st", "shoot_1st")]
    if cut_count >= 2:
        priority.append(("cut2", "cut"))
    if cut_count >= 3:
        priority.append(("cut3", "cut"))
    if cut_count >= 1:
        priority.append(("fb1", "fb"))
    if cut_count >= 2:
        priority.append(("fb2", "fb"))
    if cut_count >= 3:
        priority.append(("fb3", "fb"))

    extras = {name: 0 for name, _ in priority}
    for name, kind in priority:
        if slack <= 0:
            break
        take = min(slack, cap_extra[kind])
        extras[name] = take
        slack -= take

    # Build chain + record cut-incoming gaps
    chain: list = []
    cut_durations: list = []  # (label, gap_wd)

    sf_gap = mins["shoot_1st"] + extras["shoot_1st"]
    d = add_wd(start_anchor, sf_gap, holidays)
    chain.append(("1st Cut", d))
    cut_durations.append(("1st Cut", sf_gap))
    if cut_count >= 1:
        d = add_wd(d, mins["fb"] + extras.get("fb1", 0), holidays)
        chain.append(("Client FB 1", d))
    if cut_count >= 2:
        c2_gap = mins["cut"] + extras.get("cut2", 0)
        d = add_wd(d, c2_gap, holidays)
        chain.append(("2nd Cut", d))
        cut_durations.append(("2nd Cut", c2_gap))
        d = add_wd(d, mins["fb"] + extras.get("fb2", 0), holidays)
        chain.append(("Client FB 2", d))
    if cut_count >= 3:
        c3_gap = mins["cut"] + extras.get("cut3", 0)
        d = add_wd(d, c3_gap, holidays)
        chain.append(("3rd Cut", d))
        cut_durations.append(("3rd Cut", c3_gap))
        d = add_wd(d, mins["fb"] + extras.get("fb3", 0), holidays)
        chain.append(("Client FB 3", d))

    cut_warnings: list = []
    for label, gap_wd in cut_durations:
        if gap_wd <= 3:
            cut_warnings.append(
                f"⚠️ {label} 只有 {gap_wd} wd（≤ 3 wd 危險水平）— post team 容易頂唔順，"
                f"建議 director / producer review 條 cut 嘅 scope。"
            )

    return chain, cut_warnings, infeasible, deficit


# ---------- Pre-pro chain backward from Shoot ----------

def pre_pro_standard(shoot: date, has_style_frame: bool, holidays: set) -> dict:
    """Standard pre-pro chain backward from Shoot."""
    script_lock = sub_wd(shoot, 7, holidays)
    submit_video_flow = sub_wd(script_lock, 5, holidays)
    script_received = sub_wd(submit_video_flow, 5, holidays)
    out = {
        "script_received": script_received,
        "submit_video_flow": submit_video_flow,
        "submit_graphics_ref": submit_video_flow,
        "script_lock": script_lock,
        "confirm_graphics_ref": script_lock,
    }
    if has_style_frame:
        out["submit_style_frame"] = add_wd(script_lock, 2, holidays)
        out["confirm_style_frame"] = add_wd(out["submit_style_frame"], 1, holidays)
    return out


def pre_pro_compressed(effective_kickstart: date, has_style_frame: bool, holidays: set) -> dict:
    """
    Compressed-Edge-Case pre-pro chain forward from effective_kickstart.
    Sequential 2 wd default gap. Style Frame moved to parallel-with-1st-Cut.
    """
    sr = effective_kickstart
    svf = add_wd(sr, 2, holidays)
    sl = add_wd(svf, 2, holidays)
    out = {
        "script_received": sr,
        "submit_video_flow": svf,
        "submit_graphics_ref": svf,
        "script_lock": sl,
        "confirm_graphics_ref": sl,
    }
    # Style Frame parallel-with-1st-Cut handled later (inserted into post chain),
    # not in pre-pro here.
    return out


# ---------- Holiday/weekend cross check + push ----------

def push_milestones(milestones: list, holidays: set, warnings: list) -> list:
    """Push each non-shooting milestone forward to next weekday + non-holiday."""
    out = []
    for ms in milestones:
        d = date.fromisoformat(ms["date"])
        if ms["name"] == "Shooting":
            out.append(ms)
            continue
        if not is_wd(d, holidays):
            new_d = push_to_wd(d, holidays)
            warnings.append(
                f"⚠️ {ms['name']} {ms['date']} ({WEEKDAY_NAMES[d.weekday()]}) 撞 weekend / holiday → push 去 {new_d.isoformat()} ({WEEKDAY_NAMES[new_d.weekday()]})"
            )
            ms = dict(ms)
            ms["date"] = new_d.isoformat()
            ms["weekday"] = WEEKDAY_NAMES[new_d.weekday()]
        out.append(ms)
    return out


# ---------- Main flow ----------

def parse_args():
    p = argparse.ArgumentParser(description="Mugi backward timeline generator")
    p.add_argument("--today", help="ISO date override (default: system today)")
    p.add_argument("--final-output", help="Client deadline anchor (ISO)")
    p.add_argument("--shoot-mode", choices=["standard", "pure-post"], default="standard")
    p.add_argument("--shoot-date", help="Locked shoot date (ISO). Standard mode only.")
    p.add_argument("--first-cut-start", help="Pure-post 1st Cut start anchor (ISO).")
    p.add_argument("--has-vo", default="true", help="true|false (default true)")
    p.add_argument("--has-style-frame", default="true", help="true|false (default true)")
    p.add_argument("--senior-approval-fb2-wd", type=int, default=0,
                   help="If > 0, force 2-cut, FB2 = N wd")
    p.add_argument("--cut-count-override", type=int, default=0,
                   help="Explicit cut count override (2 or 3)")
    p.add_argument("--project", default="[Project]", help="Project label for calendar titles")
    p.add_argument("--shoot-days", type=int, default=1, help="Multi-day shoot count (default 1)")
    p.add_argument("--holidays-dir",
                   default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                        "context", "holidays"),
                   help="Folder containing hk-*.json (auto-glob)")
    # --- propose-shoot-mode flags ---
    p.add_argument("--propose-shoot-mode", action="store_true",
                   help="Propose N candidate Shoot Dates from kickstart, exit early.")
    p.add_argument("--kickstart", help="Kickstart date (ISO). Defaults to --today.")
    p.add_argument("--candidates", type=int, default=3,
                   help="Number of candidate shoot dates (default 3)")
    return p.parse_args()


def to_bool(s: str) -> bool:
    return str(s).strip().lower() in ("true", "1", "yes", "y")


def emit(payload: dict):
    print(json.dumps(payload, ensure_ascii=False))


def propose_shoot_dates(kickstart: date, final_output: date | None,
                        n_candidates: int, holidays: set, holiday_names: dict) -> dict:
    """
    Propose N candidate Shoot Dates from kickstart.

    Earliest = effective_kickstart + 5 wd (Script Lock minimum baseline).
    Subsequent candidates = +1 wd, +2 wd ... each is already a working day
    (add_wd skips weekend + holiday automatically).

    Output schema (1-line JSON):
      {
        "status": "shoot_proposal",
        "kickstart_input": "<iso>",
        "kickstart_effective": "<iso>",
        "candidates": [{"date","weekday","wd_from_kickstart","label"} ...],
        "warnings": [...],
        "holidays_in_window": [{"date","name"} ...]
      }
    """
    warnings: list = []
    effective_kickstart = push_to_wd(kickstart, holidays)
    if effective_kickstart != kickstart:
        warnings.append(
            f"⚠️ Kickstart {kickstart.isoformat()} ({WEEKDAY_NAMES[kickstart.weekday()]}) "
            f"撞 weekend / holiday → effective kickstart push 去 "
            f"{effective_kickstart.isoformat()} ({WEEKDAY_NAMES[effective_kickstart.weekday()]})。"
        )

    earliest = add_wd(effective_kickstart, 5, holidays)
    candidates = []
    for i in range(max(1, n_candidates)):
        cand = add_wd(earliest, i, holidays)
        wd_from_kick = wd_count(effective_kickstart, cand, holidays)
        if i == 0:
            label = "earliest_safe"
        else:
            label = f"+{i}_buffer"
        candidates.append({
            "date": cand.isoformat(),
            "weekday": WEEKDAY_NAMES[cand.weekday()],
            "wd_from_kickstart": wd_from_kick,
            "label": label,
        })

    # Holidays between kickstart and final (or +60 days if no final)
    window_end = final_output if final_output else (effective_kickstart + timedelta(days=60))
    holidays_in_window = []
    for hd in sorted(holidays):
        if effective_kickstart <= hd <= window_end:
            holidays_in_window.append({
                "date": hd.isoformat(),
                "weekday": WEEKDAY_NAMES[hd.weekday()],
                "name": holiday_names.get(hd, "Public Holiday"),
            })

    # Tight-final warnings (rough heuristic — we don't yet know cut_count / VO)
    if final_output:
        for c in candidates:
            cd = date.fromisoformat(c["date"])
            wd_to_final = wd_count(cd, final_output, holidays)
            # Compressed 3-cut min post window ≈ 11 wd shoot→final (incl tail).
            # Standard 3-cut min post window ≈ 20 wd. Flag both tiers.
            if wd_to_final < 7:
                warnings.append(
                    f"⚠️ Candidate {c['date']} → Final {final_output.isoformat()} "
                    f"= {wd_to_final} wd，連 Compressed-Edge-Case 都頂唔順 — 揀呢個會 trigger Extreme-Squeeze。"
                )
            elif wd_to_final < 11:
                warnings.append(
                    f"⚠️ Candidate {c['date']} → Final {final_output.isoformat()} "
                    f"= {wd_to_final} wd，post window 緊 — likely Compressed-Edge-Case。"
                )
            elif wd_to_final < 20:
                warnings.append(
                    f"ℹ️ Candidate {c['date']} → Final {final_output.isoformat()} "
                    f"= {wd_to_final} wd，行 compressed 3-cut（feedback 1 wd）— 標準 3-cut 需 ≥ 20 wd。"
                )

    warnings.append(
        "Script Lock window = 5 wd（kickstart → shoot 最低 baseline）— 如果客戶要 multi-revision script，建議延後 shoot。"
    )

    return {
        "status": "shoot_proposal",
        "kickstart_input": kickstart.isoformat(),
        "kickstart_effective": effective_kickstart.isoformat(),
        "kickstart_effective_weekday": WEEKDAY_NAMES[effective_kickstart.weekday()],
        "final_output": final_output.isoformat() if final_output else None,
        "candidates": candidates,
        "warnings": warnings,
        "holidays_in_window": holidays_in_window,
    }


def main():
    args = parse_args()

    try:
        today = date.fromisoformat(args.today) if args.today else date.today()
    except ValueError as e:
        emit({"status": "error", "error": f"Invalid --today: {e}"})
        return

    holidays_dir = os.path.normpath(args.holidays_dir)
    holidays, holiday_names = load_holidays(holidays_dir)

    # ----- propose-shoot-mode early branch -----
    if args.propose_shoot_mode:
        try:
            kickstart = date.fromisoformat(args.kickstart) if args.kickstart else today
            final_output_opt = date.fromisoformat(args.final_output) if args.final_output else None
        except ValueError as e:
            emit({"status": "error", "error": f"Invalid date: {e}"})
            return
        payload = propose_shoot_dates(
            kickstart, final_output_opt, args.candidates, holidays, holiday_names
        )
        if not holidays:
            payload["warnings"].insert(
                0,
                f"⚠️ Holiday set empty (looked in {holidays_dir}/hk-*.json). 請 double-check candidate 冇撞 public holiday。"
            )
        emit(payload)
        return

    if not args.final_output:
        emit({"status": "error", "error": "--final-output required (unless --propose-shoot-mode)"})
        return

    try:
        final_output = date.fromisoformat(args.final_output)
    except ValueError as e:
        emit({"status": "error", "error": f"Invalid date: {e}"})
        return

    warnings: list = []
    if not holidays:
        warnings.append(
            f"⚠️ Holiday set empty (looked in {holidays_dir}/hk-*.json). 請 double-check milestone 冇撞 public holiday。"
        )

    has_vo = to_bool(args.has_vo)
    has_style_frame = to_bool(args.has_style_frame)
    shoot_mode = args.shoot_mode

    # Step 0: effective kickstart
    effective_kickstart = push_to_wd(today, holidays)

    # Step B: backward tail
    tail = backward_tail(final_output, has_vo, holidays)

    # ----- pure-post branch -----
    if shoot_mode == "pure-post":
        if not args.first_cut_start:
            emit({"status": "error", "error": "pure-post mode requires --first-cut-start"})
            return
        try:
            fc_start = date.fromisoformat(args.first_cut_start)
        except ValueError:
            emit({"status": "error", "error": "Invalid --first-cut-start"})
            return
        return run_pure_post(args, effective_kickstart, today, final_output, fc_start,
                             tail, has_vo, holidays, warnings)

    # ----- standard shoot+post branch -----
    return run_standard(args, effective_kickstart, today, final_output, tail,
                        has_vo, has_style_frame, holidays, warnings)


def decide_cut_count(args, available_window: int) -> tuple[int, str, str | None, list]:
    """Return (cut_count, mode, scenario_label, extra_warnings)."""
    extra = []
    # Senior approval rule overrides everything
    if args.senior_approval_fb2_wd and args.senior_approval_fb2_wd > 0:
        return 2, "standard", "2-cut + senior approval FB2", extra
    # User override
    if args.cut_count_override in (2, 3):
        if args.cut_count_override == 3 and available_window < 14:
            extra.append("⚠️ User override 3-cut，但 available window < 14 wd，會行 compressed gaps")
            return 3, "compressed", "3-cut compressed (user override)", extra
        if args.cut_count_override == 2 and available_window < 10:
            extra.append("⚠️ 2-cut 都頂唔順 available window，會 escalate Pattern J")
        return args.cut_count_override, "standard" if available_window >= 14 else "compressed", \
               f"{args.cut_count_override}-cut (user override)", extra
    # Default decision matrix
    if available_window >= 20:
        return 3, "standard", "3-cut standard", extra
    if 14 <= available_window <= 19:
        extra.append(
            "⚠️ Available window 14–19 wd，預設行 compressed 3-cut（cut gap 3 wd, feedback 1 wd）。"
            "如要寬鬆 timeline 改 2-cut standard，請指示。"
        )
        return 3, "compressed", "3-cut compressed (14–19 wd default)", extra
    if 10 <= available_window <= 13:
        extra.append(
            "⚠️ Available window 10–13 wd，行 compressed 2-cut（Shoot→1st Cut 4 wd, FB 1 wd）。"
            "Feedback time 收緊，要同 client 講明。"
        )
        return 2, "compressed", "2-cut compressed (10–13 wd)", extra
    # < 10 wd
    return 0, "infeasible", None, extra


def run_standard(args, effective_kickstart, today, final_output, tail,
                 has_vo, has_style_frame, holidays, warnings):
    """Standard shoot+post branch."""
    project = args.project
    shoot_days = max(args.shoot_days, 1)

    # Determine shoot_date
    if args.shoot_date:
        try:
            shoot_date = date.fromisoformat(args.shoot_date)
        except ValueError:
            emit({"status": "error", "error": "Invalid --shoot-date"})
            return
    else:
        # Backward-derive: latest shoot allowing 3-cut MIN to fit picture_lock
        # min span shoot → picture_lock for 3-cut MIN = 5+3+3+3+3+3+1 = 21 wd
        # Use 20 wd to align with §1 Step D table (≥20 wd = 3-cut)
        shoot_date = sub_wd(tail["picture_lock"], 20, holidays)
        if shoot_date < add_wd(effective_kickstart, 18, holidays):
            # Pre-pro chain won't fit → use ASAP shoot for compressed branch detection
            shoot_date = add_wd(effective_kickstart, 18, holidays)

    # available_window = picture_lock - shoot
    available_window = wd_count(shoot_date, tail["picture_lock"], holidays)

    cut_count, cut_mode, scenario_label, extra_w = decide_cut_count(args, available_window)
    warnings.extend(extra_w)

    if cut_count == 0:
        # < 10 wd → Pattern J
        emit({
            "status": "infeasible_pattern_j",
            "effective_kickstart": effective_kickstart.isoformat(),
            "final_output": final_output.isoformat(),
            "shoot_date": shoot_date.isoformat(),
            "available_wd": available_window,
            "scenario_label": "Pattern J - escalate Sohling",
            "warnings": warnings + [
                f"⚠️ Shoot ({shoot_date.isoformat()}) → Picture Lock ({tail['picture_lock'].isoformat()}) "
                f"= {available_window} wd，連 2-cut compressed 都頂唔順 (MIN 10 wd)。"
                f"Escalate Sohling for manual judgment."
            ],
            "cut_warnings": [],
            "milestones": [],
        })
        return

    # Build cut chain
    cut_chain, cut_warnings, _infeasible, _deficit = distribute_slack_v2(
        shoot_date, tail["picture_lock"], cut_count, cut_mode, holidays
    )

    # Pre-pro chain backward from shoot
    pre_pro = pre_pro_standard(shoot_date, has_style_frame, holidays)

    # Step F: Past-milestone detection
    earliest = min([
        pre_pro["script_received"],
        pre_pro["submit_video_flow"],
        pre_pro["script_lock"],
    ] + ([pre_pro["submit_style_frame"]] if has_style_frame else []))

    if earliest < effective_kickstart:
        # Trigger Compressed-Edge-Case Branch.
        # Drop standard-branch cut-count warnings — they're based on a shoot date
        # we are about to discard, so they don't describe the actual scenario.
        warnings = [
            w for w in warnings
            if "14–19 wd，預設行 compressed 3-cut" not in w
            and "10–13 wd，行 compressed 2-cut" not in w
        ]
        return run_compressed_edge_case(
            args, effective_kickstart, today, final_output, tail,
            has_vo, has_style_frame, holidays, warnings,
            standard_pre_pro_earliest=earliest
        )

    # Build milestones list (standard path)
    return build_output(
        status="standard",
        scenario_label=scenario_label,
        effective_kickstart=effective_kickstart,
        final_output=final_output,
        shoot_date=shoot_date,
        shoot_days=shoot_days,
        available_window=available_window,
        cut_count=cut_count,
        pre_pro=pre_pro,
        cut_chain=cut_chain,
        tail=tail,
        has_vo=has_vo,
        has_style_frame=has_style_frame,
        compressed_style_frame_in_post=False,
        project=args.project,
        holidays=holidays,
        warnings=warnings,
        cut_warnings=cut_warnings,
    )


def run_compressed_edge_case(args, effective_kickstart, today, final_output, tail,
                             has_vo, has_style_frame, holidays, warnings,
                             standard_pre_pro_earliest=None):
    """Compressed-Edge-Case Branch: Shoot ASAP, sequential 1-2 wd pre-pro, default 3-cut compressed."""
    project = args.project
    shoot_days = max(args.shoot_days, 1)

    warnings.append(
        f"⚠️ Timeline INFEASIBLE under standard logic — standard pre-pro chain 推到 "
        f"{standard_pre_pro_earliest.isoformat() if standard_pre_pro_earliest else '?'} "
        f"(早過 effective kickstart {effective_kickstart.isoformat()})。"
        f"切換至 Compressed-Edge-Case Branch。"
    )

    # Pre-pro forward from kickstart
    pre_pro = pre_pro_compressed(effective_kickstart, has_style_frame, holidays)
    # Shoot = Script Lock + 1 wd (per playbook Compressed-Edge-Case example)
    shoot_date = add_wd(pre_pro["script_lock"], 1, holidays)

    # available_window for cut count decision in compressed mode
    available_window = wd_count(shoot_date, tail["picture_lock"], holidays)

    # Default 3-cut compressed (squeeze gap, not drop cut count) per playbook
    if args.senior_approval_fb2_wd and args.senior_approval_fb2_wd > 0:
        cut_count = 2
        scenario_label = "Compressed-Edge-Case 2-cut + senior approval FB2"
    elif args.cut_count_override == 2:
        cut_count = 2
        scenario_label = "Compressed-Edge-Case 2-cut (user override)"
    else:
        cut_count = 3
        scenario_label = "Compressed-Edge-Case 3-cut (default)"

    # Build cut chain — extreme mode floor (compressed branch always uses extreme MIN
    # for cut/fb gaps, then distribute available slack with priority).
    cut_chain, cut_warnings, infeasible, deficit = distribute_slack_v2(
        shoot_date, tail["picture_lock"], cut_count, "extreme", holidays
    )

    if infeasible:
        # Even Compressed-Edge-Case extreme MIN config can't fit → Extreme-Squeeze Tier
        return emit_extreme_squeeze(
            args, effective_kickstart, final_output, shoot_date, tail,
            available_window, deficit, holidays, warnings
        )

    # Build output (compressed)
    return build_output(
        status="compressed_edge_case",
        scenario_label=scenario_label,
        effective_kickstart=effective_kickstart,
        final_output=final_output,
        shoot_date=shoot_date,
        shoot_days=shoot_days,
        available_window=available_window,
        cut_count=cut_count,
        pre_pro=pre_pro,
        cut_chain=cut_chain,
        tail=tail,
        has_vo=has_vo,
        has_style_frame=has_style_frame,
        compressed_style_frame_in_post=has_style_frame,
        project=project,
        holidays=holidays,
        warnings=warnings,
        cut_warnings=cut_warnings,
    )


def run_pure_post(args, effective_kickstart, today, final_output, fc_start,
                  tail, has_vo, holidays, warnings):
    """Pure-post branch: skip pre-pro + shoot, anchor on 1st Cut start."""
    available_window = wd_count(fc_start, tail["picture_lock"], holidays)
    cut_count, cut_mode, scenario_label, extra_w = decide_cut_count(args, available_window)
    warnings.extend(extra_w)

    if cut_count == 0:
        emit({
            "status": "infeasible_pattern_j",
            "effective_kickstart": effective_kickstart.isoformat(),
            "final_output": final_output.isoformat(),
            "available_wd": available_window,
            "scenario_label": "Pattern J - pure post infeasible",
            "warnings": warnings + [
                f"⚠️ Pure-post 1st Cut start ({fc_start.isoformat()}) → Picture Lock "
                f"({tail['picture_lock'].isoformat()}) = {available_window} wd，"
                f"連 2-cut compressed 都頂唔順。Escalate Sohling。"
            ],
            "cut_warnings": [],
            "milestones": [],
        })
        return

    cut_chain, cut_warnings, _infeasible, _deficit = distribute_slack_v2(
        fc_start, tail["picture_lock"], cut_count, cut_mode, holidays
    )

    return build_output(
        status="pure_post" if cut_mode == "standard" else "pure_post_compressed",
        scenario_label=f"Pure-post {scenario_label}",
        effective_kickstart=effective_kickstart,
        final_output=final_output,
        shoot_date=None,
        shoot_days=0,
        available_window=available_window,
        cut_count=cut_count,
        pre_pro=None,
        cut_chain=cut_chain,
        tail=tail,
        has_vo=has_vo,
        has_style_frame=False,
        compressed_style_frame_in_post=False,
        project=args.project,
        holidays=holidays,
        warnings=warnings,
        first_cut_start=fc_start,
        cut_warnings=cut_warnings,
    )


def emit_extreme_squeeze(args, effective_kickstart, final_output, shoot_date, tail,
                         available_window, deficit_wd, holidays, warnings):
    """Extreme-Squeeze Tier: Mugi can't auto-plan, surface 3 propositions to director."""
    propositions = [
        {
            "id": 1,
            "name": "壓縮 client feedback 時間",
            "detail": "Pre-arrange senior viewing day（同 client 約定下晝某時間做 senior review），feedback turnaround 由標準 1–3 wd 壓到 same-day / next morning",
        },
        {
            "id": 2,
            "name": "同 client 傾轉數",
            "detail": "真係要 3 rounds？2 rounds 得唔得？或者其他 hybrid 做法（e.g. 1st cut + senior approval combined）",
        },
        {
            "id": 3,
            "name": "壓縮 1st cut 時間",
            "detail": "由標準 2–3 wd → 1 day。視乎 director availability + post team bandwidth + 條片複雜度",
        },
    ]
    emit({
        "status": "extreme_squeeze",
        "effective_kickstart": effective_kickstart.isoformat(),
        "final_output": final_output.isoformat(),
        "shoot_date": shoot_date.isoformat() if shoot_date else None,
        "available_wd": available_window,
        "deficit_wd": deficit_wd,
        "scenario_label": "Extreme-Squeeze Tier — director call needed",
        "extreme_squeeze_propositions": propositions,
        "warnings": warnings + [
            f"⚠️ Extreme tier — standard + Compressed-Edge-Case 都頂唔順。"
            f"Compressed branch min 仲要超 {deficit_wd} wd。"
            f"呢個 case 變數太多，Mugi judge 唔到，建議交俾導演 call。"
            f"@director 入嚟睇下：揀邊個方向？"
        ],
        "cut_warnings": [],
        "milestones": [],
    })


def build_output(*, status, scenario_label, effective_kickstart, final_output,
                 shoot_date, shoot_days, available_window, cut_count,
                 pre_pro, cut_chain, tail, has_vo, has_style_frame,
                 compressed_style_frame_in_post, project, holidays, warnings,
                 first_cut_start=None, cut_warnings=None):
    """Assemble final milestones list and emit JSON."""
    milestones: list = []
    order = 1

    # Pre-pro chain (skip for pure-post)
    if pre_pro:
        milestones.append(m(order, "Script Received", pre_pro["script_received"], "5", "Client",
                            f"Script Received - {project}"))
        order += 1
        milestones.append(m(order, "Submit Video Flow", pre_pro["submit_video_flow"], "5", "DOF",
                            f"Submit Video Flow - {project}"))
        order += 1
        milestones.append(m(order, "Submit Graphics Ref", pre_pro["submit_graphics_ref"], "5", "DOF",
                            f"Submit Graphics Ref - {project}"))
        order += 1
        milestones.append(m(order, "Script Lock", pre_pro["script_lock"], "2", "Client",
                            f"Script Lock - {project}"))
        order += 1
        milestones.append(m(order, "Confirm Graphics Ref", pre_pro["confirm_graphics_ref"], "2",
                            "Client", f"Confirm Graphics Ref - {project}"))
        order += 1
        if has_style_frame and not compressed_style_frame_in_post:
            milestones.append(m(order, "Submit Style Frame", pre_pro["submit_style_frame"], "9",
                                "DOF", f"Submit Style Frame - {project}"))
            order += 1
            milestones.append(m(order, "Confirm Style Frame", pre_pro["confirm_style_frame"], "2",
                                "Client", f"Confirm Style Frame - {project}"))
            order += 1

    # Shooting
    if shoot_date:
        title = f"({shoot_days} Day{'s' if shoot_days > 1 else ''}) Shooting - {project}"
        ms = m(order, "Shooting", shoot_date, "11", "Both", title)
        if shoot_days > 1:
            ms["shoot_days"] = shoot_days
        milestones.append(ms)
        order += 1

    # Cut chain
    cut_chain_dict = {label: d for label, d in cut_chain}
    for label, d in cut_chain:
        is_dof_cut = label.endswith("Cut")
        color = "7" if is_dof_cut else "2"
        party = "DOF" if is_dof_cut else "Client"
        title = f"{label} - {project}"
        milestones.append(m(order, label, d, color, party, title))
        order += 1

    # Compressed-Edge-Case: Style Frame parallel with 1st Cut + FB1
    if compressed_style_frame_in_post and "1st Cut" in cut_chain_dict:
        fb1_date = cut_chain_dict.get("Client FB 1", cut_chain_dict["1st Cut"])
        milestones.append(m(order, "Submit Style Frame", cut_chain_dict["1st Cut"], "9", "DOF",
                            f"Submit Style Frame - {project}"))
        order += 1
        milestones.append(m(order, "Confirm Style Frame", fb1_date, "2", "Client",
                            f"Confirm Style Frame - {project}"))
        order += 1

    # Picture Lock
    milestones.append(m(order, "Picture Lock", tail["picture_lock"], "7", "Both",
                        f"Picture Lock - {project}"))
    order += 1

    # VO Recording window
    vo_window = None
    if has_vo and tail["vo_start"]:
        vo_window = {
            "start": tail["vo_start"].isoformat(),
            "end": tail["vo_end"].isoformat(),
            "weekday_start": WEEKDAY_NAMES[tail["vo_start"].weekday()],
            "weekday_end": WEEKDAY_NAMES[tail["vo_end"].weekday()],
            "days": 2,
            "calendar_title": f"(2 Days) VO Recording - {project}",
            "colorId": "1",
        }
        # VO weekend cross check
        d = tail["vo_start"]
        while d <= tail["vo_end"]:
            if not is_wd(d, holidays):
                warnings.append(
                    f"⚠️ VO window {tail['vo_start'].isoformat()}–{tail['vo_end'].isoformat()} "
                    f"撞 {d.isoformat()} ({WEEKDAY_NAMES[d.weekday()]}) — 唔係 working day。"
                    f"@director 留意：VO recording 通常需要 talent + studio booking，撞假期要 reshuffle。"
                )
                break
            d += timedelta(days=1)

    # Color/Sound/Subtitle
    milestones.append(m(order, "Color/Sound/Subtitle", tail["cs"], "7", "DOF",
                        f"Color/Sound/Subtitle - {project}"))
    order += 1

    # Final Output
    milestones.append(m(order, "Final Output", final_output, "3", "DOF",
                        f"Final Output - {project}"))
    order += 1

    # Apply weekend/holiday push to all non-shooting milestones
    milestones = push_milestones(milestones, holidays, warnings)

    # Sort chronologically (stable: ties keep insertion order)
    milestones.sort(key=lambda x: x["date"])
    for i, ms in enumerate(milestones, start=1):
        ms["order"] = i

    payload = {
        "status": status,
        "scenario_label": scenario_label,
        "effective_kickstart": effective_kickstart.isoformat(),
        "final_output": final_output.isoformat(),
        "shoot_date": shoot_date.isoformat() if shoot_date else None,
        "shoot_days": shoot_days if shoot_date else 0,
        "first_cut_start": first_cut_start.isoformat() if first_cut_start else None,
        "available_wd": available_window,
        "cut_count": cut_count,
        "milestones": milestones,
        "vo_window": vo_window,
        "has_style_frame": has_style_frame,
        "warnings": warnings,
        "cut_warnings": cut_warnings or [],
        "extreme_squeeze_propositions": None,
    }
    emit(payload)


if __name__ == "__main__":
    main()
