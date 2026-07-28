"""Boot — the DSIU-Distro boot topology (described, not booted).

The ordered layer stack a DSIU distribution would boot through, from firmware to the
DSIU operator surface. This is a description of intended sequencing; it boots nothing.
"""

from __future__ import annotations

from datetime import date

from . import DRAFT_STAMP

# Ordered stack from lowest layer to the operator surface. Each stage names the DSIU
# component(s) that would activate there (reusing the package-set component names).
BOOT_STAGES = [
    {"order": 1, "layer": "firmware", "role": "hand off to bootloader",
     "dsiu_component": None},
    {"order": 2, "layer": "bootloader", "role": "load the kernel",
     "dsiu_component": "linux-kernel"},
    {"order": 3, "layer": "kernel", "role": "bring up hardware + hand off to init",
     "dsiu_component": "linux-kernel"},
    {"order": 4, "layer": "init", "role": "supervise services / sequence boot",
     "dsiu_component": "init-system"},
    {"order": 5, "layer": "runtime", "role": "start the Python runtime the organs use",
     "dsiu_component": "python3-runtime"},
    {"order": 6, "layer": "organs", "role": "start DSIU organs as services",
     "dsiu_component": "dsiu-oil / dsiu-uef / dsiu-shell / dsiu-daemon"},
    {"order": 7, "layer": "login", "role": "present the DSIU-Shell command cockpit",
     "dsiu_component": "dsiu-shell-login"},
    {"order": 8, "layer": "surface", "role": "present the DSIU-Desktop text-UI dashboard",
     "dsiu_component": "dsiu-desktop-tui"},
]


def build_boot_topology() -> dict:
    return {
        "schema": "dsiu.distro_boot/v0.1",
        "status": f"{DRAFT_STAMP} — planned boot topology; nothing is booted (Law 0)",
        "date": date.today().isoformat(),
        "stages": BOOT_STAGES,
        "stage_count": len(BOOT_STAGES),
        "layer_order": [s["layer"] for s in BOOT_STAGES],
        "operator_surface": "dsiu-desktop-tui",
        "no_boot_performed": True,
    }
