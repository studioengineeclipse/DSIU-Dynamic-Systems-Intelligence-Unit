"""DSIU-UEF CLI — `python -m dsiu_uef intake --path ...`.

Classifies a workload and emits a DRAFT compatibility profile (Markdown to stdout
by default; `--json` / `--md` write to files). Runs nothing.
"""

from __future__ import annotations

import argparse
import json
import sys

from .profile import build_profile
from .report import render_profile_md


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="dsiu_uef",
        description="DSIU-UEF — Universal Execution Fabric (compatibility intelligence, v0.1).",
    )
    sub = ap.add_subparsers(dest="mode", required=True)

    it = sub.add_parser("intake", help="classify a workload into a DRAFT compatibility profile")
    it.add_argument("--path", required=True, help="file / folder / repo / manifest to classify")
    it.add_argument("--json", dest="json_out", help="write the profile JSON here")
    it.add_argument("--md", dest="md_out", help="write the Markdown profile here")

    args = ap.parse_args(argv)

    if args.mode == "intake":
        profile = build_profile(args.path)
        report_md = render_profile_md(profile)
        if args.json_out:
            with open(args.json_out, "w", encoding="utf-8") as fh:
                json.dump(profile, fh, indent=2)
            sys.stderr.write(f"wrote compatibility profile: {args.json_out}\n")
        if args.md_out:
            with open(args.md_out, "w", encoding="utf-8") as fh:
                fh.write(report_md)
            sys.stderr.write(f"wrote profile report: {args.md_out}\n")
        if not args.json_out and not args.md_out:
            sys.stdout.write(report_md)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
