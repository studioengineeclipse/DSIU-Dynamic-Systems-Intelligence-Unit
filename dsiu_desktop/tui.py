"""TUI — the DSIU-Desktop text-UI dashboard (v0.2).

The first actual *interface* surface over DSIU: a bordered, full-screen text frame
rendered from the existing read-only ``build_dashboard()`` state. It is still not a
GUI, and it does NOT watch: a frame is a *snapshot* of live state at invocation time.

`render_tui_frame` is a pure function (frame in, string out) and is the unit-tested
core. `run_interactive` is an optional, user-driven viewer: it redraws only on an
explicit keypress (`r` to refresh, `q`/EOF to quit) — no timers, no threads, no watch
loop — so it stays inside the Desktop Layer's "no execution / no watching" boundary.
Screen clearing uses a plain ANSI escape string; nothing is shelled out.
"""

from __future__ import annotations

from . import DRAFT_STAMP
from .dashboard import build_dashboard

_CLEAR = "\x1b[2J\x1b[H"  # ANSI: clear screen + home cursor (a string, not a command)
_MARK = {"done": "done", "current": "current", "future": "future"}


def _clip(text: str, width: int) -> str:
    text = text.replace("\n", " ")
    return text if len(text) <= width else text[: max(0, width - 1)] + "…"


def _row(text: str, width: int) -> str:
    inner = width - 4  # "│ " + " │"
    return f"│ {_clip(text, inner):<{inner}} │"


def _rule(width: int, left: str = "├", right: str = "┤") -> str:
    return f"{left}{'─' * (width - 2)}{right}"


def _section(title: str, lines: list, width: int) -> list:
    out = [_rule(width), _row(title, width)]
    out += [_row("  " + ln, width) for ln in (lines or ["(none)"])]
    return out


def _shell_line(s: dict) -> str:
    if not s.get("present"):
        return "(none yet)"
    ms = s.get("movement_score")
    lane = s.get("primary_execution_lane")
    return (f"{s.get('command')} on {s.get('target')}"
            + (f" · movement {ms} (direction unverified)" if ms is not None else "")
            + (f" · lane {lane}" if lane else ""))


def _daemon_line(d: dict) -> str:
    if not d.get("present"):
        return "(none yet)"
    return f"{d.get('event_type')} · {d.get('change_summary')}"


def _compat_line(c: dict) -> str:
    if not c.get("present"):
        return "(none yet)"
    return (f"{c.get('workload')} → {c.get('primary_execution_lane')} "
            f"(risk {c.get('permission_risk')})")


def render_tui_frame(dash: dict, width: int = 80) -> str:
    """Render the dashboard dict as a bordered, full-screen text frame (a snapshot)."""
    width = max(48, int(width))
    org = dash["organs_summary"]
    osd = dash["os_seed_status"]
    ws = dash["registered_workspaces"]
    phase = next((p for p in dash["roadmap"] if p["state"] == "current"), None)

    top = f"┌{'─' * (width - 2)}┐"
    bottom = f"└{'─' * (width - 2)}┘"

    lines = [top]
    lines.append(_row(f"DSIU DESKTOP · text UI · {DRAFT_STAMP}", width))
    lines.append(_row(dash["status"], width))

    lines += _section(
        f"ORGANS ({org['count']})",
        [", ".join(f"{o['name']}({o['version']})" for o in org["organs"])],
        width)

    lines += _section("ROADMAP PHASE", [
        (f"{phase['phase']} ({phase['description']})" if phase else "(none current)"),
        "path: " + " → ".join(
            f"{p['phase']}[{_MARK[p['state']]}]" for p in dash["roadmap"]),
    ], width)

    lines += _section("OS-SEED READINESS", [
        osd["os_readiness_level"],
        "detected: " + ", ".join(osd["organs_detected"]),
    ], width)

    lines += _section("REPORTS", [
        "shell:    " + _shell_line(dash["latest_shell_session_summary"]),
        "daemon:   " + _daemon_line(dash["latest_daemon_event_summary"]),
        "compat:   " + _compat_line(dash["compatibility_summary"]),
    ], width)

    lines += _section(
        f"WORKSPACES ({len(ws)})",
        [f"{w['name']}: {w['path']}" for w in ws] if ws else ["(none registered)"],
        width)

    lines += _section("NEXT ACTION", [dash["next_recommended_action"]], width)

    lines.append(_rule(width))
    lines.append(_row(f"Law 0: enforced — {DRAFT_STAMP}; no execution performed.", width))
    lines.append(bottom)
    return "\n".join(lines) + "\n"


def run_interactive(state_dir=None, width: int = 80) -> int:
    """User-driven viewer: redraw a fresh snapshot only on an explicit keypress.

    Not a watch loop — it advances only when the user presses a key: `r` rebuilds
    and redraws the frame, `q` (or EOF) quits. No timers, threads, or background polling.
    """
    from . import DESKTOP_STATE_DIR
    state_dir = state_dir or DESKTOP_STATE_DIR
    while True:
        frame = render_tui_frame(build_dashboard(state_dir), width=width)
        print(_CLEAR + frame + "\n[r] refresh   [q] quit")
        try:
            choice = input("> ").strip().lower()
        except EOFError:
            return 0
        if choice in ("q", "quit", "exit"):
            return 0
        # any other key (including "r") falls through and redraws a fresh snapshot
