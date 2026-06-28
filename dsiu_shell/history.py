"""History — read-only access to saved shell sessions.

These helpers never write. status / history / explain build on them.
"""

from __future__ import annotations

import json
import os


def _session_paths(state_dir: str) -> list:
    if not os.path.isdir(state_dir):
        return []
    files = [f for f in os.listdir(state_dir)
             if f.startswith("session-") and f.endswith(".json")]
    return [os.path.join(state_dir, f) for f in sorted(files)]  # lexical == chrono


def load_session(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def list_sessions(state_dir: str, limit: int = 10) -> list:
    """Newest-first list of recent sessions (full records)."""
    paths = _session_paths(state_dir)
    recent = list(reversed(paths))[:limit]
    return [load_session(p) for p in recent]


def latest_session(state_dir: str) -> "dict | None":
    paths = _session_paths(state_dir)
    return load_session(paths[-1]) if paths else None
