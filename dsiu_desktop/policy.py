"""Desktop Law-0 policy — the surface describes; it never claims a desktop/OS exists."""

from __future__ import annotations

from . import DRAFT_STAMP

FORBIDDEN_CLAIMS = (
    "desktop ready", "os complete", "bootable", "installed", "app executed",
    "system fixed", "upgrade complete", "production-ready",
)

ALLOWED_WORDING = (
    "desktop scaffold", "workspace layer", "dashboard candidate",
    "operating environment surface", "no execution performed", "requires validation",
    "DRAFT",
)

POLICY_BOUNDARIES = [
    "Law 0: every artifact is DRAFT until human-verified.",
    "no execution performed — the desktop runs nothing.",
    "movement measured != improvement.",
    "read-only against organs; writes only its own desktop state.",
    "requires validation before any action is taken.",
]


def has_draft_stamp(artifact) -> bool:
    if isinstance(artifact, dict):
        return DRAFT_STAMP in str(artifact.get("status", ""))
    return DRAFT_STAMP in str(artifact)


def enforce_draft(**artifacts) -> list:
    return [name for name, art in artifacts.items() if not has_draft_stamp(art)]
