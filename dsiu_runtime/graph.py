"""Process Graph Engine — turn a scorecard into a DSIU process graph.

The graph is the operating layer's structural map: intake / processing / output /
feedback nodes, the loop edges between them, the per-layer control points, and
heuristic *candidate* failure points. Everything is DRAFT (Law 0) — these are a
map, not the territory.
"""

from __future__ import annotations

from datetime import date

from .engine import ATTRIBUTE_LAYERS, DRAFT_STAMP, LAYERS

SCHEMA = "dsiu.process_graph/v0.1"


def build_process_graph(name: str, scorecard: dict) -> dict:
    """Build the process graph JSON from a structured scorecard."""
    layers = scorecard.get("layers") or {}
    counts = scorecard.get("layer_counts") or {}

    nodes = []
    for layer in LAYERS:
        block = layers.get(layer) or {}
        files = block.get("files", [])
        nodes.append({
            "id": layer,
            "kind": layer,
            "count": counts.get(layer, len(files)),
            "files": files,
            "control_points": block.get("control_points",
                                        ATTRIBUTE_LAYERS[layer]["control_points"]),
        })
    # The feedback node closes the loop — its presence is what makes this an
    # operating *loop* rather than a one-shot pipeline.
    nodes.append({
        "id": "feedback",
        "kind": "feedback",
        "count": 0,
        "files": [],
        "control_points": ["diff/movement measurement", "state history",
                           "next-pass trigger"],
    })

    edges = [
        {"from": "intake", "to": "processing"},
        {"from": "processing", "to": "output"},
        {"from": "output", "to": "feedback"},
        {"from": "feedback", "to": "intake"},  # the loop
    ]

    control_points = {
        layer: ATTRIBUTE_LAYERS[layer]["control_points"] for layer in LAYERS
    }

    return {
        "schema": SCHEMA,
        "system": name,
        "status": f"{DRAFT_STAMP} — heuristic process map, candidates only (Law 0)",
        "date": date.today().isoformat(),
        "nodes": nodes,
        "edges": edges,
        "control_points": control_points,
        "failure_points": _candidate_failure_points(scorecard, layers, counts),
    }


def _candidate_failure_points(scorecard: dict, layers: dict, counts: dict) -> list:
    """Heuristic, clearly-labelled CANDIDATE failure points (never asserted)."""
    out = []
    for layer in LAYERS:
        if counts.get(layer, 0) == 0:
            out.append({
                "layer": layer,
                "kind": "candidate gap",
                "detail": f"no files detected for the {layer} layer — "
                          "either truly absent or unmapped by the heuristic.",
            })
    unclassified = counts.get("unclassified", 0)
    total = scorecard.get("files_mapped", 0) or 0
    if unclassified and total and unclassified / total >= 0.5:
        out.append({
            "layer": "unclassified",
            "kind": "unmapped surface",
            "detail": f"{unclassified}/{total} files did not match any layer "
                      "signal — large cross-cutting surface needs manual review.",
        })
    # A system with no feedback wiring cannot self-upgrade.
    out.append({
        "layer": "output",
        "kind": "candidate weakness",
        "detail": "verify a feedback loop exists (logs/telemetry/diff); without "
                  "one the system stays blind. Requires review.",
    })
    return out
