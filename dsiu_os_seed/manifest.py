"""Manifest — the DSIU system manifest (control-plane description)."""

from __future__ import annotations

from datetime import date

from . import DRAFT_STAMP
from .registry import ORGANS, resolve_version


def build_manifest() -> dict:
    organs = []
    for o in ORGANS:
        organs.append({
            "name": o["name"],
            "title": o["title"],
            "version": resolve_version(o),
            "purpose": o["purpose"],
            "import_path": o["version_module"] or o["detect_path"],
            "cli_entrypoint": o["cli_entrypoint"],
            "state_directory": o["state_dir"],
            "capabilities": o["capabilities"],
            "execution_boundary": o["execution_boundary"],
            "policy_constraints": o["policy_constraints"],
            "future_os_role": o["future_os_role"],
        })
    return {
        "schema": "dsiu.os_seed_manifest/v0.1",
        "status": f"{DRAFT_STAMP} — operating-environment map, not an OS (Law 0)",
        "date": date.today().isoformat(),
        "organs": organs,
        "current_phase": "linux_distribution",
        "next_phase": "native_os",
        "future_os_role": ("a process-intelligence operating environment where every "
                           "workload is observed, mapped, classified, supervised, and "
                           "given a best-available execution lane — built much later, "
                           "only once each layer is stable"),
        "execution_boundary": ("read-only scaffold; no boot, install, execution, or "
                               "host-OS replacement"),
    }
