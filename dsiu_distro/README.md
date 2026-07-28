# DSIU-Distro — v0.1

DSIU-Distro is the **Linux-distribution scaffold** — the next roadmap phase after the
Desktop Layer. OS-Seed describes *what DSIU is* as an operating environment; DSIU-Distro
describes *what a DSIU Linux distribution would be* if that environment were packaged as
a bootable OS image: a component/package set, a boot topology, and an image build plan.

**Hard boundary (v0.1):** a read-only spec/manifest scaffold (CLI + Markdown/JSON). It
does **not** build an image, produce an ISO/qcow2/raw file, install packages, run a
package manager, build a kernel, boot anything, or execute any workload. It **reuses**
the OS-Seed organ registry to describe the five DSIU organs *as* distribution
components (it does not re-list them). Every artifact is `DRAFT`; `no_build_performed`
and `no_image_built` are always true.

## Commands

| Command | What it does |
|---|---|
| `manifest` | Ties packages + boot + image into one distribution description (references OS-Seed). |
| `packages` | The planned component/package set: 5 organs as components + base system. |
| `boot` | The planned boot topology — the ordered layer stack (firmware → … → Desktop-TUI). |
| `image` | The planned image build stages + target formats (`iso`/`qcow2`/`raw`, all planned). |
| `status` | Component/boot/image counts, current + next phase, Law-0 status. |
| `roadmap` | The phased OS path. |

Every command supports `--json`/`--md`; default writes Markdown to stdout.

```bash
python -m dsiu_distro manifest
python -m dsiu_distro packages --json packages.json --md packages.md
python -m dsiu_distro boot
python -m dsiu_distro image
python -m dsiu_distro status
python -m dsiu_distro roadmap
```

## What it reads vs. builds

**Reads (read-only):** `dsiu_os_seed.registry.ORGANS` (organ components) and
`dsiu_os_seed.ROADMAP` (roadmap). Base components, boot stages, and image stages are
declared as pure data in this package.

**Builds:** nothing. No image is emitted, no package is installed, nothing is booted.
To actually build a distribution image, a human runs a real image pipeline later — this
is the documented plan it would follow, not the pipeline itself.

## Law 0

Every output carries `DRAFT`. No command claims *bootable / iso built / image built /
distro ready / installed / kernel built / os complete*. Allowed wording: *distribution
scaffold, package plan, boot topology, image plan, build stage, planned target, no
image built, no execution performed, requires validation.* Enforced by a source-scan
test (no subprocess/os.system/os.popen/shutil.which/exec/eval/pty) and a
forbidden-claims scan over every render.

## Roadmap

Skill ✅ → OIL ✅ → UEF ✅ → Shell ✅ → Daemon ✅ → OS-Seed ✅ → Desktop Layer ✅ →
**Linux Distribution 🟡 (you are here — scaffold)** → Native OS research

The distribution is the first step toward shipping DSIU as an installable operating
environment — built much later, only once each layer is stable.
