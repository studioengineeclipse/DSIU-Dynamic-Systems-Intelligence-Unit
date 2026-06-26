---
name: dsiu
description: >
  Use when analyzing, diagnosing, mapping, or upgrading any system — a codebase,
  AI pipeline, app, workflow, organization, machine, or behavior pattern. DSIU
  exposes a system's hidden Intake -> Processing -> Output architecture, separates
  its layers, locates control points and failure points, and produces a structured
  upgrade plan. Trigger when the user wants to understand "how this really works,"
  find bottlenecks or leverage points, restructure a process, or convert raw
  complexity into a repeatable engine. Stacks with CPK FINAL as the Observe/diagnose
  front-end that feeds a Mission Packet.
---

# DSIU — Dynamic Systems Intelligence Unit

A research, analysis, and operational-design lens for discovering the hidden layered
architecture behind any system, mapping its intake → processing → output chain,
identifying branches, gates, control points, weaknesses, and behavior-producing
conditions, then upgrading the system into a repeatable, resilient, improvable engine.

**Closing law of the unit:** *Observe. Map. Upgrade. Repeat.*

---

## When to run DSIU

Run this skill when the task is to *understand or change a system*, not just produce a
one-off output. Signals:

- "How does this actually work?" / "Why does it keep doing X?"
- "Where's the bottleneck?" / "What's the highest-leverage place to intervene?"
- "Map this codebase / pipeline / workflow / org."
- "This keeps failing — find the real cause, not the symptom."
- "Make this repeatable / harden it / seal the weak spots."

If the user just wants a single artifact built with no diagnosis, this skill is
overkill — hand off to the builder. DSIU is the **Observe** stage.

---

## The Prime Law

DSIU branches from one law (full text in `references/prime_law.md`):

1. Everything that operates has a system.
2. Every system has layers.
3. Every layer has processes.
4. Every process can be observed, improved, automated, protected, or replaced.

---

## The Doctrine (execution sequence)

Every DSIU pass runs this sequence in order. Do not skip steps; a skipped step is
the usual reason an "upgrade" fails downstream.

1. **Observe the system** — see what is *actually* happening, not what it claims.
2. **Separate the layers** — split visible from hidden parts.
3. **Identify the process chain** — map intake, processing, output, feedback, failure paths.
4. **Find the control points** — locate where intervention creates leverage.
5. **Detect failure points** — leaks, bottlenecks, weak gates, bad defaults, degraded logic.
6. **Upgrade the flow** — speed, stability, precision, resilience, automation, clarity.
7. **Seal the weak spots** — protect against collapse, misuse, drift, overload, corruption.
8. **Turn it into an engine** — make the upgraded version repeatable, teachable, measurable.

---

## The Universal Engine

The trunk of every system reduces to three processes, each of which **branches** —
it is never flat. Full taxonomy in `references/prime_law.md`.

```
SYSTEM
├── 1. INTAKE      source · format · permission · validation · rejection-path
├── 2. PROCESSING  interpretation · routing · rules · transformation · control · failure
└── 3. OUTPUT      result · destination · logging/confirm · feedback-loop · security/export
```

Then add the **attribute layer** to each process — qualities, skills, strengths,
weaknesses, control points (`references/attribute_layer.md`). This is what turns DSIU
from a description into a diagnosis.

Then add the **behavior engine** — behavior is the visible output of a hidden
condition stack: input + environment + rules + pressure + incentives + memory +
available paths + feedback. Do not fight behavior; change its producer
(`references/behavior_engine.md`).

---

## How to run a pass

**Manual pass (any system, including non-code):**
Fill `templates/dsiu_field_template.md`. Walk the 12 fields top to bottom. For each
layer, also fill `templates/dsiu_scorecard.md` (qualities / strengths / weaknesses /
control points). The filled template *is* the deliverable.

**Assisted pass (a codebase or directory):**
Run the engine to get a heuristic first draft, then verify and refine it by hand.

```bash
# Emit a blank, headed Field Template for a named system
python scripts/dsiu_analyze.py template --name "AI Control Plane" > control_plane.dsiu.md

# Walk a repo, draft the Intake->Processing->Output map + a structured JSON scorecard
python scripts/dsiu_analyze.py scan --path ./my-repo --name "My Repo" \
    --out my-repo.dsiu.md --json my-repo.scorecard.json
# add --include-docs so knowledge/config-driven systems aren't invisible to the scan

# Emit the structured attribute scorecard (qualities/skills/strengths/weaknesses/
# control-points per layer) for a named system, as JSON + Markdown — no scan, no model
python scripts/dsiu_analyze.py scorecard --name "My System" \
    --out my-system.scorecard.md --json my-system.scorecard.json

# Feedback loop: measure what moved between two passes (DSIU on DSIU, measurably)
python scripts/dsiu_analyze.py diff --before before.json --after after.json \
    --out delta.md --json delta.json

# Hand-off to CPK FINAL: emit a Mission-Packet-shaped JSON (contract only)
python scripts/dsiu_analyze.py packet --json my-repo.scorecard.json --out packet.json
```

See `../examples/dsiu_on_dsiu_field.md` for a completed Field Template — the lens
turned on its own bundle.

> **Law 0 — Honesty of Claim.** `scan` output is a *heuristic first pass*. Every
> generated mapping is marked `DRAFT` and must be verified by a human before it is
> trusted or acted on. The engine maps, scores, and proposes — it never claims to
> have *upgraded* anything. See `references/governance.md`.

---

## Output: the canonical artifact

A DSIU pass always produces a **Field Template** (the 12 fields). That artifact is
the hand-off unit. To fuse with CPK FINAL: the completed Field Template becomes the
`Inputs` + `Hard locks` + `Failure bans` of a Mission Packet — DSIU diagnoses, CPK
scores/gates/executes the upgrade. See `DSIU_INDEX.md` for the full file map.

---

## Learning ladder (where you are with a system)

Contact → Pattern → Control → Structural → Transfer → Design. You can influence a
system long before you fully understand it, but understanding multiplies leverage.
Full ladder + the imagination/feedback engine in `references/learning_ladder.md`.

*— The DSIU Way*
