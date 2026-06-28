"""Render — Markdown for the OS-Seed control plane. Every output is DRAFT."""

from __future__ import annotations

from . import DRAFT_STAMP, OS_SEED_VERSION, ROADMAP

_BOUNDARY = ("_Scaffold only: a read-only map of the operating environment. No boot, "
             "install, or execution; does not replace the host OS._")

_STATUS_MARK = {"done": "✅", "current": "🟡 in progress", "future": "▫ future"}


def _banner(title: str) -> str:
    return (f"# {title}\n\n> {OS_SEED_VERSION}  ·  {DRAFT_STAMP}\n"
            f"> {_BOUNDARY}\n")


def render_manifest_md(m: dict) -> str:
    lines = [_banner("DSIU-OS-Seed — system manifest"),
             f"**Schema:** `{m['schema']}`  ·  **Current phase:** {m['current_phase']}"
             f"  ·  **Next:** {m['next_phase']}\n"]
    for o in m["organs"]:
        lines.append(f"## {o['title']}  (`{o['name']}` · {o['version']})")
        lines.append(f"- **Purpose:** {o['purpose']}")
        lines.append(f"- **Capabilities:** {', '.join(o['capabilities'])}")
        lines.append(f"- **CLI:** `{o['cli_entrypoint']}`")
        lines.append(f"- **State dir:** {o['state_directory'] or '_(none)_'}")
        lines.append(f"- **Execution boundary:** {o['execution_boundary']}")
        lines.append(f"- **Future OS role:** {o['future_os_role']}\n")
    lines.append(f"**Future OS role:** {m['future_os_role']}")
    return "\n".join(lines) + "\n"


def render_topology_md(t: dict) -> str:
    nodes = ", ".join(f"`{n['id']}`({n['kind']})" for n in t["nodes"])
    edges = "\n".join(f"- `{e['from']}` → `{e['to']}` — {e['relation']}"
                      for e in t["edges"])
    return _banner("DSIU-OS-Seed — topology") + "\n" + "\n".join([
        f"**Schema:** `{t['schema']}`", "", f"**Nodes:** {nodes}", "",
        "**Edges:**", edges, "",
        f"- **Data flow:** {t['data_flow']}",
        f"- **Control flow:** {t['control_flow']}",
        f"- **Feedback flow:** {t['feedback_flow']}",
        f"- **State flow:** {t['state_flow']}",
        f"- **Future expansion points:** {', '.join(t['future_expansion_points'])}",
    ]) + "\n"


def render_readiness_md(r: dict) -> str:
    sd = "\n".join(f"- `{s['dir']}` ({s['organ']}) — known: {s['known']}, "
                   f"present: {s['present']}" for s in r["state_dirs"])
    return _banner("DSIU-OS-Seed — readiness") + "\n" + "\n".join([
        f"**Schema:** `{r['schema']}`",
        f"**OS readiness level:** {r['os_readiness_level']}",
        "",
        f"- **Organs detected:** {', '.join(r['organs_detected']) or '_(none)_'}",
        f"- **Missing organs:** {', '.join(r['missing_organs']) or '_(none)_'}",
        f"- **Command surfaces:** {', '.join(r['command_surfaces_detected'])}",
        f"- **Tests detected:** {', '.join(r['tests_detected'])}",
        f"- **Policy boundaries declared:** {r['policy_boundaries_declared']}",
        f"- **build_skill present:** {r['build_skill_present']}",
        f"- **State dirs known:** {r['state_dirs_known']}",
        sd,
        "",
        f"**Next required action:** {r['next_required_action']}",
    ]) + "\n"


def render_status_md(manifest: dict, readiness: dict) -> str:
    organs = ", ".join(o["name"] for o in manifest["organs"])
    caps = sum(len(o["capabilities"]) for o in manifest["organs"])
    state_dirs = ", ".join(o["state_directory"] for o in manifest["organs"]
                           if o["state_directory"])
    return _banner("DSIU-OS-Seed — status") + "\n" + "\n".join([
        f"**Organs present:** {organs}",
        f"**Capabilities available:** {caps} across {len(manifest['organs'])} organs",
        f"**Known state directories:** {state_dirs}",
        f"**OS readiness level:** {readiness['os_readiness_level']}",
        f"**Law 0:** enforced — {DRAFT_STAMP}; scaffold only, no execution performed",
        f"**Next phase recommendation:** {manifest['next_phase']} "
        "(DSIU-Desktop Layer, requires validation)",
    ]) + "\n"


def render_roadmap_md() -> str:
    rows = ["| phase | description | status |", "|---|---|---|"]
    for key, desc, st in ROADMAP:
        rows.append(f"| {key} | {desc} | {_STATUS_MARK[st]} |")
    return _banner("DSIU-OS-Seed — roadmap") + "\n" + "\n".join(rows) + "\n"
