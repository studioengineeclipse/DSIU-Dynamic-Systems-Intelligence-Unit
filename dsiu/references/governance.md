# DSIU Governance

DSIU is a lens, not a weapon and not a magic upgrader. These invariants hold on every
pass. Law 0 is top-level and overrides convenience.

## Law 0 — Honesty of Claim

Never state more certainty than the evidence supports.

- A **map is a map**, not the territory. Label inferred structure as inferred.
- The `scan` engine emits a **heuristic first pass**. Every generated mapping is marked
  `DRAFT` and must be verified by a human before it is trusted or acted on.
- DSIU **maps, scores, and proposes**. It never claims to have *upgraded*, *fixed*, or
  *sealed* anything. Those are real engineering actions that happen *after* the diagnosis,
  by doing the actual work.
- If a control point or failure point is a guess, say "candidate" — do not present it as
  confirmed.
- Meters, scores, and readiness ratings are **routing signals**, not verdicts. They tell
  you where to look, not what is true.

## Integrity rules

1. **Observe what is, not what is claimed.** Map the system's actual behavior, not its
   documentation or its self-description. They often disagree — the disagreement is data.
2. **Mark the hidden vs the visible.** Separate what you directly observed from what you
   inferred. Keep the two distinguishable in the output.
3. **No silent upgrades.** Any proposed change is a proposal until a human approves and
   implements it. The Upgrade Plan field lists proposals, not completed work.
4. **Reversibility first.** Prefer upgrades that can be rolled back. Note the rollback
   path for each proposed change where one exists.
5. **Least intervention.** The best control point is the smallest change with the largest
   downstream effect. Resist the urge to rebuild what only needs a gate adjusted.
6. **Boundaries are capability boundaries.** "Breaking through" means extending your own
   capability by finding the real control point — never bypassing consent, permissions,
   or safety on systems you do not own.

## Hand-off contract

A DSIU pass is *done* when it produces a completed Field Template whose every field is
either (a) directly observed, or (b) clearly marked as inferred/candidate/draft. An
unfinished or unverified pass is not a diagnosis — it is a hypothesis.
