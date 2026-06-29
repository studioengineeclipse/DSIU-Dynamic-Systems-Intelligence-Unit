"""Panels — read-only summarizers of the existing organs' state.

Each summarizer reads either an OS-Seed pure function (metadata only) or the latest
saved Shell/Daemon state. None of them run an organ command. All are empty-state safe.
"""

from __future__ import annotations


def organs_summary() -> dict:
    from dsiu_os_seed.manifest import build_manifest
    m = build_manifest()
    return {
        "count": len(m["organs"]),
        "organs": [{"name": o["name"], "version": o["version"],
                    "capabilities": o["capabilities"]} for o in m["organs"]],
    }


def os_seed_status() -> dict:
    from dsiu_os_seed.readiness import build_readiness
    r = build_readiness()
    return {
        "os_readiness_level": r["os_readiness_level"],
        "organs_detected": r["organs_detected"],
        "missing_organs": r["missing_organs"],
        "build_skill_present": r["build_skill_present"],
    }


def readiness_summary() -> dict:
    return os_seed_status()


def latest_shell_summary(shell_state_dir: "str | None" = None) -> dict:
    from dsiu_shell import SHELL_STATE_DIR
    from dsiu_shell.history import latest_session
    sess = latest_session(shell_state_dir or SHELL_STATE_DIR)
    if not sess:
        return {"present": False, "note": "(none yet)"}
    q = sess.get("quick_status", {})
    return {
        "present": True,
        "command": sess.get("command"),
        "target": sess.get("target"),
        "movement_score": q.get("movement_score"),
        "primary_execution_lane": q.get("primary_execution_lane"),
        "required_next_action": sess.get("required_next_action"),
    }


def latest_daemon_summary(daemon_state_dir: "str | None" = None) -> dict:
    from dsiu_daemon import DAEMON_STATE_DIR
    from dsiu_daemon.events import latest_event
    ev = latest_event(daemon_state_dir or DAEMON_STATE_DIR)
    if not ev:
        return {"present": False, "note": "(none yet)"}
    return {
        "present": True,
        "event_type": ev.get("event_type"),
        "watched_path": ev.get("watched_path"),
        "change_summary": ev.get("change_summary"),
        "movement_score": ev.get("movement_score"),
    }


def compatibility_summary(shell_state_dir: "str | None" = None,
                          daemon_state_dir: "str | None" = None) -> dict:
    """UEF lane/risk from the latest shell session or daemon event, if any."""
    from dsiu_daemon import DAEMON_STATE_DIR
    from dsiu_daemon.events import latest_event
    from dsiu_shell import SHELL_STATE_DIR
    from dsiu_shell.history import latest_session

    sess = latest_session(shell_state_dir or SHELL_STATE_DIR)
    uef = sess.get("uef_profile") if sess else None
    if not uef:
        ev = latest_event(daemon_state_dir or DAEMON_STATE_DIR)
        uef = ev.get("uef_profile") if ev else None
    if not uef:
        return {"present": False, "note": "(none yet)"}
    return {
        "present": True,
        "workload": uef.get("workload_name"),
        "detected_type": uef.get("detected_type"),
        "primary_execution_lane": uef.get("primary_execution_lane"),
        "fallback_execution_lanes": uef.get("fallback_execution_lanes"),
        "permission_risk": uef.get("permission_risk"),
    }
