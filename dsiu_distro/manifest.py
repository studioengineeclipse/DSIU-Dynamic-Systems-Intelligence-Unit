"""Manifest — the DSIU-Distro top-level manifest (spec control plane).

Ties the package set, boot topology, and image plan into one distribution description,
and references the OS-Seed control plane it builds on. It describes a distribution; it
builds nothing.
"""

from __future__ import annotations

from datetime import date

from . import DISTRO_VERSION, DRAFT_STAMP
from .boot import build_boot_topology
from .image import build_image_plan
from .packages import build_package_set


def build_manifest() -> dict:
    packages = build_package_set()
    boot = build_boot_topology()
    image = build_image_plan()
    return {
        "schema": "dsiu.distro_manifest/v0.1",
        "status": f"{DRAFT_STAMP} — distribution scaffold, not a built distro (Law 0)",
        "date": date.today().isoformat(),
        "distro_version": DISTRO_VERSION,
        "built_on": "dsiu_os_seed (operating-environment control plane)",
        "current_phase": "linux_distribution",
        "next_phase": "native_os",
        "components": {
            "count": packages["component_count"],
            "organs": packages["organ_count"],
            "base": len(packages["base_components"]),
        },
        "boot": {
            "stage_count": boot["stage_count"],
            "operator_surface": boot["operator_surface"],
        },
        "image": {
            "target_formats": image["target_formats"],
            "no_image_built": image["no_image_built"],
        },
        "distro_role": ("package the DSIU operating environment as a describable Linux "
                        "distribution — every organ a component, the Shell a login "
                        "surface, the Desktop-TUI the operator view — built much later, "
                        "only once each layer is stable"),
        "execution_boundary": ("read-only scaffold; no build, install, boot, or image "
                               "emission; does not replace the host OS"),
        "no_build_performed": True,
        "no_image_built": True,
    }
