"""Render — Markdown for the DSIU-Distro scaffold. Every output is DRAFT."""

from __future__ import annotations

from . import DISTRO_VERSION, DRAFT_STAMP

_BOUNDARY = ("_Scaffold only: a read-only description of a DSIU Linux distribution. "
             "No build, install, boot, or image emission; does not replace the host OS._")


def _banner(title: str) -> str:
    return (f"# {title}\n\n> {DISTRO_VERSION}  ·  {DRAFT_STAMP}\n> {_BOUNDARY}\n")


def render_packages_md(p: dict) -> str:
    rows = ["| component | category | role | status |", "|---|---|---|---|"]
    for c in p["components"]:
        rows.append(f"| `{c['name']}` | {c['category']} | {c['role']} | {c['status']} |")
    return _banner("DSIU-Distro — package set") + "\n" + "\n".join([
        f"**Schema:** `{p['schema']}`  ·  **components:** {p['component_count']} "
        f"({p['organ_count']} organs + {len(p['base_components'])} base)  ·  "
        f"**no_build_performed:** {p['no_build_performed']}",
        "",
        *rows,
    ]) + "\n"


def render_boot_md(b: dict) -> str:
    rows = ["| # | layer | role | DSIU component |", "|---|---|---|---|"]
    for s in b["stages"]:
        rows.append(f"| {s['order']} | {s['layer']} | {s['role']} | "
                    f"{s['dsiu_component'] or '_(none)_'} |")
    return _banner("DSIU-Distro — boot topology") + "\n" + "\n".join([
        f"**Schema:** `{b['schema']}`  ·  **operator surface:** "
        f"`{b['operator_surface']}`  ·  **no_boot_performed:** {b['no_boot_performed']}",
        "",
        *rows,
    ]) + "\n"


def render_image_md(im: dict) -> str:
    stages = "\n".join(f"{s['order']}. **{s['stage']}** — {s['role']}"
                       for s in im["build_stages"])
    targets = "\n".join(f"- `{t['format']}` — {t['role']} ({t['status']})"
                        for t in im["targets"])
    return _banner("DSIU-Distro — image plan") + "\n" + "\n".join([
        f"**Schema:** `{im['schema']}`  ·  **no_image_built:** {im['no_image_built']}",
        "",
        "## Build stages (planned)",
        stages,
        "",
        "## Target formats (planned — none emitted)",
        targets,
    ]) + "\n"


def render_manifest_md(m: dict) -> str:
    return _banner("DSIU-Distro — manifest") + "\n" + "\n".join([
        f"**Schema:** `{m['schema']}`  ·  **Current phase:** {m['current_phase']}"
        f"  ·  **Next:** {m['next_phase']}",
        f"**Built on:** {m['built_on']}",
        "",
        f"- **Components:** {m['components']['count']} "
        f"({m['components']['organs']} organs + {m['components']['base']} base)",
        f"- **Boot stages:** {m['boot']['stage_count']} "
        f"→ operator surface `{m['boot']['operator_surface']}`",
        f"- **Image targets:** {', '.join(m['image']['target_formats'])} "
        f"(no_image_built: {m['image']['no_image_built']})",
        f"- **Execution boundary:** {m['execution_boundary']}",
        "",
        f"**Distro role:** {m['distro_role']}",
    ]) + "\n"


def render_status_md(manifest: dict, packages: dict) -> str:
    return _banner("DSIU-Distro — status") + "\n" + "\n".join([
        f"**Components planned:** {packages['component_count']} "
        f"({packages['organ_count']} organs + {len(packages['base_components'])} base)",
        f"**Boot stages planned:** {manifest['boot']['stage_count']}",
        f"**Image targets planned:** {', '.join(manifest['image']['target_formats'])}",
        f"**Current phase:** {manifest['current_phase']}  ·  "
        f"**Next phase:** {manifest['next_phase']}",
        f"**Law 0:** enforced — {DRAFT_STAMP}; scaffold only, no build/boot/image, "
        "no execution performed.",
    ]) + "\n"


def render_roadmap_md() -> str:
    from dsiu_os_seed import ROADMAP
    mark = {"done": "✅", "current": "🟡 in progress", "future": "▫ future"}
    rows = ["| phase | description | status |", "|---|---|---|"]
    for key, desc, st in ROADMAP:
        rows.append(f"| {key} | {desc} | {mark[st]} |")
    return _banner("DSIU-Distro — roadmap") + "\n" + "\n".join(rows) + "\n"
