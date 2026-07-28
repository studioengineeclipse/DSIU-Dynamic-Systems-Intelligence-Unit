"""DSIU-Desktop CLI — `python -m dsiu_desktop <command>`.

The first local workspace/control surface. Read-only against the organs; it writes
only its own desktop state. It runs nothing.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import DESKTOP_STATE_DIR
from . import render as R
from . import state as _state
from . import workspace as _workspace
from .dashboard import build_dashboard


def _emit(data, md, json_out, md_out):
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
        prog="dsiu_desktop",
        description="DSIU-Desktop Layer — local workspace / control surface (v0.1).",
    )
    sub = ap.add_subparsers(dest="command", required=True)

    ov = sub.add_parser("overview", help="current desktop overview")
    ov.add_argument("--state-dir", default=DESKTOP_STATE_DIR)

    ws = sub.add_parser("workspace", help="manage registered workspaces")
    wssub = ws.add_subparsers(dest="ws_command", required=True)
    wadd = wssub.add_parser("add", help="register a workspace path")
    wadd.add_argument("path")
    wadd.add_argument("--name")
    wadd.add_argument("--state-dir", default=DESKTOP_STATE_DIR)
    wlist = wssub.add_parser("list", help="list registered workspaces")
    wlist.add_argument("--state-dir", default=DESKTOP_STATE_DIR)

    dash = sub.add_parser("dashboard", help="build a DRAFT desktop dashboard")
    dash.add_argument("--state-dir", default=DESKTOP_STATE_DIR)
    dash.add_argument("--json", dest="json_out")
    dash.add_argument("--md", dest="md_out")

    st = sub.add_parser("status", help="current desktop state")
    st.add_argument("--state-dir", default=DESKTOP_STATE_DIR)

    rm = sub.add_parser("roadmap", help="the phased OS path")
    rm.add_argument("--state-dir", default=DESKTOP_STATE_DIR)
    rm.add_argument("--json", dest="json_out")
    rm.add_argument("--md", dest="md_out")

    tui = sub.add_parser("tui", help="render the text-UI dashboard (snapshot frame)")
    tui.add_argument("--state-dir", default=DESKTOP_STATE_DIR)
    tui.add_argument("--width", type=int, default=80)
    tui.add_argument("--interactive", action="store_true",
                     help="user-driven refresh (r=refresh, q=quit); not a watch loop")

    args = ap.parse_args(argv)
    cmd = args.command

    if cmd == "overview":
        sys.stdout.write(R.render_overview_md(build_dashboard(args.state_dir)))
    elif cmd == "workspace":
        if args.ws_command == "add":
            rec = _workspace.add_workspace(args.path, name=args.name,
                                           state_dir=args.state_dir)
            sys.stdout.write(R.render_workspace_list_md(
                _workspace.list_workspaces(args.state_dir)))
            sys.stderr.write(f"registered: {rec['path']}\n")
        else:
            sys.stdout.write(R.render_workspace_list_md(
                _workspace.list_workspaces(args.state_dir)))
    elif cmd == "dashboard":
        d = build_dashboard(args.state_dir)
        _state.save_dashboard(args.state_dir, d)
        _emit(d, R.render_dashboard_md(d), args.json_out, args.md_out)
    elif cmd == "status":
        sys.stdout.write(R.render_status_md(build_dashboard(args.state_dir)))
    elif cmd == "roadmap":
        d = build_dashboard(args.state_dir)
        _emit({"schema": "dsiu.desktop_roadmap/v0.1",
               "status": "DRAFT — phased path; future phases not built",
               "roadmap": d["roadmap"]},
              R.render_roadmap_md(d), args.json_out, args.md_out)
    elif cmd == "tui":
        from . import tui as _tui
        if args.interactive:
            return _tui.run_interactive(args.state_dir, width=args.width)
        sys.stdout.write(_tui.render_tui_frame(
            build_dashboard(args.state_dir), width=args.width))
    else:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
