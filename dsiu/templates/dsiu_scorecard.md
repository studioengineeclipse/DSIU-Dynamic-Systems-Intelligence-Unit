# DSIU Attribute Scorecard

> One scorecard per system. Scores are **routing signals**, not verdicts (Law 0) —
> they tell you where to look first. Rate each quality 1–5 (1 = severe weakness,
> 5 = strong). Leave a cell blank rather than inventing a value.

**System:**  ·  **Date / Analyst:**

---

## Intake — ability to receive reality

| Quality | 1–5 | Note |
|---|---|---|
| Speed |  |  |
| Accuracy |  |  |
| Filtering (noise rejection) |  |  |
| Access / availability |  |  |
| Validation strength |  |  |

- **Strengths:**
- **Weaknesses:**
- **Control points:**

## Processing — ability to transform

| Quality | 1–5 | Note |
|---|---|---|
| Throughput |  |  |
| Correctness |  |  |
| Latency |  |  |
| Observability |  |  |
| Failure handling |  |  |

- **Strengths:**
- **Weaknesses:**
- **Control points:**

## Output — ability to act on the world

| Quality | 1–5 | Note |
|---|---|---|
| Reliability |  |  |
| Fidelity |  |  |
| Traceability (logging) |  |  |
| Safety / export control |  |  |
| Feedback wiring |  |  |

- **Strengths:**
- **Weaknesses:**
- **Control points:**

---

## Read-out

- **Weakest gate** (caps whole-system quality):
- **Highest-leverage control point** (moves the most downstream):
- **Missing feedback loop** (if any — a blind system cannot self-upgrade):
- **Bad default** (easy path producing the wrong behavior):

**First target:** the layer with control points present but weak qualities — fragile
but fixable. Park rigid layers (strong qualities, no control points) until later.
