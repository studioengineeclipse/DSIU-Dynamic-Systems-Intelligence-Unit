# DSIU-OS-Seed — v0.1

DSIU-OS-Seed is the **operating-environment scaffold / control plane** over the five
DSIU organs (Skill, OIL, UEF, Shell, Daemon). It is the bridge between *DSIU as a set
of tools* and *DSIU as an operating environment*: it describes what exists, what each
organ contributes, how they connect, what state they keep, what policies govern them,
and what is still missing before desktop/OS work.

**Hard boundary (v0.1):** read-only introspection + documentation. It does **not**
boot, install, execute, launch apps, build a kernel, create a desktop, run a package
manager, or replace the host OS. It imports organ modules only to read metadata — it
runs none of their commands. Every artifact is `DRAFT` (Law 0); it never claims an OS
exists, is bootable, installed, or ready.

## Commands

| Command | What it emits |
|---|---|
| `manifest` | The system manifest: each organ's version, purpose, capabilities, CLI, state dir, execution boundary, future OS role. |
| `topology` | The operating topology: organ nodes + future OS nodes, edges, and data/control/feedback/state flows. |
| `readiness` | A DRAFT readiness report: organs detected, command surfaces, tests, state dirs known, build present, readiness level. |
| `status` | A summary: organs present, capabilities available, known state dirs, Law-0 status, next-phase recommendation. |
| `roadmap` | The phased path: Skill → OIL → UEF → Shell → Daemon → OS-Seed → Desktop Layer → … |

Every command supports `--json <path>` and `--md <path>`; default writes Markdown to
stdout.

```bash
python -m dsiu_os_seed manifest
python -m dsiu_os_seed topology
python -m dsiu_os_seed readiness
python -m dsiu_os_seed status
python -m dsiu_os_seed roadmap
python -m dsiu_os_seed manifest --json os_seed.json --md os_seed.md
```

## Capability registry

OS-Seed is more than a module list — each organ declares what it contributes:

- **Skill:** doctrine · scan · scorecard · packet · diff
- **OIL:** loop · process graph · supervisor report · state feedback · diff/movement
- **UEF:** workload classification · lane routing · sandbox recommendation · compatibility profile
- **Shell:** inspect · profile · analyze · status · history · explain
- **Daemon:** once · watch · event history · change detection

## Readiness & state

Readiness imports each organ (metadata only) and checks file existence — it never
runs a command, a test, the build script, or a subprocess; it reports what is
*detected*, not *validated by execution*. State directories (`dsiu_state/`,
`dsiu_shell_state/`, `dsiu_daemon_state/`) are treated as **known** even when not yet
present — they are created on use, so absence is not a missing organ. The
`os_readiness_level` is always a DRAFT scaffold label (e.g. *seed-scaffold-complete
(candidate)*) — never "ready", "complete", or "production-ready".

## Law 0

Every artifact carries `DRAFT`. No command claims *OS complete / bootable / installed
/ kernel built / desktop ready / app executed / system fixed / upgrade complete*.
Allowed wording: *OS seed, scaffold, readiness candidate, operating environment map,
future OS role, requires validation, no execution performed.*

## Roadmap

Skill ✅ → OIL ✅ → UEF ✅ → Shell ✅ → Daemon ✅ → **OS-Seed ✅** → Desktop Layer ✅ →
**Linux Distribution 🟡 (scaffold)** → Native OS research

OS-Seed gives the system a formal map of itself. The Desktop Layer (now with a text
UI) and the **DSIU-Distro** Linux-distribution scaffold (`dsiu_distro/`) build on it;
a real bootable image and the OS body come much later, only once each layer is stable.
