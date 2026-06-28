"""Watch — polling-based change detection (stdlib only, no watchdog dependency).

Fingerprints each file as `mtime_ns:size`, plus a short sha256 for small files so
same-size/same-mtime edits are still caught. Reads file metadata (and small file
bytes for hashing) only — it never executes anything.
"""

from __future__ import annotations

import hashlib
import os

# Noise + DSIU state dirs we never watch.
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    "env", "dist", "build", ".next", ".cache", "vendor", ".idea", ".vscode",
    "coverage", ".pytest_cache", ".mypy_cache", "target",
    "dsiu_state", "dsiu_shell_state", "dsiu_daemon_state",
}

_SMALL_FILE_BYTES = 65536  # hash files up to 64 KiB for stronger fingerprints


def _fingerprint(full: str) -> str:
    st = os.stat(full)
    fp = f"{st.st_mtime_ns}:{st.st_size}"
    if st.st_size <= _SMALL_FILE_BYTES:
        try:
            with open(full, "rb") as fh:
                fp += ":" + hashlib.sha256(fh.read()).hexdigest()[:16]
        except OSError:
            pass
    return fp


def snapshot(path: str) -> dict:
    """Map relpath -> fingerprint for every file under `path`. Raises OSError-style
    errors to the caller (the supervisor turns them into DRAFT error events)."""
    if not os.path.isdir(path):
        raise NotADirectoryError(path)
    snap = {}
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, path)
            try:
                snap[rel] = _fingerprint(full)
            except OSError:
                snap[rel] = "unreadable"
    return snap


def diff(old: "dict | None", new: dict) -> dict:
    old = old or {}
    old_keys, new_keys = set(old), set(new)
    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    modified = sorted(k for k in (old_keys & new_keys) if old[k] != new[k])
    changed_files = sorted(added + removed + modified)
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "changed_files": changed_files,
    }
