"""OS-Seed policy — Law 0 for the control plane.

The seed describes a future OS; it must never claim one exists.
"""

from __future__ import annotations

from . import DRAFT_STAMP

FORBIDDEN_CLAIMS = (
    "os complete", "bootable", "installed", "kernel built", "desktop ready",
    "app executed", "system fixed", "upgrade complete", "production-ready",
    "os-ready",
)

ALLOWED_WORDING = (
    "OS seed", "scaffold", "readiness candidate", "operating environment map",
    "future OS role", "DRAFT", "requires validation", "no execution performed",
)


def has_draft_stamp(artifact) -> bool:
    if isinstance(artifact, dict):
        return DRAFT_STAMP in str(artifact.get("status", ""))
    return DRAFT_STAMP in str(artifact)


def enforce_draft(**artifacts) -> list:
    return [name for name, art in artifacts.items() if not has_draft_stamp(art)]
