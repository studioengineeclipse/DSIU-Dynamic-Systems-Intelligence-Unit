#!/usr/bin/env python3
"""
DSIU Analyze — Dynamic Systems Intelligence Unit engine.

Turns the DSIU lens into a runnable pass. Standard library only; runs anywhere
Python 3.8+ is available (including mobile Claude Code environments).

Modes
-----
  template   Emit a blank, headed DSIU Field Template for a named system.
  scan       Walk a target directory, heuristically map files onto the
             Intake -> Processing -> Output trunk, and emit a DRAFT Field
             Template skeleton plus a structured JSON scorecard.
  scorecard  Emit the structured attribute scorecard (qualities / skills /
             strengths / weaknesses / control-points per layer) for a named
             system, as JSON + Markdown. No directory scan, no model call.
  diff       Compare two scorecard JSONs and report what moved per layer plus a
             single movement score. This is DSIU's own feedback loop.
  packet     Emit a Mission-Packet-shaped JSON (inputs / hard_locks /
             failure_bans) for hand-off to CPK FINAL. Contract only — DSIU
             diagnoses; CPK scores, gates, and executes the upgrade.

Law 0 (Honesty of Claim)
------------------------
`scan` output is a HEURISTIC FIRST PASS. Every generated mapping is marked
DRAFT and must be verified by a human before it is trusted or acted on. The
engine maps, scores, and proposes -- it never claims to have *upgraded*,
*fixed*, or *sealed* anything.

Usage
-----
  python dsiu_analyze.py template --name "AI Control Plane" > control_plane.dsiu.md

  python dsiu_analyze.py scan --path ./my-repo --name "My Repo" \
      --out my-repo.dsiu.md --json my-repo.scorecard.json

  python dsiu_analyze.py scorecard --name "My System" \
      --out my-system.scorecard.md --json my-system.scorecard.json

  python dsiu_analyze.py diff --before before.json --after after.json \
      --out delta.md --json delta.json

  python dsiu_analyze.py packet --json my-repo.scorecard.json --out packet.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import date

# --- Heuristic signal tables -------------------------------------------------
# Substrings matched (case-insensitive) against each file's relative path.
# These are *signals*, not proof. Bucketing is a draft for human review.

INTAKE_SIGNALS = (
    "intake", "input", "ingest", "ingress", "parser", "parse", "reader",
    "/read", "load", "upload", "receive", "collect", "listener", "webhook",
    "request", "schema", "valid", "auth", "middleware", "guard", "sensor",
    "watch", "subscribe", "consume", "cli", "args", "form", "/route",
    "router", "endpoint", "controller",
)

PROCESSING_SIGNALS = (
    "service", "logic", "/core", "engine", "process", "transform", "compute",
    "calc", "model", "infer", "pipeline", "handler", "worker", "job", "queue",
    "schedul", "rules", "policy", "domain", "/util", "/lib", "graph", "reduce",
    "map", "router_logic", "orchestrat", "kernel", "compile", "render_engine",
    # F2 fix: analysis/measurement verbs were missing — DSIU's own tooling
    # ("analyze", "audit", "score", "diff") used to come back unclassified.
    "analyze", "analyse", "analysis", "audit", "measure", "diff", "score",
    "classif", "evaluate", "assess",
)

OUTPUT_SIGNALS = (
    "output", "render", "response", "writer", "/write", "export", "emit",
    "publish", "/send", "/view", "/ui", "component", "template", "report",
    "dispatch", "sink", "result", "build", "artifact", "presenter",
    "serializer", "notif", "/store", "persist", "save", "deliver",
)

# Files/dirs we never bucket (noise, not system surface).
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    "env", "dist", "build", ".next", ".cache", "vendor", ".idea", ".vscode",
    "coverage", ".pytest_cache", ".mypy_cache", "target",
}
CODE_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb", ".php",
    ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".swift", ".kt", ".scala",
    ".sh", ".sql", ".vue", ".svelte",
}
# F1 fix: knowledge/config-driven systems (DSIU itself included) are invisible
# to a code-only scan. `--include-docs` surfaces these so the system is not
# blind to itself.
DOC_EXTS = {
    ".md", ".mdx", ".rst", ".txt", ".yaml", ".yml", ".json", ".toml",
    ".ini", ".cfg", ".conf", ".env", ".properties",
}

LAYERS = ("intake", "processing", "output")

# --- The attribute layer -----------------------------------------------------
# Single source of truth for the diagnosis engine, lifted from
# references/attribute_layer.md. Reused by the scorecard renderers and the
# scan scorecard so docs and code cannot drift (F3 fix).

ATTRIBUTE_LAYERS = {
    "intake": {
        "title": "Intake — ability to receive reality",
        "qualities": ["speed", "accuracy", "filtering", "access", "validation strength"],
        "skills": ["detecting", "reading", "scanning", "accepting", "rejecting",
                   "identifying", "sorting"],
        "common_strengths": ["collects clean information", "catches errors early",
                             "recognizes patterns"],
        "common_weaknesses": ["bad data", "weak filters", "too much noise",
                             "blocked access", "false input", "missing context"],
        "control_points": ["validation rules", "auth gates", "rate limits",
                           "schema/type checks", "source allow-lists"],
    },
    "processing": {
        "title": "Processing — ability to transform",
        "qualities": ["throughput", "correctness", "latency", "observability",
                      "failure handling"],
        "skills": ["parsing", "routing", "applying rules", "rendering",
                   "computing", "generating", "verifying"],
        "common_strengths": ["correct logic", "good routing",
                             "graceful failure handling"],
        "common_weaknesses": ["hidden coupling", "silent failure", "no retries",
                             "unbounded work", "missing limits"],
        "control_points": ["routing tables", "policy/rule layers",
                           "permission checks", "queue/concurrency limits",
                           "fallbacks"],
    },
    "output": {
        "title": "Output — ability to act on the world",
        "qualities": ["reliability", "fidelity", "traceability",
                      "safety / export control", "feedback wiring"],
        "skills": ["producing", "delivering", "logging", "confirming",
                   "feeding back", "restricting"],
        "common_strengths": ["confirmed delivery", "full logging",
                             "safe export controls"],
        "common_weaknesses": ["no logging", "no confirmation", "leaky exports",
                             "no feedback loop"],
        "control_points": ["logging/audit", "delivery confirmation",
                           "export/security gates", "feedback wiring"],
    },
}

DRAFT_STAMP = "DRAFT"  # Law 0 marker that every heuristic output must carry.


def classify(rel_path: str) -> str:
    """Return the highest-scoring layer for a path, or 'unclassified'."""
    p = rel_path.replace("\\", "/").lower()
    scores = {
        "intake": sum(p.count(s) for s in INTAKE_SIGNALS),
        "processing": sum(p.count(s) for s in PROCESSING_SIGNALS),
        "output": sum(p.count(s) for s in OUTPUT_SIGNALS),
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unclassified"


def walk_repo(root: str, include_docs: bool = False):
    """Yield (rel_path, layer) for each code (and optionally doc) file under root."""
    exts = CODE_EXTS | DOC_EXTS if include_docs else CODE_EXTS
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in exts:
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), root)
            yield rel, classify(rel)


# --- Attribute scorecard builders --------------------------------------------

def _layer_attributes(layer: str, files: "list[str] | None" = None) -> dict:
    """Structured, ratings-blank attribute block for one layer (Law 0: a
    scaffold for a human to fill, not an asserted condition)."""
    spec = ATTRIBUTE_LAYERS[layer]
    return {
        "title": spec["title"],
        # ratings left null on purpose — the engine measures structure, never
        # condition. A human (or a later pass) fills 1-5.
        "qualities": [{"name": q, "rating": None, "note": ""} for q in spec["qualities"]],
        "skills": list(spec["skills"]),
        "strengths": [],
        "weaknesses": [],
        "common_strengths": list(spec["common_strengths"]),
        "common_weaknesses": list(spec["common_weaknesses"]),
        "control_points": list(spec["control_points"]),
        "files": sorted(files) if files else [],
    }


def build_attribute_layers(buckets: "dict[str, list[str]] | None" = None) -> dict:
    """All three layers' attribute blocks, optionally seeded with detected files."""
    buckets = buckets or {}
    return {layer: _layer_attributes(layer, buckets.get(layer)) for layer in LAYERS}


# --- Renderers ---------------------------------------------------------------

HEADER = "Observe. Map. Upgrade. Repeat. — The DSIU Way"


def render_template(name: str) -> str:
    """Blank, headed Field Template for a named system."""
    today = date.today().isoformat()
    return f"""# DSIU Field Template — {name}

> {HEADER}
> Every field is either **[observed]** or **[inferred / candidate / draft]**.
> An unfinished template is a hypothesis, not a diagnosis (Law 0).

**System Name:** {name}
**System Purpose:** <!-- what is it supposed to do? -->
**Date / Analyst:** {today} /

---

## Trunk
**Intake Layer** — what enters?
**Processing Layer** — what happens inside?
**Output Layer** — what is produced?

## Architecture
**Branches** — sub-processes inside each layer:
**Gates** — what controls entry, movement, permission, rejection:
**Control Points** — where to intervene (mark the single highest-leverage one):
**Failure Points** — where it breaks, slows, leaks, distorts, misfires:

## Behavior
**Behavior Producers** — input / environment / rules / pressure / incentives /
memory / available paths / feedback driving the output:

## Upgrade
**Upgrade Plan** (proposals only — note rollback where one exists):

| # | Layer | Control point | Proposed change | Rollback | Status |
|---|---|---|---|---|---|
| 1 |  |  |  |  | proposed |

**Repeatable Engine** — how it runs again and again without rescue:

---
*Observe. Map. Upgrade. Repeat.*
"""


def render_scan(name: str, root: str, items: "list[tuple[str, str]]") -> str:
    counts = Counter(layer for _, layer in items)
    total = len(items)
    buckets = {layer: sorted(p for p, l in items if l == layer)
               for layer in (*LAYERS, "unclassified")}

    def sample(layer: str, n: int = 12) -> str:
        files = buckets[layer]
        if not files:
            return "_(none detected)_"
        shown = "\n".join(f"  - `{f}`" for f in files[:n])
        if len(files) > n:
            shown += f"\n  - _… {len(files) - n} more_"
        return shown

    def pct(layer: str) -> str:
        return f"{(counts[layer] / total * 100):.0f}%" if total else "0%"

    today = date.today().isoformat()
    unclassified_note = ""
    if counts["unclassified"]:
        unclassified_note = (
            f"\n> ⚠ {counts['unclassified']} file(s) did not match any layer "
            "signal. Classify these by hand — they are often the most "
            "interesting (glue code, config, cross-cutting concerns).\n"
        )

    return f"""# DSIU Field Template — {name}  ·  {DRAFT_STAMP} (heuristic scan)

> {HEADER}
>
> **Law 0 — this is a heuristic first pass.** Files were bucketed by path-name
> signals only, not by reading what they do. Treat every mapping below as a
> `{DRAFT_STAMP}` to verify and correct by hand before acting on it.

**System Name:** {name}
**Source:** `{root}`
**Date / Analyst:** {today} /
**Files mapped:** {total}  ·  intake {pct('intake')} · processing {pct('processing')} · output {pct('output')} · unclassified {pct('unclassified')}
{unclassified_note}---

## Trunk ({DRAFT_STAMP} — verify)

**Intake Layer** — candidate entry surface ({counts['intake']} files):
{sample('intake')}

**Processing Layer** — candidate transform core ({counts['processing']} files):
{sample('processing')}

**Output Layer** — candidate result/emit surface ({counts['output']} files):
{sample('output')}

**Unclassified** — needs manual classification ({counts['unclassified']} files):
{sample('unclassified')}

---

## Architecture (fill by hand)

**Branches** — open the files above and note the real sub-processes per layer.
**Gates** — auth, validation, permission checks, rate limits — where are they?
**Control Points** — where does one change move the most downstream? (mark it)
**Failure Points** — bottlenecks, silent failures, missing limits, bad defaults.

## Behavior (fill by hand)

**Behavior Producers** — which of input / environment / rules / pressure /
incentives / memory / available paths / feedback is driving the behavior you
want to change?

## Upgrade (proposals only)

| # | Layer | Control point | Proposed change | Rollback | Status |
|---|---|---|---|---|---|
| 1 |  |  |  |  | proposed |

**Repeatable Engine** — what would make the upgraded system self-correcting?

> A structured attribute scorecard (qualities / skills / strengths / weaknesses /
> control points per layer) is in the companion JSON. Fill its `rating` fields to
> turn this structural map into a condition diagnosis.

---
*Generated by dsiu_analyze.py — a map, not the territory. Verify before trusting.*
"""


def render_scorecard_md(name: str, layers: dict, source: "str | None" = None) -> str:
    """Markdown scaffold of the structured attribute scorecard."""
    today = date.today().isoformat()
    src = f"\n**Source:** `{source}`" if source else ""

    def block(layer: str) -> str:
        a = layers[layer]
        rows = "\n".join(
            f"| {q['name']} | {q['rating'] if q['rating'] is not None else ''} | {q['note']} |"
            for q in a["qualities"]
        )
        strengths = ", ".join(a["strengths"]) or \
            "_(fill — hints: " + ", ".join(a["common_strengths"]) + ")_"
        weaknesses = ", ".join(a["weaknesses"]) or \
            "_(fill — hints: " + ", ".join(a["common_weaknesses"]) + ")_"
        files = ""
        if a["files"]:
            shown = "\n".join(f"  - `{f}`" for f in a["files"][:12])
            if len(a["files"]) > 12:
                shown += f"\n  - _… {len(a['files']) - 12} more_"
            files = f"\n- **Detected files:**\n{shown}"
        return f"""## {a['title']}

| Quality | 1–5 | Note |
|---|---|---|
{rows}

- **Skills:** {', '.join(a['skills'])}
- **Strengths:** {strengths}
- **Weaknesses:** {weaknesses}
- **Control points:** {', '.join(a['control_points'])}{files}
"""

    return f"""# DSIU Attribute Scorecard — {name}  ·  {DRAFT_STAMP}

> {HEADER}
>
> Scores are **routing signals**, not verdicts (Law 0). Rate each quality 1–5
> (1 = severe weakness, 5 = strong). Leave a cell blank rather than inventing a
> value. Ratings are null until a human fills them — the engine maps structure,
> never condition.

**System:** {name}{src}
**Date / Analyst:** {today} /

---

{block('intake')}
{block('processing')}
{block('output')}
---

## Read-out (fill by hand)

- **Weakest gate** (caps whole-system quality):
- **Highest-leverage control point** (moves the most downstream):
- **Missing feedback loop** (if any — a blind system cannot self-upgrade):
- **Bad default** (easy path producing the wrong behavior):

**First target:** the layer with control points present but weak qualities —
fragile but fixable. Park rigid layers (strong qualities, no control points).

---
*Observe. Map. Upgrade. Repeat.*
"""


# --- Scorecard JSON ----------------------------------------------------------

def build_scorecard(name: str, root: "str | None",
                    items: "list[tuple[str, str]] | None") -> dict:
    """Structured JSON scorecard. With `items` (from a scan) it seeds per-layer
    file lists + counts; without, it emits the blank attribute scaffold."""
    items = items or []
    counts = Counter(layer for _, layer in items)
    total = len(items)
    buckets = {layer: [p for p, l in items if l == layer] for layer in LAYERS}

    return {
        "system": name,
        "source": root,
        "date": date.today().isoformat(),
        "status": f"{DRAFT_STAMP} — heuristic, requires human verification (Law 0)",
        "kind": "scan" if items else "scorecard",
        "files_mapped": total,
        "layer_counts": {l: counts[l] for l in (*LAYERS, "unclassified")},
        "layer_share": {
            l: round(counts[l] / total, 3) if total else 0.0
            for l in (*LAYERS, "unclassified")
        },
        # The diagnosis engine (F3): per-layer qualities/skills/strengths/
        # weaknesses/control-points, ratings null for a human to fill.
        "layers": build_attribute_layers(buckets if items else None),
        "notes": [
            "Bucketing is by path-name signal only, not by reading file behavior.",
            "Unclassified files often hold the most important cross-cutting logic.",
            "Scores are routing signals, not verdicts.",
            "Quality ratings are null until a human fills them.",
        ],
        "next_steps": [
            "Open each bucket and confirm or move files.",
            "Fill the per-layer quality ratings (1-5) to turn structure into condition.",
            "Locate gates and the single highest-leverage control point.",
            "Re-run and use `diff` to measure whether the upgrade moved the system.",
            "Feed the verified Field Template into a CPK Mission Packet (`packet` mode).",
        ],
    }


# --- diff: DSIU's own feedback loop ------------------------------------------

def build_diff(before: dict, after: dict) -> dict:
    """Compare two scorecard JSONs and report what moved + a movement score.
    This is the feedback loop DSIU's own tooling was missing (F4)."""

    def files_of(card: dict, layer: str) -> set:
        layers = card.get("layers") or {}
        return set((layers.get(layer) or {}).get("files") or [])

    def ratings_of(card: dict, layer: str) -> dict:
        layers = card.get("layers") or {}
        out = {}
        for q in (layers.get(layer) or {}).get("qualities") or []:
            if q.get("rating") is not None:
                out[q["name"]] = q["rating"]
        return out

    per_layer = {}
    files_added_total = files_removed_total = rating_points = 0

    for layer in LAYERS:
        b_files, a_files = files_of(before, layer), files_of(after, layer)
        added = sorted(a_files - b_files)
        removed = sorted(b_files - a_files)
        files_added_total += len(added)
        files_removed_total += len(removed)

        b_counts = before.get("layer_counts", {}).get(layer, len(b_files))
        a_counts = after.get("layer_counts", {}).get(layer, len(a_files))

        b_rate, a_rate = ratings_of(before, layer), ratings_of(after, layer)
        rating_deltas = {}
        for q in set(b_rate) | set(a_rate):
            bv, av = b_rate.get(q), a_rate.get(q)
            if bv != av:
                rating_deltas[q] = {"before": bv, "after": av}
                if bv is not None and av is not None:
                    rating_points += abs(av - bv)

        per_layer[layer] = {
            "files_added": added,
            "files_removed": removed,
            "count_before": b_counts,
            "count_after": a_counts,
            "count_delta": a_counts - b_counts,
            "rating_deltas": rating_deltas,
        }

    movement_score = files_added_total + files_removed_total + rating_points

    return {
        "kind": "diff",
        "status": f"{DRAFT_STAMP} — a measured delta, not a verdict (Law 0)",
        "date": date.today().isoformat(),
        "before": {"system": before.get("system"), "date": before.get("date"),
                   "files_mapped": before.get("files_mapped")},
        "after": {"system": after.get("system"), "date": after.get("date"),
                  "files_mapped": after.get("files_mapped")},
        "per_layer": per_layer,
        "files_added_total": files_added_total,
        "files_removed_total": files_removed_total,
        "rating_points_changed": rating_points,
        "movement_score": movement_score,
        "reading": (
            "movement_score = files added + files removed + total rating points "
            "changed. It measures that the system moved, not that it improved — "
            "pair with the Field Template to judge direction (Law 0)."
        ),
    }


def render_diff_md(d: dict) -> str:
    lines = [
        f"# DSIU Diff — movement report  ·  {DRAFT_STAMP}",
        "",
        f"> {HEADER}",
        ">",
        "> A measured delta, **not** a verdict (Law 0). It tells you the system "
        "moved, not whether it improved.",
        "",
        f"**Before:** {d['before'].get('system')} ({d['before'].get('date')}) · "
        f"{d['before'].get('files_mapped')} files",
        f"**After:**  {d['after'].get('system')} ({d['after'].get('date')}) · "
        f"{d['after'].get('files_mapped')} files",
        "",
        f"**Movement score:** {d['movement_score']}  "
        f"(+{d['files_added_total']} files / −{d['files_removed_total']} files / "
        f"{d['rating_points_changed']} rating points)",
        "",
        "| Layer | Δ count | added | removed |",
        "|---|---|---|---|",
    ]
    for layer in LAYERS:
        pl = d["per_layer"][layer]
        sign = f"+{pl['count_delta']}" if pl["count_delta"] >= 0 else str(pl["count_delta"])
        lines.append(f"| {layer} | {sign} | {len(pl['files_added'])} | {len(pl['files_removed'])} |")
    lines += ["", f"_{d['reading']}_", "", "*Observe. Map. Upgrade. Repeat.*", ""]
    return "\n".join(lines)


# --- packet: hand-off to CPK FINAL (contract only) ---------------------------

GOVERNANCE_HARD_LOCKS = [
    "Law 0 — never claim more certainty than the evidence supports; outputs are DRAFT until verified.",
    "Observe what is, not what is claimed — map actual behavior, not documentation.",
    "No silent upgrades — every change is a proposal until a human approves and implements it.",
    "Reversibility first — prefer changes that can be rolled back; note the rollback path.",
    "Least intervention — smallest change with the largest downstream effect.",
    "Boundaries are capability boundaries — never bypass consent, permissions, or safety.",
]


def build_packet(name: str, card: "dict | None") -> dict:
    """Mission-Packet-shaped JSON for hand-off to CPK FINAL.

    DSIU diagnoses (maps + scores + proposes). CPK FINAL — not part of this
    repo — is what consumes this packet to score, gate, and execute the upgrade.
    This is a documented contract, not a live integration.
    """
    inputs: dict = {"system": name}
    failure_bans: list = []

    if card:
        inputs["files_mapped"] = card.get("files_mapped")
        inputs["layer_counts"] = card.get("layer_counts")
        layers = card.get("layers") or {}
        inputs["layers"] = {
            layer: {
                "files": (layers.get(layer) or {}).get("files", []),
                "control_points": (layers.get(layer) or {}).get("control_points", []),
            }
            for layer in LAYERS
        }
        # The upgrade must not ship the known weaknesses of each layer.
        for layer in LAYERS:
            for w in (layers.get(layer) or {}).get("common_weaknesses", []):
                failure_bans.append(f"{layer}: {w}")
    else:
        inputs["layers"] = {
            layer: {"control_points": ATTRIBUTE_LAYERS[layer]["control_points"]}
            for layer in LAYERS
        }
        for layer in LAYERS:
            for w in ATTRIBUTE_LAYERS[layer]["common_weaknesses"]:
                failure_bans.append(f"{layer}: {w}")

    return {
        "mission": name,
        "kind": "mission_packet",
        "status": f"{DRAFT_STAMP} — DSIU diagnosis for CPK hand-off (Law 0)",
        "date": date.today().isoformat(),
        "source": "DSIU Field Template / scorecard",
        "inputs": inputs,
        "hard_locks": GOVERNANCE_HARD_LOCKS,
        "failure_bans": failure_bans,
        "handoff": (
            "DSIU maps the system and names the control points. Feed this packet "
            "into CPK FINAL: it scores, gates, and executes the upgrade, then the "
            "result is preserved as a repeatable engine. CPK FINAL is external to "
            "this repo — this packet is the contract, not a live call."
        ),
    }


# --- CLI ---------------------------------------------------------------------

def _write(text: str, out: "str | None", label: str) -> None:
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(text)
        sys.stderr.write(f"wrote {label}: {out}\n")
    else:
        sys.stdout.write(text)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="dsiu_analyze",
        description="DSIU — map a system's intake/processing/output architecture.",
    )
    sub = ap.add_subparsers(dest="mode", required=True)

    t = sub.add_parser("template", help="emit a blank Field Template")
    t.add_argument("--name", required=True, help="system name")

    s = sub.add_parser("scan", help="heuristically map a code directory")
    s.add_argument("--path", required=True, help="directory to scan")
    s.add_argument("--name", help="system name (defaults to dir name)")
    s.add_argument("--out", help="write the DRAFT Field Template here (else stdout)")
    s.add_argument("--json", dest="json_out", help="write the JSON scorecard here")
    s.add_argument("--include-docs", action="store_true",
                   help="also inventory .md/.yaml/.json/.toml etc. (F1: see knowledge/config systems)")

    sc = sub.add_parser("scorecard", help="emit the structured attribute scorecard for a named system")
    sc.add_argument("--name", required=True, help="system name")
    sc.add_argument("--out", help="write the Markdown scorecard here (else stdout)")
    sc.add_argument("--json", dest="json_out", help="write the JSON scorecard here")

    d = sub.add_parser("diff", help="compare two scorecard JSONs (DSIU's feedback loop)")
    d.add_argument("--before", required=True, help="earlier scorecard JSON")
    d.add_argument("--after", required=True, help="later scorecard JSON")
    d.add_argument("--out", help="write the Markdown movement report here (else stdout)")
    d.add_argument("--json", dest="json_out", help="write the JSON diff here")

    p = sub.add_parser("packet", help="emit a CPK Mission-Packet-shaped JSON (contract only)")
    p.add_argument("--name", help="mission/system name (defaults to scorecard's system)")
    p.add_argument("--json", dest="json_in", help="scorecard JSON to derive inputs from")
    p.add_argument("--out", help="write the packet JSON here (else stdout)")

    args = ap.parse_args(argv)

    if args.mode == "template":
        sys.stdout.write(render_template(args.name))
        return 0

    if args.mode == "scan":
        root = os.path.abspath(args.path)
        if not os.path.isdir(root):
            sys.stderr.write(f"error: not a directory: {root}\n")
            return 2
        name = args.name or os.path.basename(root.rstrip(os.sep)) or "system"
        items = list(walk_repo(root, include_docs=args.include_docs))
        _write(render_scan(name, root, items), args.out, "Field Template (DRAFT)")
        if args.json_out:
            with open(args.json_out, "w", encoding="utf-8") as fh:
                json.dump(build_scorecard(name, root, items), fh, indent=2)
            sys.stderr.write(f"wrote scorecard: {args.json_out}\n")
        return 0

    if args.mode == "scorecard":
        layers = build_attribute_layers()
        _write(render_scorecard_md(args.name, layers), args.out, "scorecard (Markdown)")
        if args.json_out:
            with open(args.json_out, "w", encoding="utf-8") as fh:
                json.dump(build_scorecard(args.name, None, None), fh, indent=2)
            sys.stderr.write(f"wrote scorecard: {args.json_out}\n")
        return 0

    if args.mode == "diff":
        for f in (args.before, args.after):
            if not os.path.isfile(f):
                sys.stderr.write(f"error: not a file: {f}\n")
                return 2
        with open(args.before, encoding="utf-8") as fh:
            before = json.load(fh)
        with open(args.after, encoding="utf-8") as fh:
            after = json.load(fh)
        diff = build_diff(before, after)
        _write(render_diff_md(diff), args.out, "movement report (Markdown)")
        if args.json_out:
            with open(args.json_out, "w", encoding="utf-8") as fh:
                json.dump(diff, fh, indent=2)
            sys.stderr.write(f"wrote diff: {args.json_out}\n")
        return 0

    if args.mode == "packet":
        card = None
        if args.json_in:
            if not os.path.isfile(args.json_in):
                sys.stderr.write(f"error: not a file: {args.json_in}\n")
                return 2
            with open(args.json_in, encoding="utf-8") as fh:
                card = json.load(fh)
        name = args.name or (card.get("system") if card else None)
        if not name:
            sys.stderr.write("error: provide --name or --json (with a 'system')\n")
            return 2
        packet = build_packet(name, card)
        _write(json.dumps(packet, indent=2) + "\n", args.out, "Mission Packet")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
