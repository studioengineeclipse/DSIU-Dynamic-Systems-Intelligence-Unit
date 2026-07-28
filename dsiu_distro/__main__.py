"""DSIU-Distro CLI — `python -m dsiu_distro <command>`.

Read-only distribution scaffold. Each command supports --json/--md; default writes
Markdown to stdout. It describes a distribution; it builds, installs, and boots nothing.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import render as R
from .boot import build_boot_topology
from .image import build_image_plan
from .manifest import build_manifest
from .packages import build_package_set


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
        prog="dsiu_distro",
        description="DSIU-Distro — Linux-distribution scaffold / spec control plane (v0.1).",
    )
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("manifest", "packages", "boot", "image", "status", "roadmap"):
        sp = sub.add_parser(name, help=f"emit the DSIU-Distro {name}")
        sp.add_argument("--json", dest="json_out")
        sp.add_argument("--md", dest="md_out")

    args = ap.parse_args(argv)
    cmd = args.command

    if cmd == "manifest":
        data = build_manifest()
        _emit(data, R.render_manifest_md(data), args.json_out, args.md_out)
    elif cmd == "packages":
        data = build_package_set()
        _emit(data, R.render_packages_md(data), args.json_out, args.md_out)
    elif cmd == "boot":
        data = build_boot_topology()
        _emit(data, R.render_boot_md(data), args.json_out, args.md_out)
    elif cmd == "image":
        data = build_image_plan()
        _emit(data, R.render_image_md(data), args.json_out, args.md_out)
    elif cmd == "status":
        manifest, packages = build_manifest(), build_package_set()
        data = {"manifest": manifest, "packages": packages}
        _emit(data, R.render_status_md(manifest, packages),
              args.json_out, args.md_out)
    elif cmd == "roadmap":
        from dsiu_os_seed import ROADMAP
        data = {"schema": "dsiu.distro_roadmap/v0.1",
                "status": "DRAFT — phased path; future phases not built",
                "phases": [{"phase": k, "description": d, "state": s}
                           for k, d, s in ROADMAP]}
        _emit(data, R.render_roadmap_md(), args.json_out, args.md_out)
    else:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
