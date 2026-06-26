"""State directory — the v0.1 feedback memory.

Saves each pass's scorecard under `dsiu_state/<slug>/scan-<UTC>.json` so later
passes can be diffed against earlier ones. This *is* the feedback memory for v0.1
(a richer `dsiu_memory` is a later phase).

Correction hard-lock (movement must be real, not self-compared):
the operating loop loads the previous state **before** it saves the current one,
and `previous_state()` returns the latest *existing* snapshot. So when called
before the save it returns the true prior pass — the system can never diff a scan
against itself and fake a feedback loop.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone


def slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (name or "system").lower()).strip("-")
    return s or "system"


def state_subdir(state_dir: str, name: str) -> str:
    return os.path.join(state_dir, slug(name))


def _snapshots(state_dir: str, name: str) -> list:
    sub = state_subdir(state_dir, name)
    if not os.path.isdir(sub):
        return []
    files = [f for f in os.listdir(sub)
             if f.startswith("scan-") and f.endswith(".json")]
    return [os.path.join(sub, f) for f in sorted(files)]  # lexical == chronological


def latest_state_path(state_dir: str, name: str) -> "str | None":
    snaps = _snapshots(state_dir, name)
    return snaps[-1] if snaps else None


def load_state(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def previous_state(state_dir: str, name: str) -> "dict | None":
    """The latest existing snapshot. Call this BEFORE save_state() so it returns
    the true prior pass (never the current one)."""
    path = latest_state_path(state_dir, name)
    return load_state(path) if path else None


def save_state(state_dir: str, name: str, scorecard: dict) -> str:
    sub = state_subdir(state_dir, name)
    os.makedirs(sub, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S-%f")
    path = os.path.join(sub, f"scan-{ts}Z.json")
    # uniqueness guard if two saves land in the same microsecond (e.g. tests)
    n = 1
    while os.path.exists(path):
        path = os.path.join(sub, f"scan-{ts}-{n}Z.json")
        n += 1
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(scorecard, fh, indent=2)
    return path
