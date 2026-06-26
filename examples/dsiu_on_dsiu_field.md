# DSIU Field Template — DSIU v1 (self-analysis)

> Observe. Map. Upgrade. Repeat. — The DSIU Way
> The lens turned on itself. Findings marked **[observed]** (directly checked) or
> **[inferred]**. This is a diagnosis + proposal set, not completed work (Law 0).

**System Name:** DSIU v1 (the skill bundle built this session)
**System Purpose:** Expose a system's hidden Intake→Processing→Output architecture,
locate control/failure points, and produce a verified upgrade plan.
**Date / Analyst:** 2026-06-24 / DSIU-on-DSIU

---

## Trunk

**Intake Layer** — what enters DSIU?
[observed] Three intake paths: (a) a *system name* → `template` mode; (b) a *directory
path* → `scan` mode; (c) a *human reading the references* → manual pass. The scan path
ingests **file paths only** — `os.walk` + `CODE_EXTS` filter.

**Processing Layer** — what happens inside?
[observed] `scan` buckets each path by substring-signal score (3 signal tables) →
highest wins → `unclassified` fallback. Manual pass applies the doctrine + attribute
layer by hand. `template` mode just renders a blank form.

**Output Layer** — what is produced?
[observed] A Field Template (markdown) + a JSON scorecard of layer counts/shares.

---

## Architecture

**Branches** — fully documented in `prime_law.md`. The *tooling* only touches the
intake "format" branch (extension filter) and a crude "routing" step (bucketing).

**Gates** — the one real gate is Law 0 DRAFT-stamping on scan output. [observed] It is
enforced only by a hardcoded string in the renderer; nothing verifies the stamp
survives downstream.

**Control Points** (where intervention has leverage):
1. The signal tables + `CODE_EXTS` — widening these changes **intake** quality.
2. The scorecard generator — adding condition-scoring changes **processing** quality.
3. **A new diff/measurement mode** — adding this gives DSIU its missing **feedback
   loop**. ← single highest-leverage control point.

**Failure Points** (where DSIU v1 breaks):
- **F1 — scanner blind to non-code.** [observed] `CODE_EXTS` excludes `.md/.yaml/.json/
  .toml`. A knowledge- or config-driven system is invisible to it — *including DSIU
  itself* (live proof: scanned its own bundle → 1 file seen, 0 classified).
- **F2 — reads names, not contents.** [observed] Bucketing never opens a file. Structure
  not encoded in the path name is missed. "analyze" isn't a signal, so even its own one
  script came back `unclassified`.
- **F3 — no condition tooling.** [observed] The attribute layer (qualities / strengths /
  weaknesses) — DSIU's actual diagnosis engine — is 100% manual. The script maps
  *structure*, never *condition*.
- **F4 — no feedback loop.** [observed] There is no way to compare two passes. A
  framework whose Prime principle *is* the feedback loop has no feedback loop in its own
  tooling. You cannot measure whether an upgrade worked. **This is the core irony.**
- **F5 — no test harness.** [observed] The bundle ships no validation that the engine
  behaves or that Law 0 stamps persist.

---

## Behavior

**Behavior Producers** — why does DSIU v1 behave thinly?
- **Available paths** [inferred]: name-matching was the *easiest* implementation path,
  so that is what got built — DSIU's own rule ("systems do what is easiest, not best")
  applied to its own construction.
- **Feedback** [observed]: with no measurement loop, the tool cannot self-correct, so it
  stays at v1 quality. Change the producer (add feedback) and the behavior changes.

---

## Upgrade

**Upgrade Plan** (proposals only — all reversible; each is an additive mode/flag):

| # | Layer | Control point | Proposed change | Rollback | Status |
|---|---|---|---|---|---|
| 1 | Output | diff/measure mode | `diff` mode: compare two passes, emit what moved + a movement score → DSIU's own feedback loop | delete mode | proposed |
| 2 | Intake | `CODE_EXTS` + signals | scan reads file *contents* for route/handler/validation/render signatures; inventory `.md/.yaml/.json` | flag-gated | proposed |
| 3 | Processing | scorecard generator | `score` mode scaffolds the attribute scorecard with detected hints | delete mode | proposed |
| 4 | Gates | governance | `scripts/test_dsiu.py` asserts classification + DRAFT-stamp retention | delete file | proposed |
| 5 | Intake | signal tables | widen verbs (analyze, audit, validate, orchestrate…) | revert list | proposed |

**Highest-leverage:** #1. It closes DSIU's own loop — once a pass can be measured
against the previous one, every future DSIU upgrade is itself scored by DSIU.

**Repeatable Engine — how the recursion becomes real and measurable:**

```
DSIU (method)  →  diagnoses DSIU (artifact)  →  upgrade plan
      ↑                                              ↓
   sharper  ← improved DSIU  ←  Claude Code implements  ← (you approve)
              ↑___________ diff mode measures the delta ___________↑
```

The lens does the diagnosing; **Claude Code does the building** (it edits the files).
The skill does not rewrite itself autonomously — and Law 0 forbids pretending it does.
But with #1 in place, each turn of the loop is *measured*, so "DSIU building DSIU" stops
being a metaphor and becomes a tracked, improving engine.

---
*Observe. Map. Upgrade. Repeat.*
