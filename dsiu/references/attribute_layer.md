# DSIU Attribute Layer — The Diagnosis Engine

The trunk and branches describe *structure*. The attribute layer describes *condition*.
This is the layer that lets you diagnose a system instead of merely describing it.

Every process — Intake, Processing, Output — carries five attributes:

- **Qualities** — its current condition: speed, accuracy, stability, sensitivity, filtering, capacity, compatibility.
- **Skills** — what it is capable of doing: detect, read, scan, accept, reject, route, transform, verify, emit.
- **Strengths** — where it performs well.
- **Weaknesses** — where it breaks down or degrades.
- **Control Points** — specific places you can intervene, automate, harden, or upgrade.

```
SYSTEM
├── INTAKE      qualities · skills · strengths · weaknesses · control-points
├── PROCESSING  qualities · skills · strengths · weaknesses · control-points
└── OUTPUT      qualities · skills · strengths · weaknesses · control-points
```

---

## The questions a DSIU analyst asks

Not just *"What does this system do?"* but:

- What **condition** is each layer in?
- What can each layer **handle**?
- Where does it **fail**?
- Where can it be **upgraded**?
- **What single control point changes the most downstream behavior?**

That last question is the whole game. Most systems have one or two control points
whose change cascades through everything else. Find those first.

---

## Per-layer attribute prompts

### Intake — the system's ability to receive reality
- Qualities: speed, accuracy, sensitivity, filtering, awareness, access, compatibility
- Skills: detecting, reading, scanning, accepting, rejecting, identifying, sorting
- Common strengths: collects clean information, catches errors early, recognizes patterns
- Common weaknesses: bad data, weak filters, too much noise, blocked access, false input, missing context
- Control points: validation rules, auth gates, rate limits, schema/type checks, source allow-lists

### Processing — the system's ability to transform
- Qualities: throughput, correctness, determinism, latency, headroom, observability
- Skills: parsing, routing, applying rules, rendering, computing, generating, verifying
- Common strengths: correct logic, good routing, graceful failure handling
- Common weaknesses: hidden coupling, silent failure, no retries, unbounded work, missing limits
- Control points: routing tables, policy/rule layers, permission checks, queue/concurrency limits, fallbacks

### Output — the system's ability to act on the world
- Qualities: reliability, fidelity, traceability, safety, reversibility
- Skills: producing, delivering, logging, confirming, feeding back, restricting
- Common strengths: confirmed delivery, full logging, safe export controls
- Common weaknesses: no logging, no confirmation, leaky exports, no feedback loop
- Control points: logging/audit, delivery confirmation, export/security gates, feedback wiring

---

## Reading a scorecard

When all three layers are scored, look for:

1. **The weakest gate** — the layer whose weakness caps the whole system's output quality.
2. **The highest-leverage control point** — change here moves the most downstream.
3. **The missing feedback loop** — a system with no feedback stays blind and cannot self-upgrade.
4. **The bad default** — the easy/automatic path that is producing the wrong behavior.

Score using `templates/dsiu_scorecard.md`. A layer with strong qualities but no control
points is *rigid* (hard to upgrade); a layer with control points but weak qualities is
*fragile but fixable* (your first target).
