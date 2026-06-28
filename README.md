# DSIU — Dynamic Systems Intelligence Unit

> Observe. Map. Upgrade. Repeat.

DSIU is a research, analysis, and operational-design **lens**: point it at any
system — a codebase, an AI pipeline, an app, a workflow, an organization, a
machine, or a behavior pattern — and it exposes the hidden
**Intake → Processing → Output** architecture, separates the layers, locates the
control points and failure points, and produces a structured upgrade plan.

This repo turns the DSIU framework from prose into a **runnable, installable
Claude Code skill** plus a small standard-library engine.

## What's here

| Path | What it is |
|---|---|
| `dsiu/` | The skill bundle (source of truth): `SKILL.md`, doctrine in `references/`, `templates/`, and the `scripts/dsiu_analyze.py` engine. |
| `dsiu_runtime/` | **DSIU-OIL** — the Operating Intelligence Layer that turns the discrete engine modes into one operating loop. See [`dsiu_runtime/README.md`](dsiu_runtime/README.md). |
| `dsiu_uef/` | **DSIU-UEF** — the Universal Execution Fabric (compatibility intelligence: classify + route + sandbox-plan, no execution). See [`dsiu_uef/README.md`](dsiu_uef/README.md). |
| `scripts/build_skill.py` | Validates the bundle and packages it into `dist/dsiu.skill`. |
| `tests/` | Stdlib `unittest` smoke tests (no third-party deps). |
| `examples/dsiu_on_dsiu_field.md` | DSIU's lens turned on its own v1 bundle — a worked Field Template and the rationale for this hardening pass. |
| `.github/workflows/ci.yml` | Runs the tests and builds the `.skill` on every push/PR. |

## The four things this delivers

1. **An executable skill** — the full bundle in `dsiu/`, built reproducibly into
   an installable `.skill`.
2. **A lens you can run on a real codebase** — `scan` mode maps a repo onto the
   intake → processing → output trunk and emits a DRAFT Field Template.
3. **A deterministic scorecard generator** — `scorecard` mode emits the per-layer
   attribute scorecard (qualities / skills / strengths / weaknesses / control
   points) as JSON **and** Markdown, with no model call.
4. **A CPK FINAL hand-off** — `packet` mode emits a Mission-Packet-shaped JSON
   (inputs / hard_locks / failure_bans). DSIU is the *Observe* front-end; CPK
   scores, gates, and executes the upgrade. (CPK FINAL is external to this repo —
   this is the documented contract, not a live call.)

Plus the keystone the framework was missing: **`diff` mode**, DSIU's own feedback
loop — compare two passes and get a movement score, so "DSIU building DSIU"
becomes measurable instead of metaphorical.

## DSIU-OIL — the Operating Intelligence Layer (v0.1)

The discrete modes above are a toolset. **DSIU-OIL** (`dsiu_runtime/`) is the layer
that turns them into one operating loop:

> Observe → Map → Score → Packetize → Supervise → Diff → Feedback → Repeat

```bash
# Run one operating-loop pass over a target (Markdown supervisor report)
python -m dsiu_runtime loop --path ./repo --name "My Repo" --include-docs

# Full artifact bundle (JSON) + report (Markdown); re-run to measure movement
python -m dsiu_runtime loop --path ./repo --name "My Repo" --json report.json --md report.md
```

One pass emits a scorecard, a process graph, a CPK packet, an optional diff, a
policy verdict, and a supervisor report — every artifact `DRAFT`, movement measured
but improvement never claimed, execution dry-run only. This is the brain a future
DSIU shell/OS gets built around; it is **not** itself a kernel, daemon, or OS. Full
details and the phase roadmap: [`dsiu_runtime/README.md`](dsiu_runtime/README.md).

## DSIU-UEF — the Universal Execution Fabric (v0.1)

If OIL is the brain, **DSIU-UEF** (`dsiu_uef/`) is its **compatibility sense**: point
it at a file/folder/repo/manifest/binary and it classifies *what it is*, routes it to
the best execution lane (with fallbacks), flags permission risk, and recommends a
sandbox — as a `DRAFT` compatibility profile. **It does not run anything** (no
Wine/Proton/VM/container/install); it classifies, routes, and plans.

```bash
# Classify a workload (Markdown profile to stdout; or --json/--md)
python -m dsiu_uef intake --path ./some_app

# Attach a compatibility profile to an OIL supervisor pass
python -m dsiu_runtime loop --path ./repo --name "Repo" --include-docs --uef ./some_app
```

Lanes: `native_dsiu`, `linux_native`, `flatpak_appimage`, `windows_wine`,
`windows_proton`, `android_container`, `web_pwa`, `container_runtime`, `vm_runtime`,
`remote_cloud`, `unsupported_unknown`. Details: [`dsiu_uef/README.md`](dsiu_uef/README.md).

## Roadmap

Skill ✅ → OIL ✅ → **UEF ✅** → Shell → Daemon → OS

The compatibility intelligence layer exists; the OS body comes much later, only once
each layer is stable.

## Usage

```bash
# Blank Field Template for any system (code or not)
python dsiu/scripts/dsiu_analyze.py template --name "My System" > my_system.dsiu.md

# Heuristic first-pass map of a codebase (always a DRAFT — verify by hand)
python dsiu/scripts/dsiu_analyze.py scan --path ./repo --name "My Repo" \
    --out repo.dsiu.md --json repo.scorecard.json

# Add --include-docs so knowledge/config-driven systems aren't invisible
python dsiu/scripts/dsiu_analyze.py scan --path ./repo --include-docs --json repo.json

# Structured attribute scorecard for a named system (JSON + Markdown, no scan)
python dsiu/scripts/dsiu_analyze.py scorecard --name "My System" \
    --out my_system.scorecard.md --json my_system.scorecard.json

# Feedback loop: measure what moved between two passes
python dsiu/scripts/dsiu_analyze.py diff --before before.json --after after.json \
    --out delta.md --json delta.json

# Hand-off to CPK FINAL (contract shape)
python dsiu/scripts/dsiu_analyze.py packet --json repo.scorecard.json --out packet.json
```

## Build & test

```bash
python -m unittest discover -s tests   # run the smoke tests
python scripts/build_skill.py          # -> dist/dsiu.skill (installable bundle)
```

Requires Python 3.8+ and nothing else (standard library only).

## Law 0 — Honesty of Claim

DSIU is a lens, not a magic upgrader. `scan`/`diff` output is a **heuristic first
pass**, always marked `DRAFT`, and must be verified by a human before it is acted
on. DSIU **maps, scores, and proposes** — it never claims to have *upgraded*,
*fixed*, or *sealed* anything. Those are real engineering actions taken after the
diagnosis. Full text in `dsiu/references/governance.md`.
