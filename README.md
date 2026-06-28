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
| `dsiu_shell/` | **DSIU-Shell** — the user-facing command cockpit over OIL + UEF (inspect / profile / analyze / status / history / explain). See [`dsiu_shell/README.md`](dsiu_shell/README.md). |
| `dsiu_daemon/` | **DSIU-Daemon** — the explicit foreground watcher/supervisor that observes folders over time and triggers analysis on change (no execution). See [`dsiu_daemon/README.md`](dsiu_daemon/README.md). |
| `dsiu_os_seed/` | **DSIU-OS-Seed** — the operating-environment scaffold / control plane over the five organs (manifest / topology / readiness / status / roadmap; read-only). See [`dsiu_os_seed/README.md`](dsiu_os_seed/README.md). |
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

## DSIU-Shell — the command cockpit (v0.1)

**DSIU-Shell** (`dsiu_shell/`) is the single front door over OIL + UEF — so you stop
thinking in modules. It routes commands into the organs, records each session, and
shows status/history/explanations. It is **thin**: it does not analyze, classify, or
execute anything itself.

```bash
python -m dsiu_shell inspect ./repo --name "Repo" --include-docs   # OIL loop
python -m dsiu_shell profile ./app.exe                              # UEF profile
python -m dsiu_shell analyze ./repo --with ./app.exe               # OIL + UEF
python -m dsiu_shell status        # latest session summary
python -m dsiu_shell history       # recent sessions
python -m dsiu_shell explain last  # human-readable breakdown
```

Sessions are saved under `dsiu_shell_state/` (gitignored). Read commands are
read-only and safe on empty state. Details: [`dsiu_shell/README.md`](dsiu_shell/README.md).

## DSIU-Daemon — continuous observation (v0.1)

**DSIU-Daemon** (`dsiu_daemon/`) watches a folder/project **over time**: it polls for
changes and, only when something changed, triggers a Shell analysis (OIL + optional
UEF), recording an event history and tracking movement. It is an explicit,
**foreground**, observe-and-report watcher — no background service, no execution, no
fixes.

```bash
python -m dsiu_daemon once ./repo --name "Repo" --include-docs   # one cycle
python -m dsiu_daemon watch ./repo --include-docs --limit 1      # bounded foreground loop
python -m dsiu_daemon status        # latest event
python -m dsiu_daemon history       # recent events
python -m dsiu_daemon explain last  # human-readable breakdown
```

Event types: `baseline` / `changed` / `no_change` (no fake movement) / `error`.
Events are saved under `dsiu_daemon_state/` (gitignored). Details:
[`dsiu_daemon/README.md`](dsiu_daemon/README.md).

## DSIU-OS-Seed — the control plane (v0.1)

**DSIU-OS-Seed** (`dsiu_os_seed/`) unifies the five organs into one documented
operating environment — a read-only control plane. It is the bridge between DSIU as
tools and DSIU as an operating environment. It does **not** boot, install, execute,
or replace the host OS.

```bash
python -m dsiu_os_seed manifest     # organs, versions, capabilities, boundaries
python -m dsiu_os_seed topology     # how the organs connect (+ future OS nodes)
python -m dsiu_os_seed readiness    # DRAFT readiness report (detected, not validated)
python -m dsiu_os_seed status       # operating-environment summary
python -m dsiu_os_seed roadmap      # the phased OS path
```

Every command supports `--json`/`--md`. Details:
[`dsiu_os_seed/README.md`](dsiu_os_seed/README.md).

## Roadmap

Skill ✅ → OIL ✅ → UEF ✅ → Shell ✅ → Daemon ✅ → **OS-Seed ✅** → Desktop Layer → OS

Six layers now exist (five organs + the control-plane scaffold); the OS body comes
much later, only once each layer is stable.

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
