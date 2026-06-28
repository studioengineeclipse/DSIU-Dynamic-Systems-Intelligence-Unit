"""DSIU-OS-Seed CLI — `python -m dsiu_os_seed <command>`.

Read-only control plane. Each command supports --json/--md; default writes Markdown
to stdout. It introspects and documents; it runs nothing.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import render as R
from .manifest import build_manifest
from .readiness import build_readiness
from .topology import build_topology


def _emit(data: "dict | None", md: str, json_out, md_out):
    if json_out and data is not None:
        with open(json_out, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        sys.stderr.write(f"wrote JSON: {json_out}\n")
    if md_out:
        with open(md_out, "w", encoding="utf-8") as fh:
            fh.write(md)
        sys.stderr.write(f"wrote Markdown: {md_out}\n")
    if not json_out and not md_out:
        sys.stdout.write(md)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="dsiu_os_seed",
        description="DSIU-OS-Seed — operating-environment scaffold / control plane (v0.1).",
    )
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("manifest", "topology", "readiness", "status", "roadmap"):
        sp = sub.add_parser(name, help=f"emit the OS-Seed {name}")
        sp.add_argument("--json", dest="json_out")
        sp.add_argument("--md", dest="md_out")

    args = ap.parse_args(argv)
    cmd = args.command

    if cmd == "manifest":
        data = build_manifest()
        _emit(data, R.render_manifest_md(data), args.json_out, args.md_out)
    elif cmd == "topology":
        data = build_topology()
        _emit(data, R.render_topology_md(data), args.json_out, args.md_out)
    elif cmd == "readiness":
        data = build_readiness()
        _emit(data, R.render_readiness_md(data), args.json_out, args.md_out)
    elif cmd == "status":
        manifest, readiness = build_manifest(), build_readiness()
        data = {"manifest": manifest, "readiness": readiness}
        _emit(data, R.render_status_md(manifest, readiness),
              args.json_out, args.md_out)
    elif cmd == "roadmap":
        from . import ROADMAP
        data = {"schema": "dsiu.os_seed_roadmap/v0.1",
                "status": "DRAFT — phased path; future phases not built",
                "phases": [{"phase": k, "description": d, "state": s}
                           for k, d, s in ROADMAP]}
        _emit(data, R.render_roadmap_md(), args.json_out, args.md_out)
    else:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
