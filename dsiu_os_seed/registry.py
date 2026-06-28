"""Registry — the canonical, read-only description of the five DSIU organs.

Single source of truth for the manifest / topology / readiness layers. Versions are
resolved by importing each organ module and reading its version constant (no values
duplicated here where a constant already exists). Importing reads metadata only — no
organ command is ever run.
"""

from __future__ import annotations

import importlib
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Each organ: how to find it, what it contributes, and its boundaries.
ORGANS = [
    {
        "name": "skill",
        "title": "DSIU Skill",
        "purpose": "Executable doctrine + analysis engine (the lens).",
        "kind": "bundle",                       # not an importable package
        "detect_path": "dsiu/SKILL.md",
        "command_surface": "dsiu/scripts/dsiu_analyze.py",
        "cli_entrypoint": "python dsiu/scripts/dsiu_analyze.py",
        "version_module": None,
        "version_attr": None,
        "state_dir": None,
        "test_file": "tests/test_dsiu_analyze.py",
        "capabilities": ["doctrine", "scan", "scorecard", "packet", "diff"],
        "execution_boundary": "analysis only; emits DRAFT artifacts, runs nothing",
        "policy_constraints": ["Law 0: heuristic output is DRAFT until verified"],
        "future_os_role": "the OS's reasoning/doctrine core",
    },
    {
        "name": "oil",
        "title": "DSIU-OIL",
        "purpose": "Operating intelligence loop (the brain).",
        "kind": "package",
        "detect_path": "dsiu_runtime/__init__.py",
        "command_surface": "dsiu_runtime/__main__.py",
        "cli_entrypoint": "python -m dsiu_runtime loop",
        "version_module": "dsiu_runtime",
        "version_attr": "OIL_VERSION",
        "state_dir": "dsiu_state",
        "test_file": "tests/test_dsiu_runtime.py",
        "capabilities": ["loop", "process graph", "supervisor report",
                         "state feedback", "diff / movement"],
        "execution_boundary": "dry-run only; movement measured, improvement never claimed",
        "policy_constraints": ["Law 0", "no silent upgrades", "movement != improvement"],
        "future_os_role": "the OS's operating/decision loop",
    },
    {
        "name": "uef",
        "title": "DSIU-UEF",
        "purpose": "Compatibility intelligence (the compatibility sense).",
        "kind": "package",
        "detect_path": "dsiu_uef/__init__.py",
        "command_surface": "dsiu_uef/__main__.py",
        "cli_entrypoint": "python -m dsiu_uef intake",
        "version_module": "dsiu_uef",
        "version_attr": "UEF_VERSION",
        "state_dir": None,
        "test_file": "tests/test_dsiu_uef.py",
        "capabilities": ["workload classification", "lane routing",
                         "sandbox recommendation", "compatibility profile"],
        "execution_boundary": "classification only; never executes a workload",
        "policy_constraints": ["Law 0", "no 'supported' claim without execution"],
        "future_os_role": "the OS's run-anything compatibility layer",
    },
    {
        "name": "shell",
        "title": "DSIU-Shell",
        "purpose": "User-facing command cockpit over OIL + UEF.",
        "kind": "package",
        "detect_path": "dsiu_shell/__init__.py",
        "command_surface": "dsiu_shell/__main__.py",
        "cli_entrypoint": "python -m dsiu_shell inspect",
        "version_module": "dsiu_shell",
        "version_attr": "SHELL_VERSION",
        "state_dir": "dsiu_shell_state",
        "test_file": "tests/test_dsiu_shell.py",
        "capabilities": ["inspect", "profile", "analyze", "status", "history",
                         "explain"],
        "execution_boundary": "routes/renders/records; executes nothing",
        "policy_constraints": ["Law 0", "thin layer", "no execution"],
        "future_os_role": "the OS's command/control surface",
    },
    {
        "name": "daemon",
        "title": "DSIU-Daemon",
        "purpose": "Continuous observation layer (the watcher).",
        "kind": "package",
        "detect_path": "dsiu_daemon/__init__.py",
        "command_surface": "dsiu_daemon/__main__.py",
        "cli_entrypoint": "python -m dsiu_daemon watch",
        "version_module": "dsiu_daemon",
        "version_attr": "DAEMON_VERSION",
        "state_dir": "dsiu_daemon_state",
        "test_file": "tests/test_dsiu_daemon.py",
        "capabilities": ["once", "watch", "event history", "change detection"],
        "execution_boundary": "observe-and-report only; foreground; no fixes, no service",
        "policy_constraints": ["Law 0", "movement != improvement", "no execution"],
        "future_os_role": "the OS's continuous supervision layer",
    },
]


def resolve_version(organ: dict) -> str:
    """Read an organ's version constant via import (metadata only). Skill (a bundle,
    not a module) is read from its SKILL.md presence."""
    if organ["version_module"] is None:
        skill = os.path.join(REPO_ROOT, organ.get("detect_path", ""))
        return "bundled skill (v1)" if os.path.isfile(skill) else "unknown"
    try:
        mod = importlib.import_module(organ["version_module"])
        return str(getattr(mod, organ["version_attr"], "unknown"))
    except Exception:
        return "unimportable"


def organ_by_name(name: str) -> "dict | None":
    for o in ORGANS:
        if o["name"] == name:
            return o
    return None
