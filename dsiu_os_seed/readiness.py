"""Readiness — read-only introspection of the operating environment.

Imports organ modules (metadata only) and checks file existence. It NEVER runs an
organ command, a test, the build script, or any subprocess. It reports what is
*detected*, not what is *validated by execution*. It never claims the OS is "ready".
"""

from __future__ import annotations

import importlib
import os
from datetime import date

from . import DRAFT_STAMP
from .registry import ORGANS, REPO_ROOT


def _exists(rel: str) -> bool:
    return os.path.exists(os.path.join(REPO_ROOT, rel))


def _detected(organ: dict) -> bool:
    if organ["kind"] == "package":
        try:
            importlib.import_module(organ["version_module"])
            return True
        except Exception:
            return False
    return _exists(organ["detect_path"])  # skill bundle: detect by file


def build_readiness() -> dict:
    organs_detected, missing = [], []
    command_surfaces, tests, state_dirs = [], [], []

    for o in ORGANS:
        (organs_detected if _detected(o) else missing).append(o["name"])
        if _exists(o["command_surface"]):
            command_surfaces.append(o["name"])
        if _exists(o["test_file"]):
            tests.append(o["name"])
        if o["state_dir"]:
            state_dirs.append({
                "organ": o["name"],
                "dir": o["state_dir"],
                # state dirs are KNOWN from the registry even if not yet created
                # (runtime dirs are made on use — absence != missing organ).
                "known": True,
                "present": _exists(o["state_dir"]),
            })

    policy_declared = all(o.get("execution_boundary") and o.get("policy_constraints")
                          for o in ORGANS)
    build_present = _exists("scripts/build_skill.py")

    full = (not missing
            and len(command_surfaces) == len(ORGANS)
            and len(tests) == len(ORGANS)
            and policy_declared and build_present)
    # DRAFT scaffold labels only — never "ready" / "complete" / "production-ready".
    level = "seed-scaffold-complete (candidate)" if full else "seed-scaffold (partial)"

    return {
        "schema": "dsiu.os_seed_readiness/v0.1",
        "status": f"{DRAFT_STAMP} — readiness candidate; detected, not validated by "
                  "execution (Law 0)",
        "date": date.today().isoformat(),
        "organs_detected": organs_detected,
        "missing_organs": missing,
        "command_surfaces_detected": command_surfaces,
        "policy_boundaries_declared": policy_declared,
        "state_dirs_known": True,
        "state_dirs": state_dirs,
        "tests_detected": tests,
        "build_skill_present": build_present,
        "os_readiness_level": level,
        "next_required_action": (
            "Scaffold detected. Next phase candidate: DSIU-Desktop Layer "
            "(requires validation). No execution performed."
        ),
    }
