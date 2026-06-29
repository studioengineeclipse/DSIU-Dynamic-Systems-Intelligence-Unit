"""Workspace — register and list workspace paths in desktop state.

Registration only: adding a workspace records a path. It does NOT analyze, watch, or
otherwise run any organ against it.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from . import DESKTOP_STATE_DIR
from . import state as _state


def add_workspace(path: str, name: "str | None" = None,
                  state_dir: str = DESKTOP_STATE_DIR) -> dict:
    abspath = os.path.abspath(path)
    display = name or os.path.basename(abspath.rstrip(os.sep)) or abspath
    workspaces = _state.load_workspaces(state_dir)

    for ws in workspaces:                       # dedupe by absolute path
        if ws.get("path") == abspath:
            ws["name"] = display
            ws["exists"] = os.path.isdir(abspath)
            _state.save_workspaces(state_dir, workspaces)
            return ws

    record = {
        "name": display,
        "path": abspath,
        "exists": os.path.isdir(abspath),
        "registered_at": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S-%fZ"),
        "note": "registered only — not analyzed or watched (no execution performed)",
    }
    workspaces.append(record)
    _state.save_workspaces(state_dir, workspaces)
    return record


def list_workspaces(state_dir: str = DESKTOP_STATE_DIR) -> list:
    return _state.load_workspaces(state_dir)
