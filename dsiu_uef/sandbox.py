"""Sandbox planner — recommend an isolation posture and a permission-risk level.

A *plan*, not an enforcement. v0.1 recommends; it does not create sandboxes or
grant permissions. Risk is a candidate assessment, not a verdict.
"""

from __future__ import annotations

from . import lanes as L

# detected_type -> (permission_risk, reason)
_RISK = {
    L.WINDOWS_EXECUTABLE: ("high", "opaque foreign binary; full Win32 surface"),
    L.VM_IMAGE: ("high", "entire guest OS; broad device/disk access"),
    L.ANDROID_PACKAGE: ("medium", "mobile app; sensors/network/storage perms"),
    L.STEAM_GAME: ("medium", "large game runtime; GPU + network + anti-cheat"),
    L.DOCKER_PROJECT: ("medium", "container build may pull and run arbitrary layers"),
    L.APPIMAGE_FLATPAK: ("medium", "bundled Linux app; portal/permission scoped"),
    L.LINUX_BINARY: ("medium", "native binary; userland access"),
    L.WEB_APP: ("low", "browser-sandboxable; network the main surface"),
    L.LINUX_SCRIPT: ("low", "inspectable text; still runs shell commands"),
    L.DSIU_NATIVE: ("low", "DSIU-native artifact; runs in the DSIU runtime"),
    L.UNKNOWN: ("high", "unidentified workload; treat as untrusted by default"),
}

_RECO = {
    "high": ("isolated VM or rootless container; no host filesystem mounts; network "
             "off by default; explicit per-resource grants required."),
    "medium": ("rootless container or portal-scoped sandbox; least-privilege "
               "filesystem; network allow-list."),
    "low": ("standard sandbox; scoped working directory; network allow-list."),
}


def assess(detected_type: str, signals: dict):
    """Return (permission_risk, sandbox_recommendation)."""
    risk, reason = _RISK.get(detected_type, ("high", "unclassified"))
    recommendation = f"{_RECO[risk]} (reason: {reason})"
    return risk, recommendation
