"""Render — Markdown for the desktop surface. Every output is DRAFT."""

from __future__ import annotations

from . import DESKTOP_VERSION, DRAFT_STAMP

_BOUNDARY = ("_Operating environment surface: a read-only workspace/dashboard. "
             "No execution performed; does not boot, install, watch, or replace the host OS._")

_MARK = {"done": "✅", "current": "🟡 in progress", "future": "▫ future"}


def _banner(title: str) -> str:
    return (f"# {title}\n\n> {DESKTOP_VERSION}  ·  {DRAFT_STAMP}\n> {_BOUNDARY}\n")


def _shell_line(s: dict) -> str:
    if not s.get("present"):
        return "_(none yet)_"
    ms = s.get("movement_score")
    lane = s.get("primary_execution_lane")
    return (f"`{s.get('command')}` on `{s.get('target')}`"
            + (f" · movement {ms} (direction unverified)" if ms is not None else "")
            + (f" · lane {lane}" if lane else ""))


def _daemon_line(d: dict) -> str:
    if not d.get("present"):
        return "_(none yet)_"
    return f"{d.get('event_type')} · {d.get('change_summary')}"


def render_overview_md(dash: dict) -> str:
    org = dash["organs_summary"]
    osd = dash["os_seed_status"]
    phase = next((p for p in dash["roadmap"] if p["state"] == "current"), None)
    return _banner("DSIU Desktop — overview") + "\n" + "\n".join([
        f"**Organs ({org['count']}):** "
        + ", ".join(o["name"] for o in org["organs"]),
        f"**Roadmap phase:** {phase['phase'] if phase else '?'} "
        f"({phase['description'] if phase else ''})",
        f"**OS-Seed readiness:** {osd['os_readiness_level']} "
        f"(detected: {', '.join(osd['organs_detected'])})",
        f"**Latest shell session:** {_shell_line(dash['latest_shell_session_summary'])}",
        f"**Latest daemon event:** {_daemon_line(dash['latest_daemon_event_summary'])}",
        f"**Registered workspaces:** {len(dash['registered_workspaces'])}",
        "",
        f"**Next recommended action:** {dash['next_recommended_action']}",
        f"\n**Law 0:** enforced — {DRAFT_STAMP}; no execution performed.",
    ]) + "\n"


def render_dashboard_md(dash: dict) -> str:
    org = dash["organs_summary"]
    comp = dash["compatibility_summary"]
    ws = dash["registered_workspaces"]
    ws_md = ("\n".join(f"- `{w['path']}` ({w['name']})" for w in ws)
             if ws else "_(none registered)_")
    comp_line = ("_(none yet)_" if not comp.get("present")
                 else f"{comp.get('workload')} → `{comp.get('primary_execution_lane')}` "
                      f"(risk {comp.get('permission_risk')})")
    return _banner("DSIU Desktop — dashboard") + "\n" + "\n".join([
        f"**Schema:** `{dash['schema']}`  ·  **no_execution_performed:** "
        f"{dash['no_execution_performed']}",
        "",
        "## Organs",
        ", ".join(f"{o['name']}({o['version']})" for o in org["organs"]),
        "",
        "## OS-Seed status",
        f"- readiness: {dash['os_seed_status']['os_readiness_level']}",
        "",
        "## Workspaces",
        ws_md,
        "",
        "## Reports",
        f"- latest shell session: {_shell_line(dash['latest_shell_session_summary'])}",
        f"- latest daemon event: {_daemon_line(dash['latest_daemon_event_summary'])}",
        f"- compatibility: {comp_line}",
        "",
        "## Policies",
        "\n".join(f"- {b}" for b in dash["policy_boundaries"]),
        "",
        f"## Next recommended action\n{dash['next_recommended_action']}",
    ]) + "\n"


def render_workspace_list_md(workspaces: list) -> str:
    head = _banner("DSIU Desktop — workspaces") + "\n"
    if not workspaces:
        return head + f"{DRAFT_STAMP} — no workspaces registered. Run `workspace add`.\n"
    rows = ["| # | name | path | exists |", "|---|---|---|---|"]
    for i, w in enumerate(workspaces, 1):
        rows.append(f"| {i} | {w['name']} | `{w['path']}` | {w.get('exists')} |")
    return head + "\n".join(rows) + "\n"


def render_status_md(dash: dict) -> str:
    org = dash["organs_summary"]
    return _banner("DSIU Desktop — status") + "\n" + "\n".join([
        f"**Workspaces registered:** {len(dash['registered_workspaces'])}",
        f"**Known organs ({org['count']}):** "
        + ", ".join(o["name"] for o in org["organs"]),
        f"**Latest shell:** {_shell_line(dash['latest_shell_session_summary'])}",
        f"**Latest daemon:** {_daemon_line(dash['latest_daemon_event_summary'])}",
        f"**Law 0:** enforced — {DRAFT_STAMP}; no execution performed.",
    ]) + "\n"


def render_roadmap_md(dash: dict) -> str:
    rows = ["| phase | description | status |", "|---|---|---|"]
    for p in dash["roadmap"]:
        rows.append(f"| {p['phase']} | {p['description']} | {_MARK[p['state']]} |")
    return _banner("DSIU Desktop — roadmap") + "\n" + "\n".join(rows) + "\n"
