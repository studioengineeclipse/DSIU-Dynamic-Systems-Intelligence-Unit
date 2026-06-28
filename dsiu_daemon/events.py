"""Events — the daemon state store: build/save/read events + snapshot persistence.

Read helpers (list/latest/load) never write. Snapshots are kept so `once` run twice
and `watch` cycles detect real change instead of comparing a pass to itself.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from . import DRAFT_STAMP


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S-%f")


def build_event(config, event_type: str, change: dict, change_summary: str, *,
                session: "dict | None" = None,
                shell_session_path: "str | None" = None,
                error: "str | None" = None) -> dict:
    movement_score = None
    uef_profile = None
    law0 = "enforced (DRAFT) — observation only, execution not performed"
    next_action = "Continue watching."

    if session:
        report = session.get("oil_report") or {}
        movement_score = report.get("movement_score")
        uef_profile = session.get("uef_profile")
        law0 = session.get("law0_status", law0)
        next_action = session.get("required_next_action", next_action)
    if event_type == "error":
        next_action = "Check the watched path and rerun. Execution not performed."

    return {
        "kind": "daemon_event",
        "status": f"{DRAFT_STAMP} — daemon observation event (Law 0); "
                  "movement measured ≠ improvement; no fixes applied",
        "event_type": event_type,
        "timestamp": _timestamp(),
        "watched_path": os.path.abspath(config.path),
        "name": config.display_name(),
        "changed_files": change.get("changed_files", []),
        "change_detail": {k: change.get(k, []) for k in ("added", "removed", "modified")},
        "change_summary": change_summary,
        "analyzed": session is not None,
        "shell_session_path": shell_session_path,
        "shell_session": session,
        "movement_score": movement_score,
        "uef_profile": uef_profile,
        "law0_status": law0,
        "required_next_action": next_action,
        "error": error,
    }


def save_event(state_dir: str, event: dict) -> str:
    os.makedirs(state_dir, exist_ok=True)
    ts = event.get("timestamp") or _timestamp()
    path = os.path.join(state_dir, f"event-{ts}.json")
    n = 1
    while os.path.exists(path):
        path = os.path.join(state_dir, f"event-{ts}-{n}.json")
        n += 1
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(event, fh, indent=2)
    return path


# --- read-only -------------------------------------------------------------

def _event_paths(state_dir: str) -> list:
    if not os.path.isdir(state_dir):
        return []
    files = [f for f in os.listdir(state_dir)
             if f.startswith("event-") and f.endswith(".json")]
    return [os.path.join(state_dir, f) for f in sorted(files)]


def load_event(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def list_events(state_dir: str, limit: int = 10) -> list:
    return [load_event(p) for p in list(reversed(_event_paths(state_dir)))[:limit]]


def latest_event(state_dir: str) -> "dict | None":
    paths = _event_paths(state_dir)
    return load_event(paths[-1]) if paths else None


# --- snapshot persistence --------------------------------------------------

def _snapshot_path(state_dir: str, slug: str) -> str:
    return os.path.join(state_dir, f"snapshot-{slug}.json")


def load_snapshot(state_dir: str, slug: str) -> "dict | None":
    path = _snapshot_path(state_dir, slug)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_snapshot(state_dir: str, slug: str, snap: dict) -> str:
    os.makedirs(state_dir, exist_ok=True)
    path = _snapshot_path(state_dir, slug)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snap, fh, indent=2)
    return path
