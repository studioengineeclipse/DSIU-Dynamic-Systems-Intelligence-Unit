# DSIU — Skill Index

**Dynamic Systems Intelligence Unit.** A universal operating lens: look at any system
and ask what enters it, what transforms inside it, what leaves, what controls the
transformation, what conditions shape the behavior, where it fails, where it can be
upgraded, and how to make the upgraded version repeatable.

> Observe. Map. Upgrade. Repeat.

---

## File map

| Path | What it is |
|---|---|
| `SKILL.md` | Entry point. Trigger conditions, Prime Law, the 8-step Doctrine, the Universal Engine, how to run a pass. Read this first. |
| `references/prime_law.md` | The Prime Law, the Universal Pattern table, the full branch taxonomy (trunk → branches → gates → control points). |
| `references/attribute_layer.md` | The diagnosis engine: qualities / skills / strengths / weaknesses / control points per layer, and how to read a scorecard. |
| `references/behavior_engine.md` | The 8 behavior producers, control points, the "change the producer" rule, worked example. |
| `references/learning_ladder.md` | The 6 learning levels and the self-upgrading perception→feedback→repetition engine. |
| `references/governance.md` | **Law 0 — Honesty of Claim** and the integrity / hand-off rules. Read before acting on any output. |
| `templates/dsiu_field_template.md` | The canonical 12-field deliverable. One per system. |
| `templates/dsiu_scorecard.md` | Per-layer attribute scorecard (1–5 ratings + read-out). |
| `scripts/dsiu_analyze.py` | Runnable engine (stdlib only). Modes: `template` (blank Field Template), `scan` (intake/processing/output map of a directory + structured JSON scorecard; `--include-docs` to see config/knowledge files), `scorecard` (structured attribute scorecard for a named system, JSON + Markdown), `diff` (compare two passes → movement score; DSIU's feedback loop), `packet` (Mission-Packet-shaped JSON for CPK hand-off). |
| `../examples/dsiu_on_dsiu_field.md` | Worked example: DSIU's lens turned on its own v1 bundle (a completed Field Template). |

---

## Quick start

```bash
# Blank Field Template for any system (code or not)
python scripts/dsiu_analyze.py template --name "My System" > my_system.dsiu.md

# Heuristic first-pass map of a codebase (always a DRAFT — verify by hand)
python scripts/dsiu_analyze.py scan --path ./repo --name "My Repo" \
    --out repo.dsiu.md --json repo.scorecard.json

# Structured attribute scorecard for a named system (JSON + Markdown, no model call)
python scripts/dsiu_analyze.py scorecard --name "My System" --json my.scorecard.json

# Measure what moved between two passes — DSIU's feedback loop
python scripts/dsiu_analyze.py diff --before before.json --after after.json --json delta.json

# Emit a CPK Mission-Packet-shaped JSON for hand-off (contract only)
python scripts/dsiu_analyze.py packet --json repo.scorecard.json --out packet.json
```

For non-code systems (a workflow, an org, a habit, an AI pipeline), skip the script
and fill `templates/dsiu_field_template.md` directly using the doctrine in `SKILL.md`.

---

## Where DSIU sits in the stack

DSIU is the **Observe / diagnose** front-end. It produces a completed Field Template;
that artifact becomes the `Inputs` + `Hard locks` + `Failure bans` of a **CPK FINAL**
Mission Packet. DSIU maps the system and names the control points → CPK scores, gates,
and executes the upgrade → the result is preserved as a repeatable engine.

```
DSIU (map + diagnose)  →  CPK Mission Packet (score/gate/route)  →  Build (upgrade)  →  Preserve (engine)
```

---

## Law 0 (non-negotiable)

DSIU **maps, scores, and proposes**. It never claims to have upgraded, fixed, or sealed
anything — those are real engineering actions taken *after* the diagnosis. The `scan`
engine emits a heuristic draft; verify before trusting. Scores are routing signals, not
verdicts. Full text: `references/governance.md`.
