"""Intake — gather raw compatibility signals from a path.

Reads metadata and at most the first few bytes of a file (magic number). For a
directory it inventories well-known manifest filenames. It NEVER executes the
workload, imports it, installs anything, or runs a subprocess.
"""

from __future__ import annotations

import os

# Magic numbers (first bytes) — enough to tell broad categories apart.
_MAGIC = {
    b"MZ": "pe",            # Windows PE (.exe/.dll/.msi often)
    b"\x7fELF": "elf",      # Linux ELF binary
    b"#!": "script",        # shebang script
    b"PK\x03\x04": "zip",   # zip container (apk/jar/appimage payloads, etc.)
}

_VM_EXTS = {".iso", ".qcow2", ".vmdk", ".ova", ".vdi"}
_ARCH_HINTS = {
    "x86_64": "x86_64", "amd64": "x86_64", "x64": "x86_64",
    "arm64": "arm64", "aarch64": "arm64", "armv7": "arm32", "i386": "x86_32",
}


def _read_magic(path: str) -> str:
    try:
        with open(path, "rb") as fh:
            head = fh.read(8)
    except OSError:
        return "unreadable"
    for sig, label in _MAGIC.items():
        if head.startswith(sig):
            return label
    return "binary" if b"\x00" in head else "text"


def _arch_signal(name: str) -> str:
    low = name.lower()
    for hint, arch in _ARCH_HINTS.items():
        if hint in low:
            return arch
    return "unknown"


def _scan_dir(path: str) -> dict:
    """Inventory well-known manifests in a directory (non-recursive + one level)."""
    found = {
        "dockerfile": False, "compose": False, "package_json": False,
        "android_manifest": False, "apk": False, "steam_manifest": False,
        "appimage": False, "flatpak": False, "skill_md": False,
        "elf_or_exe": False,
    }
    try:
        entries = os.listdir(path)
    except OSError:
        return found
    for e in entries:
        low = e.lower()
        if low == "dockerfile":
            found["dockerfile"] = True
        elif low in ("docker-compose.yml", "docker-compose.yaml", "compose.yml",
                     "compose.yaml"):
            found["compose"] = True
        elif low == "package.json":
            found["package_json"] = True
        elif low == "androidmanifest.xml":
            found["android_manifest"] = True
        elif low.endswith(".apk"):
            found["apk"] = True
        elif low.startswith("appmanifest_") and low.endswith(".acf"):
            found["steam_manifest"] = True
        elif low == "steamapps":
            found["steam_manifest"] = True
        elif low.endswith(".appimage"):
            found["appimage"] = True
        elif low.endswith(".flatpakref") or low == "flatpak":
            found["flatpak"] = True
        elif low == "skill.md":
            found["skill_md"] = True
    return found


def gather(path: str) -> dict:
    """Return a dict of raw signals for classification."""
    workload_path = os.path.abspath(path)
    name = os.path.basename(workload_path.rstrip(os.sep)) or workload_path
    exists = os.path.exists(workload_path)
    is_dir = os.path.isdir(workload_path)
    ext = "" if is_dir else os.path.splitext(name)[1].lower()

    signals = {
        "workload_name": name,
        "workload_path": workload_path,
        "exists": exists,
        "is_dir": is_dir,
        "extension": ext,
        "magic": None,
        "manifests": {},
        "cpu_architecture_signal": _arch_signal(name),
    }

    if exists and is_dir:
        signals["manifests"] = _scan_dir(workload_path)
    elif exists:
        signals["magic"] = _read_magic(workload_path)
    else:
        # name-only workload (e.g. a binary name) — classify by extension alone.
        signals["magic"] = None

    return signals
