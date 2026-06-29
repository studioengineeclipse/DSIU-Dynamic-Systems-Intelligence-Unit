# DSIU-Desktop Layer — v0.1

DSIU-Desktop Layer is the first local **workspace / control surface** over DSIU.
OS-Seed tells the system *what DSIU is*; the Desktop Layer gives the user a
*workspace to operate it* — a read-only dashboard that organizes organs, state,
sessions, daemon events, compatibility profiles, readiness, roadmap, and the next
recommended action into one operating-environment surface.

**Hard boundary (v0.1):** a read-only dashboard/workspace scaffold (CLI + Markdown/
JSON, **not a GUI**). It does **not** boot, install, execute, launch apps, watch, or
replace the host OS, and it does **not** run any organ command (no Shell
inspect/profile/analyze, no Daemon once/watch, no OIL/UEF analysis). It **reads**
organ state + OS-Seed pure functions and **writes only its own** desktop state. Every
artifact is `DRAFT`; `no_execution_performed: true`.

## Commands

| Command | What it does |
|---|---|
| `overview` | Organs · roadmap phase · latest shell session · latest daemon event · OS-Seed readiness · next action. |
| `workspace add <path> [--name]` | Registers a workspace path (registration only — no analyze/watch). |
| `workspace list` | Lists registered workspaces. |
| `dashboard [--json] [--md]` | Builds a DRAFT desktop dashboard artifact (also saved to desktop state). |
| `status` | Workspace count · known organs · latest shell/daemon · Law-0 status. |
| `roadmap [--json] [--md]` | The phased OS path. |

`--state-dir` (default `dsiu_desktop_state/`) is available on every command.

```bash
python -m dsiu_desktop overview
python -m dsiu_desktop workspace add ./repo --name "Repo"
python -m dsiu_desktop workspace list
python -m dsiu_desktop dashboard --json desktop.json --md desktop.md
python -m dsiu_desktop status
python -m dsiu_desktop roadmap
```

## What it reads vs. writes

**Reads (read-only):** OS-Seed pure functions (`manifest`, `readiness`, `topology`,
`ROADMAP`), the latest Shell session (`dsiu_shell_state/`), the latest Daemon event
(`dsiu_daemon_state/`), and UEF compatibility from whichever of those is present.

**Writes (its own state only):** `dsiu_desktop_state/registered_workspaces.json` and
`latest_dashboard.json` (gitignored).

It never triggers analysis or observation — to produce new sessions/events, you run
the Shell or Daemon yourself, then refresh the dashboard.

## Law 0

Every output carries `DRAFT` and `no_execution_performed: true`. No command claims
*desktop ready / OS complete / bootable / installed / app executed / system fixed /
upgrade complete*. Allowed wording: *desktop scaffold, workspace layer, dashboard
candidate, operating environment surface, no execution performed, requires
validation.* Enforced by a source-scan test (no subprocess/os.system/os.popen/
shutil.which/exec/eval/pty).

## Roadmap

Skill ✅ → OIL ✅ → UEF ✅ → Shell ✅ → Daemon ✅ → OS-Seed ✅ →
**Desktop Layer ✅ (you are here)** → Linux Distribution → Native OS research

The Desktop Layer is the first step toward a future DSIU operating-environment UI.
The next phase candidate is a DSIU Linux-based environment — built much later, only
once each layer is stable.
