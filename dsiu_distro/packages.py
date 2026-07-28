"""Packages — the DSIU-Distro component/package set (described, not installed).

The five DSIU organs are described *as* distribution components by reusing the OS-Seed
registry (single source of truth — not re-listed here), alongside the base-system
components a minimal Linux distribution would need to host them. Nothing is fetched,
installed, or run: this is a plan.
"""

from __future__ import annotations

from datetime import date

from dsiu_os_seed.registry import ORGANS

from . import DRAFT_STAMP

# Base-system components a DSIU distribution would layer the organs on top of. These
# are described as planned components, with no version pinned and nothing installed.
BASE_COMPONENTS = [
    {
        "name": "linux-kernel",
        "category": "base",
        "role": "host kernel (distribution-provided; choice deferred)",
        "provides": ["process/memory/device management"],
        "status": "planned",
    },
    {
        "name": "init-system",
        "category": "base",
        "role": "PID 1 / service supervisor that would start the DSIU organs",
        "provides": ["boot sequencing", "service lifecycle"],
        "status": "planned",
    },
    {
        "name": "python3-runtime",
        "category": "runtime",
        "role": "standard-library Python runtime the organs run on (no third-party deps)",
        "provides": ["dsiu organ execution environment"],
        "status": "planned",
    },
    {
        "name": "dsiu-shell-login",
        "category": "surface",
        "role": "DSIU-Shell as the default login/command surface",
        "provides": ["cockpit login"],
        "status": "planned",
    },
    {
        "name": "dsiu-desktop-tui",
        "category": "surface",
        "role": "DSIU-Desktop text-UI dashboard as the default operator view",
        "provides": ["operating environment surface"],
        "status": "planned",
    },
]


def _organ_component(o: dict) -> dict:
    """Describe one DSIU organ as a distribution component/service."""
    return {
        "name": f"dsiu-{o['name']}",
        "category": "organ",
        "organ": o["name"],
        "title": o["title"],
        "role": o["purpose"],
        "service_kind": "system-service" if o["state_dir"] else "on-demand-tool",
        "cli_entrypoint": o["cli_entrypoint"],
        "state_directory": o["state_dir"],
        "capabilities": o["capabilities"],
        "execution_boundary": o["execution_boundary"],
        "distro_role": o["future_os_role"],
        "status": "planned",
    }


def build_package_set() -> dict:
    organ_components = [_organ_component(o) for o in ORGANS]
    components = BASE_COMPONENTS + organ_components
    return {
        "schema": "dsiu.distro_packages/v0.1",
        "status": f"{DRAFT_STAMP} — planned component/package set; nothing installed "
                  "or built (Law 0)",
        "date": date.today().isoformat(),
        "base_components": BASE_COMPONENTS,
        "organ_components": organ_components,
        "components": components,
        "component_count": len(components),
        "organ_count": len(organ_components),
        "no_build_performed": True,
        "no_packages_installed": True,
    }
