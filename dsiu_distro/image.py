"""Image — the DSIU-Distro image build plan (described, not built).

The build stages and target formats a DSIU distribution image *would* go through. No
image is produced: every target is marked `planned`, and `no_image_built` is always
true.
"""

from __future__ import annotations

from datetime import date

from . import DRAFT_STAMP

# Ordered build stages — a description of the intended pipeline, executed by nothing.
BUILD_STAGES = [
    {"order": 1, "stage": "bootstrap-base",
     "role": "assemble a minimal base root filesystem"},
    {"order": 2, "stage": "install-runtime",
     "role": "add the standard-library Python runtime"},
    {"order": 3, "stage": "vendor-organs",
     "role": "vendor the DSIU organs as distribution components"},
    {"order": 4, "stage": "register-services",
     "role": "register organ services + the Shell login / Desktop-TUI surface"},
    {"order": 5, "stage": "compose-image",
     "role": "compose the target image (planned — not emitted)"},
    {"order": 6, "stage": "verify-image",
     "role": "verification pass a human would run before trusting the image"},
]

# Target formats a build could emit — all planned, none produced.
IMAGE_TARGETS = [
    {"format": "iso", "role": "installable / live boot media", "status": "planned"},
    {"format": "qcow2", "role": "VM disk image", "status": "planned"},
    {"format": "raw", "role": "raw block-device image", "status": "planned"},
]


def build_image_plan() -> dict:
    return {
        "schema": "dsiu.distro_image/v0.1",
        "status": f"{DRAFT_STAMP} — planned image build; no image is built (Law 0)",
        "date": date.today().isoformat(),
        "build_stages": BUILD_STAGES,
        "stage_count": len(BUILD_STAGES),
        "targets": IMAGE_TARGETS,
        "target_formats": [t["format"] for t in IMAGE_TARGETS],
        "all_targets_planned": all(t["status"] == "planned" for t in IMAGE_TARGETS),
        "no_image_built": True,
    }
