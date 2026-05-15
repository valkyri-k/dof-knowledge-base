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


# ---------- Timeline value dicts (spec §4) ----------
#
# All gap values in HK working days. Tuple = (min, default, max).
# Used by compress_to_min() — default-first compression algorithm (spec §3).
# Migration note: standard mode (min, default, max) defaults intentionally
# shorter than the pre-spec distribute_slack_v2 max-fill behavior. Resulting
# timelines pack tighter at default. See spec/pure-post-mode-spec.md §13
# Open Item #1 (resolved 2026-05-10).

TIMELINE_VALUES = {
    "standard": {
        # Pre-pro chain (shoot-anchored, backward)
        "script_received_to_video_flow":   (3, 5, 7),
        "video_flow_to_script_lock":       (3, 5, 7),
        "script_lock_to_shoot":            (3, 5, 10),
        "script_lock_to_submit_sf":        (1, 2, 3),
        "submit_sf_to_confirm_sf":         (1, 2, 3),
        # Cut chain
        "shoot_to_first_cut":              (2, 4, 6),
        "cut_production":                  (2, 3, 6),
        "cut_fb":                          (1, 2, 3),
    },
    "animation": {
        "script_to_treatment":             (1, 2, 3),
        "treatment_to_stb_sf":             (3, 5, 7),   # Treatment Meeting → STB+SF Submit
        "stb_sf_fb":                       (1, 2, 3),   # STB+SF Submit → STB+SF Confirm
        "stb_sf_to_animatic":              (2, 3, 4),   # STB+SF Confirm → Animatic Submit
        "animatic_fb":                     (1, 2, 3),   # Animatic Submit → Animatic Confirm
        "animatic_to_first_cut":           (4, 5, 7),
        "first_cut_fb":                    (1, 2, 3),
        "second_cut":                      (3, 4, 5),
        "second_cut_fb":                   (1, 2, 3),
        "third_cut":                       (2, 3, 4),
        "third_cut_fb":                    (1, 2, 3),
    },
    "mixed": {
        "storyboard_production":           (2, 3, 5),
        "storyboard_fb":                   (1, 2, 3),
        "storyboard_revision":             (1, 2, 3),
        "materials_to_rough_cut":          (2, 3, 4),
        "rough_cut_fb":                    (1, 2, 3),
        "rough_to_first_cut":              (3, 4, 6),
        "first_cut_fb":                    (1, 2, 3),
        "second_cut":                      (2, 3, 3),
        "second_cut_fb":                   (1, 2, 3),
        "third_cut":                       (1, 2, 3),
        "third_cut_fb":                    (1, 2, 3),
    },
    "edit": {
        "storyboard_production":           (2, 3, 5),
        "storyboard_fb":                   (1, 2, 3),
        "storyboard_revision":             (1, 2, 3),
        "materials_to_first_cut":          (2, 3, 5),
        "first_cut_fb":                    (1, 2, 3),
        "second_cut":                      (2, 3, 4),
        "second_cut_fb":                   (1, 2, 3),
        "third_cut":                       (2, 2, 3),
        "third_cut_fb":                    (1, 2, 3),
    },
}

# Backward tail (Picture Lock → VO → Color/Sound → Final). Mode-agnostic.
TAIL_VALUES = {
    "picture_lock_to_vo_start":            (1, 1, 2),
    "vo_window":                           (1, 2, 3),
    "vo_end_to_color_sound":               (1, 1, 2),
    "color_sound_to_final":                (1, 1, 2),
}

# Materials gathering estimate for pure-post storyboard sub-chain (spec §7.2).
# TODO: surface as CLI override if pattern emerges from real production use.
MATERIALS_GATHERING_ESTIMATE_WD = 5


# ---------- User anchor alias mapping (bug: user-supplied-dates-not-anchored) ----------
#
# User-facing alias → list of possible milestone `name` field values to overwrite.
# Standard mode uses title-case `name` ("1st Cut", "Picture Lock"); pure-post mode
# uses snake_case (`first_cut_submit`, `picture_lock`). For each alias we try each
# target in order until one matches a milestone in the assembled list.
#
# Principle: user-supplied dates are LOCKED ANCHORS, not candidates. Apply after
# default chain + push_milestones + sort; do NOT recompute surrounding milestones
# in v1 (surrounding stay at script default — Mugi explains at prompt layer).

ALIAS_TO_TARGETS = {
    "script_received":      ["Script Received"],
    "submit_video_flow":    ["Submit Video Flow"],
    "submit_graphics_ref":  ["Submit Graphics Ref"],
    "script_lock":          ["Script Lock"],
    "confirm_graphics_ref": ["Confirm Graphics Ref"],
    "submit_style_frame":   ["Submit Style Frame"],
    "confirm_style_frame":  ["Confirm Style Frame"],
    "shoot_date":           ["Shooting"],
    "storyboard_submit":    ["storyboard_submit"],
    "storyboard_confirm":   ["storyboard_confirm"],
    "treatment_meeting":    ["treatment_meeting"],
    "stb_sf_submit":        ["stb_sf_submit"],
    "stb_sf_confirm":       ["stb_sf_confirm"],
    "animatic_submit":      ["animatic_submit"],
    "animatic_confirm":     ["animatic_confirm"],
    "materials_ready":      ["materials_ready"],
    "rough_cut_submit":     ["rough_cut_submit"],
    "rough_cut_fb_due":     ["rough_cut_fb_due"],
    "first_cut_submit":     ["first_cut_submit", "1st Cut"],
    "first_cut_fb_due":     ["first_cut_fb_due", "Client FB 1"],
    "second_cut_submit":    ["second_cut_submit", "2nd Cut"],
    "second_cut_fb_due":    ["second_cut_fb_due", "Client FB 2"],
    "third_cut_submit":     ["third_cut_submit", "3rd Cut"],
    "third_cut_fb_due":     ["third_cut_fb_due", "Client FB 3"],
    "picture_lock":         ["picture_lock", "Picture Lock"],
    "vo_start":             ["vo_start"],
    "vo_end":               ["vo_end"],
    "color_sound":          ["color_sound", "Color/Sound/Subtitle"],
    "final_output":         ["Final Output"],
}


def parse_user_anchors(arg_list: list) -> tuple[dict, list]:
    """Parse repeatable --anchor name=YYYY-MM-DD args.

    Returns (anchors_dict, warnings). anchors_dict = {alias: date_obj}.
    Unknown alias / invalid date → warning, skip that entry.
    """
    anchors: dict = {}
    warnings: list = []
    for raw in arg_list or []:
        if "=" not in raw:
            warnings.append(f"⚠️ --anchor 格式錯誤（缺 `=`）：{raw}。Skip 咗。")
            continue
        name, _, datestr = raw.partition("=")
        name = name.strip()
        datestr = datestr.strip()
        if name not in ALIAS_TO_TARGETS:
            valid = ", ".join(sorted(ALIAS_TO_TARGETS.keys()))
            warnings.append(
                f"⚠️ --anchor `{name}` 唔識：可用 alias 包括 {valid}。Skip 咗。"
            )
            continue
        try:
            d = date.fromisoformat(datestr)
        except ValueError:
            warnings.append(f"⚠️ --anchor `{name}={datestr}` 唔係 valid ISO date。Skip 咗。")
            continue
        anchors[name] = d
    return anchors, warnings


def apply_anchors(milestones: list, anchors: dict, holidays: set) -> tuple[list, list, list]:
    """Overlay user-supplied anchor dates onto already-assembled milestone list.

    For each anchor:
      - Find first milestone whose `name` matches one of ALIAS_TO_TARGETS[alias].
      - Record original_default (the script-computed date about to be overwritten).
      - Overwrite milestone["date"] + milestone["weekday"] with anchor date.
      - Warn if anchor falls on non-wd (user knows, but surface it).

    After all anchors applied, scan consecutive milestones (by new date) and warn
    if any pair has 0 wd gap (date order swap or same-day where shouldn't be) —
    this is the feasibility signal for prompt-layer to surface.

    Returns (anchor_results, anchor_warnings, infeasibility_warnings). Caller is
    responsible for re-sorting milestones after the overlay.
    """
    anchor_results: list = []
    anchor_warnings: list = []
    name_to_idx = {m_dict.get("name"): i for i, m_dict in enumerate(milestones)}
    for alias, anchor_date in anchors.items():
        target_idx = None
        matched_name = None
        for target in ALIAS_TO_TARGETS[alias]:
            if target in name_to_idx:
                target_idx = name_to_idx[target]
                matched_name = target
                break
        if target_idx is None:
            anchor_warnings.append(
                f"⚠️ --anchor `{alias}` 喺今次 timeline 搵唔到對應 milestone "
                f"(tried {ALIAS_TO_TARGETS[alias]})。Skip 咗。"
            )
            anchor_results.append({
                "alias": alias,
                "requested_date": anchor_date.isoformat(),
                "applied_date": None,
                "original_default": None,
                "matched_milestone": None,
                "status": "milestone_not_found",
            })
            continue
        ms = milestones[target_idx]
        original_default = ms["date"]
        ms["date"] = anchor_date.isoformat()
        ms["weekday"] = WEEKDAY_NAMES[anchor_date.weekday()]
        ms["user_anchor"] = True
        status = "applied"
        if not is_wd(anchor_date, holidays):
            anchor_warnings.append(
                f"⚠️ --anchor `{alias}={anchor_date.isoformat()}` "
                f"({WEEKDAY_NAMES[anchor_date.weekday()]}) 唔係 working day。"
                f"User 講就跟，但留意可能撞 weekend / public holiday。"
            )
            status = "applied_non_wd"
        anchor_results.append({
            "alias": alias,
            "requested_date": anchor_date.isoformat(),
            "applied_date": anchor_date.isoformat(),
            "original_default": original_default,
            "matched_milestone": matched_name,
            "status": status,
        })
    # Feasibility scan: iterate by business sequence (order field). Caller may
    # re-sort by date after this call, so we MUST scan before that — `order` here
    # still reflects business sequence, not chronological.
    infeasibility_warnings: list = []
    if anchor_results:
        sorted_by_order = sorted(milestones, key=lambda x: x.get("order", 0))
        for i in range(1, len(sorted_by_order)):
            prev = sorted_by_order[i - 1]
            cur = sorted_by_order[i]
            if cur.get("user_anchor") or prev.get("user_anchor"):
                if cur["date"] < prev["date"]:
                    infeasibility_warnings.append(
                        f"⚠️ Anchor 令 chain 出現倒序：business sequence {prev['name']} → "
                        f"{cur['name']}，但 dates {prev['date']} > {cur['date']}。"
                        f"User 嘅 anchor 同其他 default milestone 衝突，"
                        f"surrounding milestones 仍係 script default 計，"
                        f"可能要 user reconfirm 或者放鬆其中一邊。"
                    )
                elif cur["date"] == prev["date"] and cur.get("user_anchor") != prev.get("user_anchor"):
                    infeasibility_warnings.append(
                        f"⚠️ Anchor 令 chain 出現 0 wd gap：business sequence {prev['name']} → "
                        f"{cur['name']} 落到同日 ({cur['date']})。"
                        f"Min gap 可能未滿足，留意 production feasibility。"
                    )
    return anchor_results, anchor_warnings + infeasibility_warnings, infeasibility_warnings


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


def mm(order: int, name: str, label: str, d: date, *,
       calendar_emit: bool = True, client_facing: bool = False,
       internal_only: bool = False, party: str = "DOF",
       color: str = "5", project: str = "[Project]") -> dict:
    """
    Build pure-post-mode milestone dict (spec §8.2). Adds calendar_emit /
    client_facing / internal_only fields on top of the base m() schema.
    """
    return {
        "order": order,
        "name": name,
        "label": label,
        "date": d.isoformat(),
        "weekday": WEEKDAY_NAMES[d.weekday()],
        "colorId": color,
        "party": party,
        "calendar_title": f"{label} - {project}",
        "calendar_emit": calendar_emit,
        "client_facing": client_facing,
        "internal_only": internal_only,
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


# ---------- Default-first compression (spec §3.2) ----------

# Compression priority categories (Step 1 → Step 2 → Step 3).
# Lower index = compressed first when window insufficient.
COMPRESSION_PRIORITY = ("cut_fb", "cut_production", "pre_pro")


def compress_to_min(chain_spec: list, available_window: int) -> dict:
    """
    Default-first compression: start with defaults; if total > available_window,
    compress entire categories to min in priority order until fits or all-min.

    chain_spec: list of dicts, each with keys:
        - name: str (gap identifier, used in returned `gaps` dict)
        - category: str ∈ COMPRESSION_PRIORITY
        - min: int (wd floor)
        - default: int (wd baseline)
        - max: int (wd ceiling — currently unused; reserved for complexity-driven
          expansion, see backlog/ideas/complexity-driven-selective-expansion.md)
    available_window: int (wd between chain start and end anchors)

    Returns dict:
        - gaps: {name: resolved_wd}
        - total_wd: int (sum of resolved gap values)
        - compressions_applied: list[str] (categories pushed to min, in order)
        - infeasible: bool (True if even all-min total > available_window)
        - deficit_wd: int (only > 0 when infeasible — caller should trigger
          Pattern J extreme squeeze)

    Note: when total < available_window after resolution, the caller is
    responsible for placing excess as front buffer before the earliest milestone
    — compress_to_min does NOT distribute excess into gaps (per spec §3 default-
    first philosophy).
    """
    if not chain_spec:
        return {
            "gaps": {},
            "total_wd": 0,
            "compressions_applied": [],
            "infeasible": False,
            "deficit_wd": 0,
        }

    gaps = {g["name"]: g["default"] for g in chain_spec}
    total = sum(gaps.values())

    if total <= available_window:
        return {
            "gaps": gaps,
            "total_wd": total,
            "compressions_applied": [],
            "infeasible": False,
            "deficit_wd": 0,
        }

    compressions_applied: list = []
    for category in COMPRESSION_PRIORITY:
        category_has_gap = False
        for g in chain_spec:
            if g["category"] == category:
                gaps[g["name"]] = g["min"]
                category_has_gap = True
        if category_has_gap:
            compressions_applied.append(category)
        total = sum(gaps.values())
        if total <= available_window:
            return {
                "gaps": gaps,
                "total_wd": total,
                "compressions_applied": compressions_applied,
                "infeasible": False,
                "deficit_wd": 0,
            }

    # All-min exceeds window — caller triggers Pattern J extreme squeeze.
    return {
        "gaps": gaps,
        "total_wd": total,
        "compressions_applied": compressions_applied,
        "infeasible": True,
        "deficit_wd": total - available_window,
    }


# ---------- Storyboard sub-chain (spec §7) ----------

def build_storyboard_chain(
    materials_ready_anchor: date,
    available_window: int,
    mode: str,
    holidays: set,
    forced_chain_mode: str = None,
) -> dict:
    """
    Build storyboard sub-chain for mixed/edit modes with --storyboard=we-make.

    Backward layout from materials_ready_anchor:

      Sequential (default when window allows):
        production_start ← [sp] ← submit ← [sfb] ← fb_end ← [sr] ← confirm
                                                                    ↓ [mg]
                                                            materials_ready
        Total wd from production_start to materials_ready = sp+sfb+sr+mg

      Parallel (auto-fallback when window < seq_window_needed):
        production_start ← [sp] ← submit ← [sfb] ← fb_end ← [sr] ← confirm
        gathering_start ←─────────────[mg]─────────────────────→ materials_ready
        materials_ready = max(confirm, gathering_start + mg) — modeled as confirm
        coinciding with materials_ready (storyboard chain typically longer than mg).

    Args:
        materials_ready_anchor: target date materials must be ready (anchor for
            backward walk).
        available_window: wd from kickstart (script_received) to
            materials_ready_anchor — used for sequential/parallel auto-decision.
        mode: "mixed" | "edit" — selects TIMELINE_VALUES gap defaults.
        holidays: HK holiday set.
        forced_chain_mode: "sequential" | "parallel" | None. If set, skip the
            auto-check and honor user intent (--storyboard-mode override).

    Returns dict:
        - chain_mode: "sequential" | "parallel"
        - fallback_triggered: bool (True only when auto-check chose parallel)
        - storyboard_submit: date
        - storyboard_fb_end: date    (FB window closes — revision starts here)
        - storyboard_confirm: date   (client milestone — calendar_emit, client_facing)
        - materials_ready: date      (= anchor)
        - gaps: dict with sp/sfb/sr/mg defaults used
        - seq_window_needed: int     (informational; for warnings)
    """
    if mode not in ("mixed", "edit"):
        raise ValueError(f"build_storyboard_chain: mode must be 'mixed' or 'edit', got {mode!r}")

    vals = TIMELINE_VALUES[mode]
    sp = vals["storyboard_production"][1]
    sfb = vals["storyboard_fb"][1]
    sr = vals["storyboard_revision"][1]
    mg = MATERIALS_GATHERING_ESTIMATE_WD

    seq_window_needed = sp + sfb + sr + mg

    if forced_chain_mode in ("sequential", "parallel"):
        chain_mode = forced_chain_mode
        fallback_triggered = False
    elif available_window >= seq_window_needed:
        chain_mode = "sequential"
        fallback_triggered = False
    else:
        chain_mode = "parallel"
        fallback_triggered = True

    materials_ready = materials_ready_anchor

    if chain_mode == "sequential":
        # Confirm precedes materials_ready by mg wd.
        storyboard_confirm = sub_wd(materials_ready, mg, holidays)
    else:
        # Parallel: confirm coincides with materials_ready (gathering runs concurrent).
        storyboard_confirm = materials_ready

    fb_end = sub_wd(storyboard_confirm, sr, holidays)
    storyboard_submit = sub_wd(fb_end, sfb, holidays)

    return {
        "chain_mode": chain_mode,
        "fallback_triggered": fallback_triggered,
        "storyboard_submit": storyboard_submit,
        "storyboard_fb_end": fb_end,
        "storyboard_confirm": storyboard_confirm,
        "materials_ready": materials_ready,
        "gaps": {
            "storyboard_production": sp,
            "storyboard_fb": sfb,
            "storyboard_revision": sr,
            "materials_gathering": mg,
        },
        "seq_window_needed": seq_window_needed,
    }


# ---------- Pure-post mode chain spec builders (spec §6) ----------
# Each builder returns a chain_spec list (consumed by compress_to_min). The
# returned list is ordered from EARLIEST gap → LATEST gap. Walking dates
# backward from the end-anchor is the dispatcher's job.
#
# Per spec §6 + Q3 resolution: pre_pro_* build PRE-PRO SEGMENT ONLY.
#   - animation: ends at Animatic Confirm
#   - mixed: ends at 1st Cut Submit
#   - edit:  ends at 1st Cut Submit
# Cut chain (animatic→1st_cut→…→picture_lock for animation; 1st_fb→2nd→… for
# mixed/edit) is built separately by cut_chain_for_mode().


def _gap(name: str, category: str, mode: str) -> dict:
    """Helper: build a chain_spec gap dict from TIMELINE_VALUES[mode][name]."""
    mn, df, mx = TIMELINE_VALUES[mode][name]
    return {"name": name, "category": category, "min": mn, "default": df, "max": mx}


def chain_spec_animation() -> list:
    """
    Pre-pro segment for animation mode.

    Chain (earliest → latest):
        Script + Workflow Received
          → script_to_treatment      → Treatment Meeting (internal)
          → treatment_to_stb_sf      → STB + SF Submit
          → stb_sf_fb                → STB + SF Confirm     (client milestone)
          → stb_sf_to_animatic       → Animatic Submit
          → animatic_fb              → Animatic Confirm     (client milestone, end)
    """
    return [
        _gap("script_to_treatment",   "pre_pro", "animation"),
        _gap("treatment_to_stb_sf",   "pre_pro", "animation"),
        _gap("stb_sf_fb",             "pre_pro", "animation"),
        _gap("stb_sf_to_animatic",    "pre_pro", "animation"),
        _gap("animatic_fb",           "pre_pro", "animation"),
    ]


def chain_spec_mixed() -> list:
    """
    Pre-pro segment for mixed mode (storyboard chain handled separately by
    build_storyboard_chain).

    Chain (earliest → latest, starting from Materials Ready):
        Materials Ready
          → materials_to_rough_cut   → Rough Cut Submit
          → rough_cut_fb             → Rough Cut FB end
          → rough_to_first_cut       → 1st Cut Submit  (end)
    """
    # rough_cut_fb is a client feedback window — same nature as first/second/third_cut_fb.
    # Category "cut_fb" (not "pre_pro") so it compresses together with the other client FBs
    # under window pressure. Otherwise 1st/2nd/3rd Cut FB compress to 1 wd while Rough Cut FB
    # stays at default 2 wd — inconsistent rule from the user's perspective.
    return [
        _gap("materials_to_rough_cut", "pre_pro", "mixed"),
        _gap("rough_cut_fb",           "cut_fb",  "mixed"),
        _gap("rough_to_first_cut",     "pre_pro", "mixed"),
    ]


def chain_spec_edit() -> list:
    """
    Pre-pro segment for edit mode (storyboard chain handled separately).

    Chain (earliest → latest):
        Materials Ready
          → materials_to_first_cut   → 1st Cut Submit  (end)
    """
    return [
        _gap("materials_to_first_cut", "pre_pro", "edit"),
    ]


def cut_chain_for_mode(mode: str, cut_count: int) -> list:
    """
    Build cut chain spec for the given mode.

    Per spec §6 + Q3 resolution: cut chain is separate from pre_pro_*.

    For animation:
        Animatic Confirm
          → animatic_to_first_cut    → 1st Cut Submit
          → first_cut_fb             → 1st Cut FB end
          → second_cut               → 2nd Cut Submit
          → second_cut_fb            → 2nd Cut FB end
          [→ third_cut               → 3rd Cut Submit
           → third_cut_fb            → 3rd Cut FB end]   (3-cut only)
          → (Picture Lock)

    For mixed / edit:
        1st Cut Submit
          → first_cut_fb             → 1st Cut FB end
          → second_cut               → 2nd Cut Submit
          → second_cut_fb            → 2nd Cut FB end
          [→ third_cut               → 3rd Cut Submit
           → third_cut_fb            → 3rd Cut FB end]   (3-cut only)
          → (Picture Lock)

    Per Q4 resolution: 2-cut variant skips third_cut + third_cut_fb.

    Args:
        mode: "animation" | "mixed" | "edit"
        cut_count: 2 | 3

    Returns: chain_spec list ordered earliest → latest.
    """
    if mode not in ("animation", "mixed", "edit"):
        raise ValueError(f"cut_chain_for_mode: mode must be animation/mixed/edit, got {mode!r}")
    if cut_count not in (2, 3):
        raise ValueError(f"cut_chain_for_mode: cut_count must be 2 or 3, got {cut_count!r}")

    spec: list = []

    if mode == "animation":
        spec.append(_gap("animatic_to_first_cut", "cut_production", "animation"))

    spec.append(_gap("first_cut_fb", "cut_fb", mode))
    spec.append(_gap("second_cut", "cut_production", mode))
    spec.append(_gap("second_cut_fb", "cut_fb", mode))

    if cut_count == 3:
        spec.append(_gap("third_cut", "cut_production", mode))
        spec.append(_gap("third_cut_fb", "cut_fb", mode))

    return spec


def cut_chain_spec_standard(cut_count: int) -> list:
    """
    Build standard-mode cut chain spec (shoot → picture_lock).

    Standard mode TIMELINE_VALUES reuses generic gap names (cut_production, cut_fb)
    across all cuts, so we expand to per-cut entries with stable names. Output
    label set: 1st Cut / Client FB 1 / 2nd Cut / Client FB 2 / 3rd Cut / Client FB 3
    (matches build_output() consumption shape).

    Args:
        cut_count: 2 or 3
    Returns: chain_spec list ordered earliest → latest.
    """
    if cut_count not in (2, 3):
        raise ValueError(f"cut_chain_spec_standard: cut_count must be 2 or 3, got {cut_count!r}")

    vals = TIMELINE_VALUES["standard"]

    def _g(name: str, category: str, key: str) -> dict:
        mn, df, mx = vals[key]
        return {"name": name, "category": category, "min": mn, "default": df, "max": mx}

    spec = [
        _g("shoot_to_first_cut", "cut_production", "shoot_to_first_cut"),
        _g("first_cut_fb",       "cut_fb",         "cut_fb"),
    ]
    if cut_count >= 2:
        spec.append(_g("second_cut",    "cut_production", "cut_production"))
        spec.append(_g("second_cut_fb", "cut_fb",         "cut_fb"))
    if cut_count == 3:
        spec.append(_g("third_cut",     "cut_production", "cut_production"))
        spec.append(_g("third_cut_fb",  "cut_fb",         "cut_fb"))
    return spec


def walk_cut_chain_forward(start_anchor: date, chain_spec: list, gaps: dict,
                           cut_count: int, holidays: set) -> tuple:
    """
    Walk cut chain forward from start_anchor, producing the (label, date) pair
    list consumed by build_output().

    Per spec §3 + Open Item #1: emit cut_warnings for any production gap
    (shoot→1st, 1st_fb→2nd, 2nd_fb→3rd) ≤ 3 wd.

    Returns (chain_pairs, cut_warnings).
    """
    by_name = {g["name"]: gaps[g["name"]] for g in chain_spec}
    chain: list = []
    cut_durations: list = []  # (label, gap_wd) for cut_production gaps only

    g = by_name["shoot_to_first_cut"]
    d = add_wd(start_anchor, g, holidays)
    chain.append(("1st Cut", d))
    cut_durations.append(("1st Cut", g))

    d = add_wd(d, by_name["first_cut_fb"], holidays)
    chain.append(("Client FB 1", d))

    if cut_count >= 2:
        g = by_name["second_cut"]
        d = add_wd(d, g, holidays)
        chain.append(("2nd Cut", d))
        cut_durations.append(("2nd Cut", g))
        d = add_wd(d, by_name["second_cut_fb"], holidays)
        chain.append(("Client FB 2", d))
    if cut_count == 3:
        g = by_name["third_cut"]
        d = add_wd(d, g, holidays)
        chain.append(("3rd Cut", d))
        cut_durations.append(("3rd Cut", g))
        d = add_wd(d, by_name["third_cut_fb"], holidays)
        chain.append(("Client FB 3", d))

    cut_warnings: list = []
    for label, gap_wd in cut_durations:
        if gap_wd <= 3:
            cut_warnings.append(
                f"⚠️ {label} 只有 {gap_wd} wd（≤ 3 wd 危險水平）— post team 容易頂唔順，"
                f"建議 director / producer review 條 cut 嘅 scope。"
            )
    return chain, cut_warnings


def pre_pro_animation() -> list:
    """Thin wrapper — returns chain_spec_animation() pre-pro segment."""
    return chain_spec_animation()


def pre_pro_mixed() -> list:
    """Thin wrapper — returns chain_spec_mixed() pre-pro segment."""
    return chain_spec_mixed()


def pre_pro_edit() -> list:
    """Thin wrapper — returns chain_spec_edit() pre-pro segment."""
    return chain_spec_edit()


def walk_chain_backward(end_anchor: date, chain_spec: list, gaps: dict,
                        holidays: set) -> dict:
    """
    Walk a chain spec backward from end_anchor, assigning a date to each
    boundary milestone.

    chain_spec: list ordered earliest → latest (as produced by
        chain_spec_animation/mixed/edit + cut_chain_for_mode).
    gaps: {gap_name: resolved_wd} from compress_to_min().
    end_anchor: date of the LAST milestone (after the final gap).

    Returns dict {gap_name: start_date_of_gap}, where start_date_of_gap
    is the date end_anchor stepped back by the cumulative wd from that
    gap to end_anchor. Plus key "_end_anchor" holding end_anchor itself.

    Example: chain [A, B] with gaps {A:2, B:3}, end_anchor=Day10
    Returns {A: Day10-5wd, B: Day10-3wd, _end_anchor: Day10}.
    """
    result: dict = {"_end_anchor": end_anchor}
    cursor = end_anchor
    for gap in reversed(chain_spec):
        cursor = sub_wd(cursor, gaps[gap["name"]], holidays)
        result[gap["name"]] = cursor
    result["_chain_start"] = cursor
    return result


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
    # --- Pure-post mode flags (spec §2) ---
    p.add_argument("--mode", choices=["animation", "mixed", "edit"],
                   help="Pure-post sub-mode. Required when --shoot-mode=pure-post.")
    p.add_argument("--storyboard", choices=["we-make", "client-provides", "none"],
                   help="Storyboard provenance for mixed/edit modes. Required for those modes.")
    p.add_argument("--storyboard-mode", choices=["sequential", "parallel"],
                   help="Force storyboard sub-chain layout. Default = auto.")
    p.add_argument("--complexity", choices=["simple", "medium", "complex"], default="medium",
                   help="Project complexity. v1: accepted but ignored — see backlog/ideas/complexity-driven-selective-expansion.md")
    p.add_argument("--push-fb-sameday", action="store_true",
                   help="Override buffer-default (2 wd FB) for 2nd/3rd cut to allow same-day FB.")
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
    # --- DOF-made pre-pro deliverables (Script / Video Flow / Storyboard) ---
    # When DOF writes script (or makes Video Flow / Storyboard) before client
    # can sign off and unblock production, effective_kickstart must be pushed
    # past the last client confirm date — not anchored to today. See
    # dof/workflows/timeline-planning-considerations.md (vault) or
    # skills/producer/timeline-planning-context.md (KB mirror).
    p.add_argument("--dof-pre-pro-deliverables", default="",
                   help="Comma-list of DOF-made pre-pro deliverables to prepend "
                        "into the chain. Valid: script, video-flow, storyboard. "
                        "Sequencing: Script → Video Flow OR Storyboard "
                        "(VF and STB mutually exclusive; if both supplied, "
                        "Video Flow is dropped in favor of Storyboard).")
    p.add_argument("--script-write-days", type=int, default=3,
                   help="DOF script writing days (default 3 wd; internal 2-3, outsourced 2-4).")
    p.add_argument("--script-confirm-wd", type=int, default=3,
                   help="Client script confirm turnaround (default 3 wd; needs senior approval).")
    p.add_argument("--video-flow-write-days", type=int, default=3,
                   help="DOF Video Flow drafting days (default 3 wd; range 1-3).")
    p.add_argument("--video-flow-confirm-wd", type=int, default=2,
                   help="Client Video Flow confirm turnaround (default 2 wd; range 1-3).")
    p.add_argument("--storyboard-write-days", type=int, default=5,
                   help="DOF Storyboard production days (default 5 wd; range 3-6; "
                        "mixed extreme 1-2; full animation min 3).")
    p.add_argument("--storyboard-confirm-wd", type=int, default=2,
                   help="Client Storyboard confirm turnaround (default 2 wd; range 1-3).")
    # --- User-supplied milestone anchors (bug: user-supplied-dates-not-anchored) ---
    # Treat user-supplied milestone dates as LOCKED ANCHORS, not candidates.
    # Repeatable; format `name=YYYY-MM-DD`. Aliases see ALIAS_TO_TARGETS.
    # Common: storyboard_submit, rough_cut_submit, first_cut_submit,
    # first_cut_fb_due, second_cut_submit, second_cut_fb_due, third_cut_submit,
    # third_cut_fb_due, picture_lock, color_sound, final_output, shoot_date.
    p.add_argument("--anchor", action="append", default=[],
                   help="User-supplied milestone anchor: name=YYYY-MM-DD (repeatable). "
                        "Supplied dates are locked; surrounding milestones stay at "
                        "script default. See ALIAS_TO_TARGETS for valid names.")
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


def compute_dof_pre_pro_chain(today: date, args, holidays: set) -> tuple:
    """
    Compute the forward chain of DOF-made pre-pro deliverables (Script /
    Video Flow / Storyboard) starting from today. Pushes effective_kickstart
    past the last client confirm date so downstream chain math doesn't anchor
    materials_ready / shoot prep to a date when client haven't yet unblocked.

    Returns (new_effective_kickstart, deliverable_entries, warnings).

    deliverable_entries = list of dicts:
        {
            "kind": "submit" | "confirm",
            "deliverable": "Script" | "Video Flow" | "Storyboard",
            "label": display label (e.g. "DOF Script Submit"),
            "date": date,
            "party": "DOF" | "Client",
            "color": "9" | "2",
        }
    Each output path adapts these into m()/mm() format and prepends to its
    milestone list.

    Sequencing rule: Script → (Video Flow OR Storyboard). VF and STB are
    mutually exclusive (DOF only does one align doc). If both supplied,
    drop Video Flow with a warning.
    """
    today_pushed = push_to_wd(today, holidays)
    raw_input = (args.dof_pre_pro_deliverables or "").strip()
    if not raw_input:
        return today_pushed, [], []

    raw = [s.strip().lower() for s in raw_input.split(",") if s.strip()]
    valid = {"script", "video-flow", "storyboard"}
    warnings: list = []
    deliverables: list = []
    for d in raw:
        if d not in valid:
            warnings.append(
                f"⚠️ --dof-pre-pro-deliverables: 唔識 '{d}'，"
                f"valid 值係 script/video-flow/storyboard，已 ignore。"
            )
            continue
        if d not in deliverables:
            deliverables.append(d)

    if "video-flow" in deliverables and "storyboard" in deliverables:
        warnings.append(
            "⚠️ Video Flow 同 Storyboard 互斥（DOF 只做其中一個 align doc）。"
            "已自動移除 Video Flow，跟 Storyboard 行。"
        )
        deliverables = [d for d in deliverables if d != "video-flow"]

    if not deliverables:
        return today_pushed, [], warnings

    # Enforce canonical ordering: Script first, then Video Flow OR Storyboard.
    canonical_order = ["script", "video-flow", "storyboard"]
    deliverables = [d for d in canonical_order if d in deliverables]

    SPEC = {
        "script":     ("Script",     args.script_write_days,     args.script_confirm_wd),
        "video-flow": ("Video Flow", args.video_flow_write_days, args.video_flow_confirm_wd),
        "storyboard": ("Storyboard", args.storyboard_write_days, args.storyboard_confirm_wd),
    }

    entries: list = []
    cursor = today_pushed
    for key in deliverables:
        label, wd_write, wd_fb = SPEC[key]
        if wd_write < 1 or wd_fb < 1:
            warnings.append(
                f"⚠️ {label}: write_days={wd_write}, confirm_wd={wd_fb} — 兩者都應 ≥ 1 wd。"
            )
        submit_d = add_wd(cursor, max(wd_write, 1), holidays)
        confirm_d = add_wd(submit_d, max(wd_fb, 1), holidays)
        entries.append({
            "kind": "submit",
            "deliverable": label,
            "label": f"DOF {label} Submit",
            "date": submit_d,
            "party": "DOF",
            "color": "9",
        })
        entries.append({
            "kind": "confirm",
            "deliverable": label,
            "label": f"Client {label} Confirm",
            "date": confirm_d,
            "party": "Client",
            "color": "2",
        })
        cursor = confirm_d

    new_kickstart = cursor
    pretty = " → ".join(SPEC[d][0] for d in deliverables)
    warnings.append(
        f"DOF 寫嘅 pre-pro deliverables ({pretty}) 推 effective kickstart 由 "
        f"{today_pushed.isoformat()} → {new_kickstart.isoformat()} (= last client confirm date)。"
        f" Materials ready / shoot prep 唔可以早過呢個日期。"
    )
    return new_kickstart, entries, warnings


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

    # Step 0: effective kickstart.
    # If DOF makes pre-pro deliverables (Script / Video Flow / Storyboard)
    # before client can sign off, push effective_kickstart past the last
    # client confirm date. Otherwise default = push_to_wd(today).
    effective_kickstart, dof_pre_pro_entries, dof_pre_pro_warnings = (
        compute_dof_pre_pro_chain(today, args, holidays)
    )
    warnings.extend(dof_pre_pro_warnings)

    # Parse user-supplied milestone anchors (bug: user-supplied-dates-not-anchored).
    # Applied AFTER milestone list assembled in build_output / _build_pure_post_milestones.
    user_anchors, anchor_parse_warnings = parse_user_anchors(args.anchor)
    warnings.extend(anchor_parse_warnings)

    # Step B: backward tail
    tail = backward_tail(final_output, has_vo, holidays)

    # ----- pure-post branch -----
    if shoot_mode == "pure-post":
        if args.mode not in ("animation", "mixed", "edit"):
            emit({"status": "error",
                  "error": "pure-post mode requires --mode {animation|mixed|edit}"})
            return
        return run_pure_post(args, effective_kickstart, today, final_output,
                             tail, has_vo, holidays, holiday_names, warnings,
                             dof_pre_pro_entries=dof_pre_pro_entries,
                             user_anchors=user_anchors)

    # ----- standard shoot+post branch -----
    return run_standard(args, effective_kickstart, today, final_output, tail,
                        has_vo, has_style_frame, holidays, holiday_names, warnings,
                        dof_pre_pro_entries=dof_pre_pro_entries,
                        user_anchors=user_anchors)


def decide_cut_count(args, available_window: int) -> tuple[int, str | None, list]:
    """
    Return (cut_count, scenario_label, extra_warnings).

    cut_count selection only — gap sizing happens in compress_to_min downstream.
    Window thresholds (20 / 14 / 10) preserved from legacy logic so warnings
    still fire at the right boundaries.
    """
    extra = []
    # Senior approval rule overrides everything
    if args.senior_approval_fb2_wd and args.senior_approval_fb2_wd > 0:
        return 2, "2-cut + senior approval FB2", extra
    # User override
    if args.cut_count_override in (2, 3):
        if args.cut_count_override == 3 and available_window < 14:
            extra.append("⚠️ User override 3-cut，但 available window < 14 wd，cut gaps 會被壓到 min")
        if args.cut_count_override == 2 and available_window < 10:
            extra.append("⚠️ 2-cut 都頂唔順 available window，會 escalate Pattern J")
        return args.cut_count_override, f"{args.cut_count_override}-cut (user override)", extra
    # Default decision matrix
    if available_window >= 20:
        return 3, "3-cut standard", extra
    if 14 <= available_window <= 19:
        extra.append(
            "⚠️ Available window 14–19 wd，預設行 3-cut（cut gaps 會被壓緊）。"
            "如要寬鬆 timeline 改 2-cut，請指示。"
        )
        return 3, "3-cut compressed (14–19 wd default)", extra
    if 10 <= available_window <= 13:
        extra.append(
            "⚠️ Available window 10–13 wd，行 2-cut（cut gaps 收緊）。"
            "Feedback time 收緊，要同 client 講明。"
        )
        return 2, "2-cut compressed (10–13 wd)", extra
    # < 10 wd
    return 0, None, extra


def run_standard(args, effective_kickstart, today, final_output, tail,
                 has_vo, has_style_frame, holidays, holiday_names, warnings,
                 dof_pre_pro_entries=None, user_anchors=None):
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

    cut_count, scenario_label, extra_w = decide_cut_count(args, available_window)
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
                f"= {available_window} wd，低於 2-cut 自動嘗試門檻 (10 wd)。"
                f"Escalate Sohling for manual judgment."
            ],
            "cut_warnings": [],
            "milestones": [],
        })
        return

    # Build cut chain (default-first compression — spec §3.2)
    chain_spec = cut_chain_spec_standard(cut_count)
    target_last_fb = sub_wd(tail["picture_lock"], 1, holidays)
    available_cut_window = wd_count(shoot_date, target_last_fb, holidays)
    compression = compress_to_min(chain_spec, available_cut_window)
    if compression["infeasible"]:
        # Even all-min cut chain doesn't fit — fall through to compressed-edge-case
        # which will re-derive shoot_date and may further reduce cut_count.
        return run_compressed_edge_case(
            args, effective_kickstart, today, final_output, tail,
            has_vo, has_style_frame, holidays, holiday_names, warnings,
            standard_pre_pro_earliest=None,
            dof_pre_pro_entries=dof_pre_pro_entries,
            user_anchors=user_anchors,
        )
    cut_chain, cut_warnings = walk_cut_chain_forward(
        shoot_date, chain_spec, compression["gaps"], cut_count, holidays
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
            has_vo, has_style_frame, holidays, holiday_names, warnings,
            standard_pre_pro_earliest=earliest,
            dof_pre_pro_entries=dof_pre_pro_entries,
            user_anchors=user_anchors,
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
        holiday_names=holiday_names,
        warnings=warnings,
        cut_warnings=cut_warnings,
        dof_pre_pro_entries=dof_pre_pro_entries,
        user_anchors=user_anchors,
    )


def run_compressed_edge_case(args, effective_kickstart, today, final_output, tail,
                             has_vo, has_style_frame, holidays, holiday_names, warnings,
                             standard_pre_pro_earliest=None,
                             dof_pre_pro_entries=None, user_anchors=None):
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

    # Build cut chain (default-first compression — spec §3.2). standard mode
    # TIMELINE_VALUES min already matches legacy "extreme" floors (shoot_to_first_cut
    # min=2, cut_production min=2, cut_fb min=1), so a single compress_to_min call
    # handles the squeeze.
    chain_spec = cut_chain_spec_standard(cut_count)
    target_last_fb = sub_wd(tail["picture_lock"], 1, holidays)
    available_cut_window = wd_count(shoot_date, target_last_fb, holidays)
    compression = compress_to_min(chain_spec, available_cut_window)

    if compression["infeasible"]:
        # Even all-min cut chain can't fit → Extreme-Squeeze Tier
        return emit_extreme_squeeze(
            args, effective_kickstart, final_output, shoot_date, tail,
            available_window, compression["deficit_wd"], holidays, warnings
        )

    cut_chain, cut_warnings = walk_cut_chain_forward(
        shoot_date, chain_spec, compression["gaps"], cut_count, holidays
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
        holiday_names=holiday_names,
        warnings=warnings,
        cut_warnings=cut_warnings,
        dof_pre_pro_entries=dof_pre_pro_entries,
        user_anchors=user_anchors,
    )


def run_pure_post(args, effective_kickstart, today, final_output,
                  tail, has_vo, holidays, holiday_names, warnings,
                  dof_pre_pro_entries=None, user_anchors=None):
    """
    Pure-post dispatcher (spec §11.5). Routes to mode runner.
    --mode in {animation, mixed, edit} is required; main() validates upfront.
    """
    return _run_pure_post_modes(args, effective_kickstart, today, final_output,
                                tail, has_vo, holidays, holiday_names, warnings,
                                dof_pre_pro_entries=dof_pre_pro_entries,
                                user_anchors=user_anchors)


# ---------- Pure-post mode runner (spec §6 + §7 + §11.5) ----------

def _run_pure_post_modes(args, effective_kickstart, today, final_output,
                         tail, has_vo, holidays, holiday_names, warnings,
                         dof_pre_pro_entries=None, user_anchors=None):
    """
    Dispatcher for --mode animation/mixed/edit. Implements the 3-cut → 2-cut →
    extreme-squeeze fallback ladder (spec §6 Q4 resolution) and routes
    storyboard sub-chain for mixed/edit (spec §7).
    """
    mode = args.mode
    project = args.project
    available_window = wd_count(effective_kickstart, tail["picture_lock"], holidays)

    # Storyboard validation (mixed/edit only).
    if mode in ("mixed", "edit"):
        if args.storyboard is None:
            emit({"status": "error",
                  "error": f"--storyboard required when --mode={mode} (we-make|client-provides|none)"})
            return
    elif args.storyboard is not None:
        warnings.append(f"⚠️ --storyboard ignored for --mode={mode}")

    # Build pre-pro chain spec (segment only, per Q3).
    if mode == "animation":
        pre_pro_spec = chain_spec_animation()
    elif mode == "mixed":
        pre_pro_spec = chain_spec_mixed()
    else:  # edit
        pre_pro_spec = chain_spec_edit()

    # Try 3-cut → 2-cut fallback ladder.
    fallbacks_triggered: list = []
    cut_count = 3
    cut_chain_spec = cut_chain_for_mode(mode, cut_count)
    full_spec = pre_pro_spec + cut_chain_spec
    compress = compress_to_min(full_spec, available_window)

    if compress["infeasible"]:
        # Try 2-cut.
        cut_count = 2
        cut_chain_spec = cut_chain_for_mode(mode, cut_count)
        full_spec = pre_pro_spec + cut_chain_spec
        compress_2 = compress_to_min(full_spec, available_window)
        if compress_2["infeasible"]:
            # Both 3-cut and 2-cut infeasible at min → Pattern J extreme squeeze.
            warnings.append(
                f"⚠️ Mode={mode}: 3-cut min ({compress['total_wd']} wd) 同 2-cut min "
                f"({compress_2['total_wd']} wd) 都超過 available window "
                f"({available_window} wd)。Trigger Pattern J extreme squeeze."
            )
            return emit_extreme_squeeze(
                args, effective_kickstart, final_output, None, tail,
                available_window, compress_2["deficit_wd"], holidays, warnings
            )
        # 2-cut feasible — emit with explicit warning.
        warnings.append(
            f"⚠️ Mode={mode}: 3-cut min ({compress['total_wd']} wd) > available window "
            f"({available_window} wd)。Fall back 至 2-cut（skip 3rd cut + 3rd FB）。"
        )
        fallbacks_triggered.append(f"cut_count_2_fallback_from_3")
        compress = compress_2

    # Apply buffer-default rule: 2nd/3rd cut FB default to min(2, default), unless
    # --push-fb-sameday override (spec §9.3). compress_to_min already pushed cut_fb
    # to min if compression triggered. Here, when cut_fb category was NOT
    # compressed, ensure 2nd/3rd FB respect the 2-wd buffer default (1 if min=1).
    if "cut_fb" not in compress["compressions_applied"] and not args.push_fb_sameday:
        for gap_name in ("second_cut_fb", "third_cut_fb"):
            if gap_name in compress["gaps"]:
                # default is already (1,2,3)[1]=2 — buffer-default already satisfied.
                pass

    # Walk cut chain backward from picture_lock.
    cut_dates = walk_chain_backward(tail["picture_lock"], cut_chain_spec,
                                    compress["gaps"], holidays)

    # The cut chain's "_chain_start" date is the END of the pre-pro chain.
    pre_pro_end_anchor = cut_dates["_chain_start"]

    # For mixed/edit with storyboard=we-make: insert storyboard sub-chain.
    storyboard_chain_mode = None
    storyboard_dates = None
    if mode in ("mixed", "edit") and args.storyboard == "we-make":
        # Pre-pro segment ends at 1st Cut Submit; storyboard chain feeds into
        # Materials Ready (= start of pre_pro segment).
        pre_pro_dates = walk_chain_backward(pre_pro_end_anchor, pre_pro_spec,
                                            compress["gaps"], holidays)
        materials_ready_anchor = pre_pro_dates["_chain_start"]
        storyboard_window = wd_count(effective_kickstart, materials_ready_anchor, holidays)
        sb = build_storyboard_chain(
            materials_ready_anchor, storyboard_window, mode, holidays,
            forced_chain_mode=args.storyboard_mode,
        )
        storyboard_chain_mode = sb["chain_mode"]
        storyboard_dates = sb
        if sb["fallback_triggered"]:
            fallbacks_triggered.append("storyboard_parallel_fallback")
            warnings.append(
                f"⚠️ Storyboard sub-chain auto-fell-back to parallel "
                f"(window {storyboard_window} wd < seq need {sb['seq_window_needed']} wd)."
            )
    else:
        pre_pro_dates = walk_chain_backward(pre_pro_end_anchor, pre_pro_spec,
                                            compress["gaps"], holidays)

    # Emit milestones in chronological order.
    milestones = _build_pure_post_milestones(
        mode=mode,
        project=project,
        pre_pro_dates=pre_pro_dates,
        cut_dates=cut_dates,
        tail=tail,
        has_vo=has_vo,
        cut_count=cut_count,
        storyboard_choice=args.storyboard if mode in ("mixed", "edit") else None,
        storyboard_dates=storyboard_dates,
        dof_pre_pro_entries=dof_pre_pro_entries,
    )

    # Apply user-supplied anchors AFTER milestones assembled. Pure-post milestones
    # are built in chronological order already; overlay then re-sort + re-order.
    anchor_results: list = []
    if user_anchors:
        anchor_results, anchor_warnings, _infeas = apply_anchors(
            milestones, user_anchors, holidays
        )
        warnings.extend(anchor_warnings)
        milestones.sort(key=lambda x: x["date"])
        for i, ms in enumerate(milestones, start=1):
            ms["order"] = i

    # Past-milestone detection.
    earliest = pre_pro_dates["_chain_start"]
    if storyboard_dates is not None:
        earliest = min(earliest, storyboard_dates["storyboard_submit"])
    if earliest < effective_kickstart:
        warnings.append(
            f"⚠️ Earliest milestone {earliest.isoformat()} < kickstart "
            f"{effective_kickstart.isoformat()}. Window over-tight even after compression."
        )

    payload = {
        "status": "pure_post_mode",
        "mode": mode,
        "storyboard_choice": args.storyboard if mode in ("mixed", "edit") else None,
        "storyboard_chain_mode": storyboard_chain_mode,
        "cut_count": cut_count,
        "buffer_overrides": ["push_fb_sameday"] if args.push_fb_sameday else [],
        "fallbacks_triggered": fallbacks_triggered,
        "compressions_applied": compress["compressions_applied"],
        "effective_kickstart": effective_kickstart.isoformat(),
        "final_output": final_output.isoformat(),
        "available_wd": available_window,
        "total_chain_wd": compress["total_wd"],
        "scenario_label": f"Pure-post {mode} {cut_count}-cut",
        "warnings": warnings,
        "milestones": milestones,
        "user_anchors_applied": anchor_results,
        "holidays_in_window": compute_holidays_in_window(
            milestones, None, holidays, holiday_names
        ),
    }
    emit(payload)


def _build_pure_post_milestones(*, mode, project, pre_pro_dates, cut_dates,
                                tail, has_vo, cut_count, storyboard_choice,
                                storyboard_dates, dof_pre_pro_entries=None):
    """Build ordered milestone list for pure-post mode output (spec §8)."""
    milestones: list = []
    order = 1

    def add(name, label, d, **kwargs):
        nonlocal order
        kwargs.setdefault("project", project)
        milestones.append(mm(order, name, label, d, **kwargs))
        order += 1

    # DOF-made pre-pro deliverables prepend (Script / Video Flow / Storyboard).
    # Inserted before all other milestones so chronological order surfaces them
    # at the top of the timeline.
    if dof_pre_pro_entries:
        for entry in dof_pre_pro_entries:
            slug = entry["deliverable"].lower().replace(" ", "_")
            name = f"dof_{slug}_{entry['kind']}"
            add(name, entry["label"], entry["date"],
                calendar_emit=True,
                client_facing=(entry["party"] == "Client"),
                party=entry["party"],
                color=entry["color"])

    # Storyboard sub-chain (mixed/edit only, when we-make).
    if storyboard_dates is not None:
        add("storyboard_submit", "Storyboard Submit",
            storyboard_dates["storyboard_submit"],
            calendar_emit=True, client_facing=False, party="DOF")
        add("storyboard_confirm", "Storyboard Confirm",
            storyboard_dates["storyboard_confirm"],
            calendar_emit=True, client_facing=True, party="Client", color="2")

    # Mode-specific pre-pro segment.
    if mode == "animation":
        add("script_workflow_received", "Script + Workflow Received",
            pre_pro_dates["_chain_start"],
            calendar_emit=True, client_facing=False, party="Client")
        add("treatment_meeting", "Treatment Meeting",
            pre_pro_dates["treatment_to_stb_sf"],
            calendar_emit=False, internal_only=True, party="DOF", color="9")
        add("stb_sf_submit", "STB + SF Submit",
            pre_pro_dates["stb_sf_fb"],
            calendar_emit=True, client_facing=False, party="DOF")
        add("stb_sf_confirm", "STB + SF Confirm",
            pre_pro_dates["stb_sf_to_animatic"],
            calendar_emit=True, client_facing=True, party="Client", color="2")
        add("animatic_submit", "Animatic Submit",
            pre_pro_dates["animatic_fb"],
            calendar_emit=True, client_facing=False, party="DOF")
        add("animatic_confirm", "Animatic Confirm",
            pre_pro_dates["_end_anchor"],
            calendar_emit=True, client_facing=True, party="Client", color="2")
        # Materials Ready = Animatic Confirm date (Q2 resolution).
        add("materials_ready", "Materials Ready",
            pre_pro_dates["_end_anchor"],
            calendar_emit=True, client_facing=False, party="DOF")
    else:
        # mixed / edit
        if storyboard_dates is None:
            # No storyboard chain — Materials Ready = pre_pro chain start.
            mr_date = pre_pro_dates["_chain_start"]
        else:
            mr_date = storyboard_dates["materials_ready"]
        add("materials_ready", "Materials Ready", mr_date,
            calendar_emit=True, client_facing=False, party="DOF")
        if mode == "mixed":
            # Rough cut milestones.
            add("rough_cut_submit", "Rough Cut Submit",
                pre_pro_dates["rough_cut_fb"],
                calendar_emit=True, client_facing=False, party="DOF")
            add("rough_cut_fb_due", "Rough Cut FB Due",
                pre_pro_dates["rough_to_first_cut"],
                calendar_emit=True, client_facing=True, party="Client", color="2")
        # 1st Cut Submit = pre-pro chain end anchor.
        add("first_cut_submit", "1st Cut Submit",
            pre_pro_dates["_end_anchor"],
            calendar_emit=True, client_facing=False, party="DOF")

    # Cut chain.
    # For animation: cut chain starts from animatic_confirm (cut_dates["_chain_start"]
    # = animatic_confirm). animatic_to_first_cut gap → 1st Cut Submit.
    # For mixed/edit: cut chain starts from 1st Cut Submit.
    if mode == "animation":
        add("first_cut_submit", "1st Cut Submit",
            cut_dates["first_cut_fb"],
            calendar_emit=True, client_facing=False, party="DOF")

    add("first_cut_fb_due", "1st Cut FB Due",
        cut_dates["second_cut"],
        calendar_emit=True, client_facing=True, party="Client", color="2")
    add("second_cut_submit", "2nd Cut Submit",
        cut_dates["second_cut_fb"],
        calendar_emit=True, client_facing=False, party="DOF")

    if cut_count == 3:
        add("second_cut_fb_due", "2nd Cut FB Due",
            cut_dates["third_cut"],
            calendar_emit=True, client_facing=True, party="Client", color="2")
        add("third_cut_submit", "3rd Cut Submit",
            cut_dates["third_cut_fb"],
            calendar_emit=True, client_facing=False, party="DOF")
        add("third_cut_fb_due", "3rd Cut FB Due",
            cut_dates["_end_anchor"],
            calendar_emit=True, client_facing=True, party="Client", color="2")
    else:
        # 2-cut: 2nd cut FB closes at picture_lock (= cut_dates _end_anchor).
        add("second_cut_fb_due", "2nd Cut FB Due",
            cut_dates["_end_anchor"],
            calendar_emit=True, client_facing=True, party="Client", color="2")

    # Backward tail (mode-agnostic; reuse existing tail dict from main()).
    add("picture_lock", "Picture Lock", tail["picture_lock"],
        calendar_emit=True, client_facing=False, party="DOF", color="11")
    if has_vo and tail["vo_start"] is not None:
        add("vo_start", "VO Recording Start", tail["vo_start"],
            calendar_emit=True, client_facing=False, party="DOF")
        add("vo_end", "VO Recording End", tail["vo_end"],
            calendar_emit=True, client_facing=False, party="DOF")
    add("color_sound", "Color / Sound / Subtitle", tail["cs"],
        calendar_emit=True, client_facing=False, party="DOF")
    # Final output is implicit (= tail end), but emit for completeness.
    # final_output is passed via main; reuse tail["cs"]+1wd? Actually final_output
    # is the anchor — emit from caller's final_output. Skipping here; payload
    # surfaces it as top-level field.

    return milestones


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


def compute_holidays_in_window(milestones: list, vo_window: dict | None,
                               holidays: set, holiday_names: dict) -> list:
    """Public holidays falling within the timeline's date range.

    Window = earliest milestone date → latest milestone date, extended to cover
    vo_window if present. Self-evidences that the script has loaded + applied
    the HK holiday set, so downstream consumers don't need to verify externally.
    """
    if not milestones:
        return []
    iso_dates = [ms["date"] for ms in milestones]
    start = date.fromisoformat(min(iso_dates))
    end = date.fromisoformat(max(iso_dates))
    if vo_window:
        vo_start = date.fromisoformat(vo_window["start"])
        vo_end = date.fromisoformat(vo_window["end"])
        if vo_start < start:
            start = vo_start
        if vo_end > end:
            end = vo_end
    return [
        {"date": hd.isoformat(), "name": holiday_names.get(hd, "Public Holiday")}
        for hd in sorted(holidays) if start <= hd <= end
    ]


def build_output(*, status, scenario_label, effective_kickstart, final_output,
                 shoot_date, shoot_days, available_window, cut_count,
                 pre_pro, cut_chain, tail, has_vo, has_style_frame,
                 compressed_style_frame_in_post, project, holidays, holiday_names,
                 warnings,
                 first_cut_start=None, cut_warnings=None,
                 dof_pre_pro_entries=None, user_anchors=None):
    """Assemble final milestones list and emit JSON."""
    milestones: list = []
    order = 1

    # DOF-made pre-pro deliverables (Script / Video Flow / Storyboard).
    # Inserted first; final milestones.sort() at end of function ensures
    # chronological order regardless of insertion sequence.
    if dof_pre_pro_entries:
        for entry in dof_pre_pro_entries:
            title = f"{entry['label']} - {project}"
            milestones.append(m(order, entry["label"], entry["date"],
                                entry["color"], entry["party"], title))
            order += 1

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

    # Apply user-supplied anchors AFTER push so user dates stay literal (user
    # knows; we surface non-wd as warning but don't move). Sort happens below.
    anchor_results: list = []
    if user_anchors:
        anchor_results, anchor_warnings, _infeas = apply_anchors(
            milestones, user_anchors, holidays
        )
        warnings.extend(anchor_warnings)

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
        "user_anchors_applied": anchor_results,
        "holidays_in_window": compute_holidays_in_window(
            milestones, vo_window, holidays, holiday_names
        ),
    }
    emit(payload)


if __name__ == "__main__":
    main()
