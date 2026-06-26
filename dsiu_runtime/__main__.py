"""DSIU-OIL CLI — `python -m dsiu_runtime <mode>`.

v0.1 exposes the operating loop. Default output is the Markdown supervisor report
on stdout; `--json` / `--md` write the full artifact bundle / report to files.
"""

from __future__ import annotations

import argparse
import json
import sys

from .loop import run_loop
from .supervisor import render_report_md


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="dsiu_runtime",
        description="DSIU-OIL — the DSIU Operating Intelligence Layer (v0.1).",
    )
    sub = ap.add_subparsers(dest="mode", required=True)

    # `loop` is the operating loop. `operating_loop` is a documented alias.
    for alias in ("loop", "operating_loop"):
        lp = sub.add_parser(alias, help="run one operating-loop pass over a target")
        lp.add_argument("--path", required=True, help="directory to operate on")
        lp.add_argument("--name", help="system name (defaults to dir name)")
        lp.add_argument("--state-dir", default="dsiu_state",
                        help="where before/after scan states are saved")
        lp.add_argument("--include-docs", action="store_true",
                        help="include .md/.yaml/.json/.toml etc. in the scan surface")
        lp.add_argument("--execute", action="store_true",
                        help="record a gated supervised no-op (no live change in v0.1)")
        lp.add_argument("--json", dest="json_out",
                        help="write the full artifact bundle (JSON) here")
        lp.add_argument("--md", dest="md_out",
                        help="write the Markdown supervisor report here")

    args = ap.parse_args(argv)

    if args.mode in ("loop", "operating_loop"):
        try:
            result = run_loop(
                path=args.path, name=args.name, state_dir=args.state_dir,
                include_docs=args.include_docs, execute=args.execute,
            )
        except NotADirectoryError as exc:
            sys.stderr.write(f"error: not a directory: {exc}\n")
            return 2

        report_md = render_report_md(result["supervisor_report"])

        if args.json_out:
            with open(args.json_out, "w", encoding="utf-8") as fh:
                json.dump(result, fh, indent=2)
            sys.stderr.write(f"wrote artifact bundle: {args.json_out}\n")
        if args.md_out:
            with open(args.md_out, "w", encoding="utf-8") as fh:
                fh.write(report_md)
            sys.stderr.write(f"wrote supervisor report: {args.md_out}\n")
        if not args.json_out and not args.md_out:
            sys.stdout.write(report_md)
        else:
            sys.stderr.write(f"state saved: {result['state_path']}\n")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
