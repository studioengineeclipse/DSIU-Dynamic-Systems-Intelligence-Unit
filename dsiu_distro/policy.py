"""Distro policy — Law 0 for the distribution scaffold.

The scaffold describes a distribution that could be built later; it must never claim
one has been built, booted, or installed.
"""

from __future__ import annotations

from . import DRAFT_STAMP

FORBIDDEN_CLAIMS = (
    "bootable", "iso built", "image built", "distro ready", "distribution ready",
    "installed", "kernel built", "os complete", "app executed", "system fixed",
    "upgrade complete", "production-ready",
)

ALLOWED_WORDING = (
    "distribution scaffold", "package plan", "boot topology", "image plan",
    "build stage", "planned target", "operating environment map", "DRAFT",
    "requires validation", "no execution performed", "no image built",
)

POLICY_BOUNDARIES = [
    "Law 0: every artifact is DRAFT until human-verified.",
    "no execution performed — nothing is built, installed, or booted.",
    "no image produced — target formats are planned, not emitted.",
    "read-only: describes distribution components; runs no package manager.",
    "requires validation before any build is attempted.",
]


def has_draft_stamp(artifact) -> bool:
    if isinstance(artifact, dict):
        return DRAFT_STAMP in str(artifact.get("status", ""))
    return DRAFT_STAMP in str(artifact)


def enforce_draft(**artifacts) -> list:
    return [name for name, art in artifacts.items() if not has_draft_stamp(art)]
