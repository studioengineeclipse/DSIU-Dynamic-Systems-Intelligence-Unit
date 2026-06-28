"""Render — clean Markdown for shell output.

Thin: reuses the organ renderers (OIL `render_report_md`, UEF `render_profile_md`)
for deep sections instead of re-deriving them. Every output carries a DRAFT banner
and the hard-boundary note.
"""

from __future__ import annotations

from . import DRAFT_STAMP, EMPTY_STATE_MESSAGE, SHELL_VERSION

_BOUNDARY = ("_Hard boundary: DSIU-Shell routes, renders, and records. "
             "No execution performed; no apps run, no dependencies installed._")


def _banner(title: str) -> str:
    return (f"# {title}\n\n> {SHELL_VERSION}  ·  {DRAFT_STAMP}\n"
            f"> {_BOUNDARY}\n")


def render_command_report(session: dict) -> str:
    parts = [_banner(f"DSIU-Shell — {session['command']}")]
    parts.append(f"**Command:** `{session['command']}`")
    parts.append(f"**Target:** `{session['target']}`\n")

    oil = session.get("oil_report")
    if oil:
        from dsiu_runtime.supervisor import render_report_md
        parts.append("## OIL operating-loop report\n")
        parts.append(render_report_md(oil))

    uef = session.get("uef_profile")
    if uef:
        from dsiu_uef.report import render_profile_md
        parts.append("## UEF compatibility profile\n")
        parts.append(render_profile_md(uef))

    parts.append("## Required next action")
    parts.append(session.get("required_next_action") or "_(none)_")
    parts.append(f"\n**Law 0:** {session['law0_status']}")
    return "\n".join(parts) + "\n"


def render_status(session: "dict | None") -> str:
    if not session:
        return _banner("DSIU-Shell — status") + "\n" + EMPTY_STATE_MESSAGE + "\n"
    q = session.get("quick_status", {})
    layers = q.get("detected_layers")
    layers_line = (", ".join(f"{k}={v['count']}" for k, v in layers.items())
                   if layers else "_(none)_")
    ms = q.get("movement_score")
    lane = q.get("primary_execution_lane")
    return _banner("DSIU-Shell — status") + "\n" + "\n".join([
        f"**Last command:** `{session['command']}`",
        f"**Last target:** `{session['target']}`",
        f"**Detected layers:** {layers_line}",
        f"**UEF lane:** {lane or '_(none)_'}"
        + (f"  ·  risk: {q.get('permission_risk')}" if lane else ""),
        f"**Movement score:** {ms if ms is not None else '_(no prior pass)_'}"
        + (" (direction unverified — movement ≠ improvement)" if ms is not None else ""),
        f"**Law 0:** {session['law0_status']}",
        f"**Required next action:** {session.get('required_next_action') or '_(none)_'}",
    ]) + "\n"


def render_history(sessions: list) -> str:
    head = _banner("DSIU-Shell — history") + "\n"
    if not sessions:
        return head + EMPTY_STATE_MESSAGE + "\n"
    rows = ["| # | timestamp | command | target |", "|---|---|---|---|"]
    for i, s in enumerate(sessions, 1):
        rows.append(f"| {i} | {s.get('timestamp','')} | {s.get('command','')} "
                    f"| `{s.get('target','')}` |")
    return head + "\n".join(rows) + "\n"


def render_explain(session: "dict | None") -> str:
    head = _banner("DSIU-Shell — explain last") + "\n"
    if not session:
        return head + EMPTY_STATE_MESSAGE + "\n"

    lines = [f"**What was analyzed:** `{session['target']}` "
             f"(via `{session['command']}`)."]

    oil = session.get("oil_report")
    if oil:
        q = session.get("quick_status", {})
        layers = q.get("detected_layers") or {}
        layer_line = ", ".join(f"{k}={v['count']}" for k, v in layers.items()) or "none"
        lines.append(f"**What DSIU detected (OIL):** layers — {layer_line}.")
        weaknesses = oil.get("key_weaknesses") or []
        if weaknesses:
            lines.append("**Candidate weaknesses (require review):**")
            for w in weaknesses:
                lines.append(f"- [{w['kind']}] ({w['layer']}) {w['detail']}")
        ms = q.get("movement_score")
        if ms is not None:
            lines.append(f"**Movement:** {ms} — measured change only; "
                         "direction unverified; no improvement or upgrade claimed.")
        else:
            lines.append("**Movement:** no prior pass on record — nothing to measure yet.")

    uef = session.get("uef_profile") or (
        {"primary_execution_lane": session.get("quick_status", {}).get("primary_execution_lane")}
        if session.get("quick_status", {}).get("primary_execution_lane") else None)
    if uef and uef.get("primary_execution_lane"):
        lines.append(f"**Compatibility (UEF):** recommended candidate lane "
                     f"`{uef['primary_execution_lane']}` (requires validation; "
                     "execution not performed).")
        if uef.get("permission_risk"):
            lines.append(f"**Permission risk:** {uef['permission_risk']}.")

    lines.append(f"**Next action:** {session.get('required_next_action') or '_(none)_'}")
    lines.append(f"\n**Law 0:** {session['law0_status']}")
    return head + "\n".join(lines) + "\n"
