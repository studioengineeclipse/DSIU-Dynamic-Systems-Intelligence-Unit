"""Dashboard — assemble the DRAFT desktop dashboard artifact from the panels."""

from __future__ import annotations

from datetime import date

from . import DESKTOP_STATE_DIR, DRAFT_STAMP
from . import panels as P
from . import workspace as _workspace
from .policy import POLICY_BOUNDARIES


def _roadmap() -> list:
    from dsiu_os_seed import ROADMAP
    return [{"phase": k, "description": d, "state": s} for k, d, s in ROADMAP]


def _next_action(workspaces: list, shell: dict, daemon: dict) -> str:
    if not workspaces:
        return ("No workspaces registered. Run `workspace add <path>` to start "
                "organizing the environment. No execution performed.")
    if not shell.get("present") and not daemon.get("present"):
        return ("Workspaces registered but no analysis/observation on record. Use the "
                "Shell (`inspect`/`analyze`) or Daemon (`once`) yourself, then refresh "
                "the dashboard. Requires validation.")
    return ("Review the latest session/event below. Next phase candidate: DSIU Linux "
            "distribution environment (requires validation).")


def build_dashboard(desktop_state_dir: str = DESKTOP_STATE_DIR,
                    shell_state_dir: "str | None" = None,
                    daemon_state_dir: "str | None" = None) -> dict:
    workspaces = _workspace.list_workspaces(desktop_state_dir)
    shell = P.latest_shell_summary(shell_state_dir)
    daemon = P.latest_daemon_summary(daemon_state_dir)

    return {
        "schema": "dsiu.desktop_dashboard/v0.1",
        "status": f"{DRAFT_STAMP} — operating environment surface, not a desktop/OS (Law 0)",
        "date": date.today().isoformat(),
        "organs_summary": P.organs_summary(),
        "os_seed_status": P.os_seed_status(),
        "registered_workspaces": workspaces,
        "latest_shell_session_summary": shell,
        "latest_daemon_event_summary": daemon,
        "compatibility_summary": P.compatibility_summary(shell_state_dir, daemon_state_dir),
        "readiness_summary": P.readiness_summary(),
        "roadmap": _roadmap(),
        "policy_boundaries": POLICY_BOUNDARIES,
        "next_recommended_action": _next_action(workspaces, shell, daemon),
        "no_execution_performed": True,
    }
