# DSIU-Shell — v0.1

DSIU-Shell is the **user-facing command cockpit** over the organs already built —
DSIU-OIL (the operating intelligence loop) and DSIU-UEF (the compatibility fabric).
It gives DSIU a single front door so you stop thinking in modules.

Before:
```bash
python -m dsiu_runtime loop ...
python -m dsiu_uef intake ...
```
After:
```bash
python -m dsiu_shell inspect ./repo
python -m dsiu_shell profile ./app.exe
python -m dsiu_shell analyze ./repo --with ./app.exe
```

**Hard boundary (v0.1):** the shell is **thin** — it routes, renders, and records
sessions. It does **not**: analyze or classify directly (that's OIL/UEF), execute
apps, install dependencies, launch Wine/Proton/VM/container/Android, run a
background watcher, or replace the OS. Every output is `DRAFT` (Law 0).

## Commands

| Command | What it does |
|---|---|
| `inspect <path>` | Runs the OIL operating loop and prints the supervisor report. |
| `profile <path>` | Runs UEF intake and prints the compatibility profile. |
| `analyze <path> --with <workload>` | Runs OIL with an attached UEF profile. |
| `status` | Latest session: last target, detected layers, UEF lane, movement score, Law-0 status, next action. |
| `history` | Lists recent sessions (newest first). |
| `explain last` | Human-readable breakdown of the latest session. |

Common flags: `--name`, `--include-docs`, `--state-dir` (default `dsiu_shell_state/`),
and `--oil-state-dir` (default `dsiu_state/`, for commands that call OIL).

```bash
python -m dsiu_shell inspect dsiu --name "DSIU self" --include-docs
python -m dsiu_shell profile tests/fixtures/uef/windows_app.exe
python -m dsiu_shell analyze dsiu --name "DSIU self" --include-docs --with tests/fixtures/uef/windows_app.exe
python -m dsiu_shell status
python -m dsiu_shell history --limit 10
python -m dsiu_shell explain last
```

## Sessions & state

Write commands (`inspect`, `profile`, `analyze`) save a session under
`dsiu_shell_state/` (gitignored). Each session stores the **rendered summary** plus
the **raw artifacts** — the OIL supervisor report and/or the UEF profile — so the
shell can show quick status/history while preserving the full trace, including
`law0_status` and `required_next_action`.

Read commands (`status`, `history`, `explain last`) are **read-only** — they never
create sessions, and they return a safe `DRAFT` "no sessions found" message when the
state is empty (no stack traces). OIL keeps its own feedback memory in `dsiu_state/`,
so movement still accumulates across `inspect`/`analyze` runs.

## Law 0

Every shell output carries `DRAFT`. No command claims *upgrade complete, supported,
verified working, app executed, system fixed*. Allowed wording: *DRAFT, candidate,
recommended lane, likely runtime, movement measured, direction unverified, execution
not performed, requires validation.* The shell executes nothing — it orchestrates
OIL (dry-run only) and UEF (classification only).

## Roadmap

Skill ✅ → OIL ✅ → UEF ✅ → **Shell ✅ (you are here)** → Daemon → OS

The shell is the first command/control surface for the future DSIU operating
environment. The next phase, **DSIU-Daemon**, would watch projects/folders over
time — but not yet. The OS body comes much later, once each layer is stable.
