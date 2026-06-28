"""DSIU-Shell CLI — `python -m dsiu_shell <command>`.

The single front door over OIL + UEF. Parses args, calls the programmatic command
API, and prints rendered Markdown. It runs nothing itself.
"""

from __future__ import annotations

import argparse
import sys

from . import OIL_STATE_DIR, SHELL_STATE_DIR
from . import commands as C
from . import render as R


def _add_state_args(p, oil=False):
    p.add_argument("--state-dir", default=SHELL_STATE_DIR,
                   help="where shell sessions are saved")
    if oil:
        p.add_argument("--oil-state-dir", default=OIL_STATE_DIR,
                       help="where OIL feedback memory is saved")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="dsiu_shell",
        description="DSIU-Shell — command cockpit over OIL + UEF (v0.1).",
    )
    sub = ap.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("inspect", help="run the OIL operating loop on a target")
    sp.add_argument("path")
    sp.add_argument("--name")
    sp.add_argument("--include-docs", action="store_true")
    _add_state_args(sp, oil=True)

    sp = sub.add_parser("profile", help="run UEF compatibility intake on a workload")
    sp.add_argument("path")
    _add_state_args(sp)

    sp = sub.add_parser("analyze", help="run OIL with an attached UEF profile")
    sp.add_argument("path")
    sp.add_argument("--name")
    sp.add_argument("--include-docs", action="store_true")
    sp.add_argument("--with", dest="with_path", required=True,
                    help="workload to attach a UEF compatibility profile for")
    _add_state_args(sp, oil=True)

    sp = sub.add_parser("status", help="show the latest shell session summary")
    _add_state_args(sp)

    sp = sub.add_parser("history", help="list recent shell sessions")
    sp.add_argument("--limit", type=int, default=10)
    _add_state_args(sp)

    sp = sub.add_parser("explain", help="explain the last session (`explain last`)")
    sp.add_argument("what", nargs="?", default="last")
    _add_state_args(sp)

    args = ap.parse_args(argv)
    cmd = args.command

    try:
        if cmd == "inspect":
            sess = C.inspect(args.path, name=args.name,
                             include_docs=args.include_docs,
                             state_dir=args.state_dir,
                             oil_state_dir=args.oil_state_dir)
            sys.stdout.write(sess["rendered_summary"])
        elif cmd == "profile":
            sess = C.profile(args.path, state_dir=args.state_dir)
            sys.stdout.write(sess["rendered_summary"])
        elif cmd == "analyze":
            sess = C.analyze(args.path, name=args.name,
                             include_docs=args.include_docs,
                             with_path=args.with_path,
                             state_dir=args.state_dir,
                             oil_state_dir=args.oil_state_dir)
            sys.stdout.write(sess["rendered_summary"])
        elif cmd == "status":
            sys.stdout.write(R.render_status(C.status(state_dir=args.state_dir)))
        elif cmd == "history":
            sys.stdout.write(R.render_history(
                C.history(state_dir=args.state_dir, limit=args.limit)))
        elif cmd == "explain":
            sys.stdout.write(R.render_explain(
                C.explain_last(state_dir=args.state_dir)))
        else:
            return 1
    except (NotADirectoryError, FileNotFoundError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    except ValueError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
