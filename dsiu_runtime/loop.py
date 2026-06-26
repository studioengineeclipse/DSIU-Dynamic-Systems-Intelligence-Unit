"""The operating loop — the heart of DSIU-OIL.

    Observe -> Map -> Score -> Packetize -> Supervise -> Diff -> Feedback -> Repeat

One coherent pass over a target that orchestrates the existing engine, persists
state, measures movement against the previous pass, applies Law-0 policy, and
emits a supervisor report. It performs no live changes.
"""

from __future__ import annotations

import os

from .engine import build_diff, build_packet, build_scorecard, walk_repo
from .graph import build_process_graph
from .policy import build_policy_verdict, enforce_draft
from .state import previous_state, save_state
from .supervisor import build_supervisor_report


def run_loop(path: str, name: "str | None" = None,
             state_dir: str = "dsiu_state",
             include_docs: bool = False,
             execute: bool = False) -> dict:
    """Run one operating-loop pass and return all artifacts."""
    root = os.path.abspath(path)
    if not os.path.isdir(root):
        raise NotADirectoryError(root)
    name = name or os.path.basename(root.rstrip(os.sep)) or "system"

    # 1. Observe / Map — include_docs so config/knowledge surfaces aren't invisible.
    items = list(walk_repo(root, include_docs=include_docs))

    # 2. Score
    scorecard = build_scorecard(name, root, items)

    # 3. Feedback memory: load the PREVIOUS state *before* saving the current one,
    #    so a pass can never be diffed against itself.
    previous = previous_state(state_dir, name)
    state_path = save_state(state_dir, name, scorecard)

    # 4. Map structure -> process graph
    graph = build_process_graph(name, scorecard)

    # 5. Packetize -> CPK Mission Packet shape
    packet = build_packet(name, scorecard)

    # 6. Diff -> movement (only when a real prior pass exists)
    diff = build_diff(previous, scorecard) if previous else None

    # 7. Supervise -> Law-0 policy gate over every emitted artifact
    draft_violations = enforce_draft(
        scorecard=scorecard, graph=graph, packet=packet, diff=diff,
    )
    policy_verdict = build_policy_verdict(diff, draft_violations)

    # Execution Supervisor: dry-run by default; --execute is a gated no-op record.
    execute_record = None
    if execute:
        if policy_verdict["draft_ok"]:
            execute_record = (
                "approved supervised no-op — no agent / execution fabric is wired "
                "in v0.1; no live change was performed and no upgrade is claimed."
            )
        else:
            execute_record = ("execution refused — Law-0 DRAFT stamp violations "
                              "present; resolve before any execution.")

    report = build_supervisor_report(
        target=root, scorecard=scorecard, graph=graph, packet=packet,
        diff=diff, policy_verdict=policy_verdict, execute_record=execute_record,
    )

    return {
        "state_path": state_path,
        "scorecard": scorecard,
        "graph": graph,
        "packet": packet,
        "diff": diff,
        "policy_verdict": policy_verdict,
        "supervisor_report": report,
    }
