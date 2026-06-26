# DSIU Operating Intelligence Layer — v0.1

> Observe → Map → Score → Packetize → Supervise → Diff → Feedback → Repeat

DSIU-OIL is the **operating intelligence layer**: it turns the discrete DSIU engine
modes (`scan`, `scorecard`, `packet`, `diff`) into one coherent operating loop. This
is the brainstem before the body — the brain a future DSIU shell/OS gets built
around.

**It is NOT** a kernel, daemon, desktop shell, universal execution fabric, or OS.
Those are later phases. v0.1 keeps strictly to the loop, with the same realistic
dependencies as the skill: Python/CLI, JSON contracts, Markdown reports, local
state, policy gates, tests.

```
DSIU Operating Intelligence Layer (v0.1)
├── engine.py      reuses the skill engine (dsiu/scripts/dsiu_analyze.py) — no rewrite
├── graph.py       Process Graph Engine — intake/processing/output/feedback + control/failure points
├── state.py       State directory = v0.1 feedback memory (before/after snapshots)
├── policy.py      Law-0 gate — DRAFT everywhere; movement ≠ improvement
├── supervisor.py  Supervisor report (JSON + Markdown) + reserved execution seam
├── loop.py        run_loop(): the operating loop itself
└── __main__.py    `python -m dsiu_runtime loop ...`
```

## Run it

```bash
# One operating-loop pass (Markdown supervisor report to stdout)
python -m dsiu_runtime loop --path ./repo --name "My Repo" --include-docs

# Write the full artifact bundle (JSON) and the report (Markdown)
python -m dsiu_runtime loop --path ./repo --name "My Repo" \
    --json report.json --md report.md

# Re-run after a change — the loop diffs against the saved prior state
python -m dsiu_runtime loop --path ./repo --name "My Repo" --json report2.json

# Record a gated, supervised no-op (no live change happens in v0.1)
python -m dsiu_runtime loop --path ./repo --name "My Repo" --execute
```

`operating_loop` is a documented alias for `loop`.

## What one pass produces

A single artifact bundle: `scorecard`, process `graph`, CPK `packet`, optional
`diff` (only when a prior pass exists), `policy_verdict`, and the `supervisor_report`
with: target analyzed · detected layers · candidate weaknesses · control points ·
proposed mission packet · required next action · movement score (if a diff exists).

## Feedback memory & state

Each pass saves its scorecard under `dsiu_state/<slug>/scan-<UTC>.json`. The loop
loads the **previous** state *before* saving the current one, so a pass can never be
diffed against itself and fake a feedback loop. This state history is the v0.1
feedback memory; a richer `dsiu_memory` (repeated-failure tracking, known patterns)
is a later phase. `dsiu_state/` is gitignored.

## Law 0 (enforced here, not just documented)

- **Every** artifact carries the `DRAFT` stamp — scorecard, graph, packet, diff,
  policy verdict, supervisor report, and the execute record.
- **Movement is not improvement.** A diff can show the system *changed*; v0.1 never
  claims it *improved*. The policy verdict always sets
  `improvement_claim_allowed: false`, `upgrade_claim_allowed: false`,
  `direction: "unverified"`. An improvement evaluator is a later phase.
- Allowed wording: *candidate weakness, proposed control point, movement measured,
  direction unverified, requires review.* Forbidden: *upgrade completed, system
  fixed, weakness solved, confirmed improvement.*
- **Execution is dry-run only.** `--execute` records a supervised no-op; no agent or
  execution fabric is wired. `future_execution_fabric: reserved` is just a named
  seam for a later phase.

## Where this sits in the roadmap

1. DSIU executable skill ✅
2. **DSIU-OIL — operating intelligence layer ← you are here**
3. DSIU-UEF — universal execution fabric (next)
4. DSIU Shell
5. DSIU system daemon
6. DSIU OS distribution

Build OIL now. Build UEF next. The OS comes much later — once the brain is stable.
