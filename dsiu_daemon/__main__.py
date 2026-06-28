"""DSIU-Daemon CLI — `python -m dsiu_daemon <command>`.

Explicit, foreground watcher over Shell + OIL + UEF. Observes and reports only.
"""

from __future__ import annotations

import argparse
import sys

from . import DAEMON_STATE_DIR, FOREGROUND_NOTICE
from . import events as E
from . import render as R
from . import supervisor as S
from .config import WatchConfig


def _add_common(p, watcher=False):
    p.add_argument("path")
    p.add_argument("--name")
    p.add_argument("--include-docs", action="store_true")
    p.add_argument("--uef", dest="uef_path",
                   help="attach a UEF compatibility profile for this workload")
    p.add_argument("--state-dir", default=DAEMON_STATE_DIR)
    p.add_argument("--oil-state-dir", default="dsiu_state")
    if watcher:
        p.add_argument("--interval", type=int, default=5,
                       help="seconds between polls (watch mode)")
        p.add_argument("--limit", type=int, default=None,
                       help="max observation cycles (bounds the foreground loop)")
        p.add_argument("--record-no-change", action="store_true",
                       help="write every no_change event (default: suppress repeats)")


def _config(args) -> WatchConfig:
    return WatchConfig(
        path=args.path, name=args.name, include_docs=args.include_docs,
        interval=getattr(args, "interval", 5), uef_path=args.uef_path,
        state_dir=args.state_dir, oil_state_dir=args.oil_state_dir,
        record_no_change=getattr(args, "record_no_change", False),
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="dsiu_daemon",
        description="DSIU-Daemon — explicit foreground watcher over Shell + OIL + UEF (v0.1).",
    )
    sub = ap.add_subparsers(dest="command", required=True)

    _add_common(sub.add_parser("once", help="run one observation cycle"))
    _add_common(sub.add_parser("watch", help="foreground watch loop"), watcher=True)

    for name in ("status", "explain"):
        sp = sub.add_parser(name, help=f"{name} the latest daemon event")
        sp.add_argument("what", nargs="?", default="last")
        sp.add_argument("--state-dir", default=DAEMON_STATE_DIR)
    hp = sub.add_parser("history", help="list recent daemon events")
    hp.add_argument("--limit", type=int, default=10)
    hp.add_argument("--state-dir", default=DAEMON_STATE_DIR)

    args = ap.parse_args(argv)
    cmd = args.command

    try:
        if cmd == "once":
            ev = S.run_once(_config(args))
            sys.stdout.write(R.render_event_report(ev))
        elif cmd == "watch":
            sys.stderr.write(FOREGROUND_NOTICE + "\n")
            events = S.run_watch(_config(args), max_cycles=args.limit)
            sys.stdout.write(R.render_event_report(events[-1]) if events
                             else "no cycles run\n")
        elif cmd == "status":
            sys.stdout.write(R.render_status(E.latest_event(args.state_dir)))
        elif cmd == "history":
            sys.stdout.write(R.render_history(
                E.list_events(args.state_dir, limit=args.limit)))
        elif cmd == "explain":
            sys.stdout.write(R.render_explain(E.latest_event(args.state_dir)))
        else:
            return 1
    except (NotADirectoryError, FileNotFoundError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
