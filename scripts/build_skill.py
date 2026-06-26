#!/usr/bin/env python3
"""
Build the installable DSIU skill bundle.

Zips the `dsiu/` source tree into `dist/dsiu.skill` (a plain zip with a `dsiu/`
top-level folder, the Claude Code skill layout). Validates the bundle before
packaging so CI fails on a broken skill instead of shipping one.

Usage:
    python scripts/build_skill.py [--src dsiu] [--out dist/dsiu.skill]

Standard library only.
"""

from __future__ import annotations

import argparse
import os
import sys
import zipfile

REQUIRED_FILES = (
    "SKILL.md",
    "DSIU_INDEX.md",
    "scripts/dsiu_analyze.py",
    "references/prime_law.md",
    "references/attribute_layer.md",
    "references/behavior_engine.md",
    "references/learning_ladder.md",
    "references/governance.md",
    "templates/dsiu_field_template.md",
    "templates/dsiu_scorecard.md",
)


def _read_frontmatter(skill_md: str) -> dict:
    """Minimal YAML-frontmatter reader (name/description) — no PyYAML needed."""
    with open(skill_md, encoding="utf-8") as fh:
        text = fh.read()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    keys = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith((" ", "\t", "#")):
            k, _, v = line.partition(":")
            keys[k.strip()] = v.strip()
    return keys


def validate(src: str) -> list:
    """Return a list of problems; empty means the bundle is valid."""
    problems = []
    for rel in REQUIRED_FILES:
        if not os.path.isfile(os.path.join(src, rel)):
            problems.append(f"missing required file: {rel}")

    skill_md = os.path.join(src, "SKILL.md")
    if os.path.isfile(skill_md):
        fm = _read_frontmatter(skill_md)
        if "name" not in fm:
            problems.append("SKILL.md frontmatter missing `name`")
        if "description" not in fm and "description" not in open(
                skill_md, encoding="utf-8").read():
            problems.append("SKILL.md frontmatter missing `description`")
    return problems


def build(src: str, out: str) -> int:
    problems = validate(src)
    if problems:
        sys.stderr.write("build failed — bundle is invalid:\n")
        for p in problems:
            sys.stderr.write(f"  - {p}\n")
        return 1

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    top = os.path.basename(src.rstrip(os.sep))

    files = []
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for fn in sorted(filenames):
            if fn.endswith(".pyc"):
                continue
            full = os.path.join(dirpath, fn)
            arc = os.path.join(top, os.path.relpath(full, src))
            files.append((full, arc))

    files.sort(key=lambda t: t[1])  # stable ordering for reproducible builds
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for full, arc in files:
            zf.write(full, arc)

    sys.stdout.write(f"built {out} ({len(files)} files)\n")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build the DSIU .skill bundle.")
    ap.add_argument("--src", default="dsiu", help="skill source directory")
    ap.add_argument("--out", default="dist/dsiu.skill", help="output .skill path")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.src):
        sys.stderr.write(f"error: source dir not found: {args.src}\n")
        return 2
    return build(args.src, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
