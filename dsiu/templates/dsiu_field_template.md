# DSIU Field Template

> The canonical DSIU artifact. One per system analyzed. Every field is either
> **[observed]** or **[inferred / candidate / draft]** — keep the two distinguishable
> (Law 0). An unfinished template is a hypothesis, not a diagnosis.

---

**System Name:**
<!-- What system is being studied? -->

**System Purpose:**
<!-- What is it supposed to do? -->

**Date / Analyst:**

---

## Trunk

**Intake Layer** — what enters the system?
<!-- sources, formats, who/what supplies input -->

**Processing Layer** — what happens inside?
<!-- interpretation, routing, rules, transformation -->

**Output Layer** — what result is produced?
<!-- results, destinations, what leaves or changes -->

---

## Architecture

**Branches** — what sub-processes exist inside each layer?
<!-- intake: source/format/permission/validation/rejection
     processing: interpretation/routing/rules/transformation/control/failure
     output: result/destination/logging/feedback/security -->

**Gates** — what controls entry, movement, permission, or rejection?

**Control Points** — where can we intervene? (mark the single highest-leverage one)

**Failure Points** — where does the system break, slow, leak, distort, or misfire?

---

## Behavior

**Behavior Producers** — what input, environment, rules, pressure, incentives, memory,
available paths, or feedback shape the output?
<!-- which producer is driving the behavior you want to change? -->

---

## Upgrade

**Upgrade Plan** — what should be improved, automated, protected, simplified, or
replaced? (proposals only — note rollback path where one exists)

| # | Layer | Control point | Proposed change | Rollback | Status |
|---|---|---|---|---|---|
| 1 |  |  |  |  | proposed |

**Repeatable Engine** — how does the upgraded version run again and again without
needing constant rescue? (what makes it teachable, measurable, and self-correcting?)

---

*Observe. Map. Upgrade. Repeat.*
