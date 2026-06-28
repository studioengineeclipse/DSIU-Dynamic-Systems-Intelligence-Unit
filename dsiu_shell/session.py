"""Session — build and save one shell session record.

A session stores both the rendered summary and the raw artifacts (OIL report and/or
UEF profile) so the shell can show quick status/history while preserving the full
trace. Sessions are saved by the write commands only (inspect/profile/analyze).
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone

from . import DRAFT_STAMP, SHELL_STATE_DIR


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S-%f")


def _law0_status(oil_bundle: "dict | None") -> str:
    if oil_bundle:
        pv = oil_bundle.get("policy_verdict") or {}
        return (f"law_0={pv.get('law_0', 'enforced')}; "
                f"draft_ok={pv.get('draft_ok', True)}; "
                "movement measured, direction unverified; no upgrade claimed")
    return "enforced (DRAFT) — classification only, execution not performed"


def _quick_status(command: str, target: str, oil_bundle, uef_profile) -> dict:
    report = (oil_bundle or {}).get("supervisor_report") or {}
    detected_layers = report.get("detected_layers")
    movement_score = report.get("movement_score")
    primary_lane = None
    permission_risk = None
    if uef_profile:
        primary_lane = uef_profile.get("primary_execution_lane")
        permission_risk = uef_profile.get("permission_risk")
    elif report.get("uef_summary"):
        primary_lane = report["uef_summary"].get("primary_execution_lane")
        permission_risk = report["uef_summary"].get("permission_risk")
    return {
        "command": command,
        "target": target,
        "detected_layers": detected_layers,
        "movement_score": movement_score,
        "primary_execution_lane": primary_lane,
        "permission_risk": permission_risk,
    }


def build_session(command: str, target: str, summary: str, *,
                  oil_bundle: "dict | None" = None,
                  uef_profile: "dict | None" = None) -> dict:
    report = (oil_bundle or {}).get("supervisor_report")
    next_action = ""
    if report:
        next_action = report.get("required_next_action", "")
    elif uef_profile:
        next_action = uef_profile.get("required_next_action", "")

    return {
        "kind": "shell_session",
        "status": f"{DRAFT_STAMP} — shell session record (Law 0)",
        "timestamp": _timestamp(),
        "command": command,
        "target": target,
        "oil_report": report,                 # raw supervisor report (or None)
        "uef_profile": uef_profile,           # raw UEF profile (or None)
        "rendered_summary": summary,
        "law0_status": _law0_status(oil_bundle),
        "required_next_action": next_action,
        "quick_status": _quick_status(command, target, oil_bundle, uef_profile),
    }


def save_session(state_dir: str, session: dict) -> str:
    os.makedirs(state_dir, exist_ok=True)
    ts = session.get("timestamp") or _timestamp()
    path = os.path.join(state_dir, f"session-{ts}.json")
    n = 1
    while os.path.exists(path):
        path = os.path.join(state_dir, f"session-{ts}-{n}.json")
        n += 1
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(session, fh, indent=2)
    return path
