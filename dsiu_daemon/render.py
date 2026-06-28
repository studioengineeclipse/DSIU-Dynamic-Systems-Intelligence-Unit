"""Render — Markdown for daemon output. Empty-state safe; read views never write."""

from __future__ import annotations

from . import DAEMON_VERSION, DRAFT_STAMP, EMPTY_STATE_MESSAGE

_BOUNDARY = ("_Observation only: the daemon watches and reports. No execution, no "
             "fixes applied, no background service installed._")


def _banner(title: str) -> str:
    return (f"# {title}\n\n> {DAEMON_VERSION}  ·  {DRAFT_STAMP}\n"
            f"> {_BOUNDARY}\n")


def _movement_line(ev: dict) -> str:
    ms = ev.get("movement_score")
    if ms is None:
        return "_(no movement measured this event)_"
    return f"{ms} (direction unverified — movement ≠ improvement)"


def render_event_report(ev: dict) -> str:
    changed = ev.get("changed_files") or []
    changed_md = ("\n".join(f"- `{f}`" for f in changed[:20]) +
                  (f"\n- _… {len(changed) - 20} more_" if len(changed) > 20 else "")
                  ) if changed else "_(none)_"
    uef = ev.get("uef_profile")
    uef_line = (f"`{uef['primary_execution_lane']}` (candidate, requires validation)"
                if uef else "_(none attached)_")
    return _banner(f"DSIU-Daemon — {ev.get('event_type')} event") + "\n" + "\n".join([
        f"**Watched:** `{ev.get('watched_path')}`  ·  **Name:** {ev.get('name')}",
        f"**Event type:** {ev.get('event_type')}  ·  **Timestamp:** {ev.get('timestamp')}",
        f"**Change:** {ev.get('change_summary')}",
        "",
        "## Changed files",
        changed_md,
        "",
        f"**Analyzed:** {ev.get('analyzed')}",
        f"**Movement:** {_movement_line(ev)}",
        f"**UEF lane:** {uef_line}",
        f"**Law 0:** {ev.get('law0_status')}",
        f"**Required next action:** {ev.get('required_next_action')}",
    ]) + "\n"


def render_status(ev: "dict | None") -> str:
    if not ev:
        return _banner("DSIU-Daemon — status") + "\n" + EMPTY_STATE_MESSAGE + "\n"
    return _banner("DSIU-Daemon — status") + "\n" + "\n".join([
        f"**Last event:** {ev.get('event_type')} @ {ev.get('timestamp')}",
        f"**Watched:** `{ev.get('watched_path')}`",
        f"**Change:** {ev.get('change_summary')}",
        f"**Movement:** {_movement_line(ev)}",
        f"**Law 0:** {ev.get('law0_status')}",
        f"**Required next action:** {ev.get('required_next_action')}",
    ]) + "\n"


def render_history(events: list) -> str:
    head = _banner("DSIU-Daemon — history") + "\n"
    if not events:
        return head + EMPTY_STATE_MESSAGE + "\n"
    rows = ["| # | timestamp | type | changed | watched |",
            "|---|---|---|---|---|"]
    for i, ev in enumerate(events, 1):
        rows.append(f"| {i} | {ev.get('timestamp','')} | {ev.get('event_type','')} "
                    f"| {len(ev.get('changed_files') or [])} "
                    f"| `{ev.get('watched_path','')}` |")
    return head + "\n".join(rows) + "\n"


def render_explain(ev: "dict | None") -> str:
    head = _banner("DSIU-Daemon — explain last") + "\n"
    if not ev:
        return head + EMPTY_STATE_MESSAGE + "\n"
    lines = [
        f"**What was observed:** `{ev.get('watched_path')}` "
        f"({ev.get('event_type')} event).",
        f"**What changed:** {ev.get('change_summary')}.",
    ]
    if ev.get("event_type") == "error":
        lines.append(f"**Error:** {ev.get('error')}.")
    if ev.get("analyzed"):
        lines.append("**Analysis:** DSIU-Shell was triggered (OIL"
                     + (" + UEF" if ev.get("uef_profile") else "") + ").")
        lines.append(f"**Movement:** {_movement_line(ev)}. "
                     "Measured change only; no improvement or upgrade claimed.")
    else:
        lines.append("**Analysis:** not triggered (no change) — no movement claim.")
    lines.append(f"**Next action:** {ev.get('required_next_action')}")
    lines.append(f"\n**Law 0:** {ev.get('law0_status')}")
    return head + "\n".join(lines) + "\n"
