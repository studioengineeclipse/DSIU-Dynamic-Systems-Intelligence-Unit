"""Desktop state — read/write the desktop's own local state.

The desktop writes ONLY here (`dsiu_desktop_state/`): the registered workspaces and
the latest generated dashboard. It is safe when the dir/files do not exist yet.
"""

from __future__ import annotations

import json
import os

from . import DESKTOP_STATE_DIR, DESKTOP_STATE_VERSION, DRAFT_STAMP

_WORKSPACES = "registered_workspaces.json"
_DASHBOARD = "latest_dashboard.json"


def _read_json(path: str, default):
    if not os.path.isfile(path):
        return default
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def load_workspaces(state_dir: str = DESKTOP_STATE_DIR) -> list:
    doc = _read_json(os.path.join(state_dir, _WORKSPACES), None)
    return (doc or {}).get("workspaces", []) if isinstance(doc, dict) else []


def save_workspaces(state_dir: str, workspaces: list) -> str:
    os.makedirs(state_dir, exist_ok=True)
    path = os.path.join(state_dir, _WORKSPACES)
    doc = {
        "desktop_state_version": DESKTOP_STATE_VERSION,
        "status": f"{DRAFT_STAMP} — desktop workspace registry",
        "workspaces": workspaces,
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)
    return path


def save_dashboard(state_dir: str, dashboard: dict) -> str:
    os.makedirs(state_dir, exist_ok=True)
    path = os.path.join(state_dir, _DASHBOARD)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(dashboard, fh, indent=2)
    return path
