# DSIU-Daemon — v0.1

DSIU-Daemon is the **watcher/supervisor** layer over Shell + OIL + UEF. It observes a
folder/project **over time**: it polls for file changes, triggers a DSIU-Shell
analysis (OIL + optional UEF) only when something changed, records an event history,
tracks movement across runs, and recommends the next action.

**Hard boundary (v0.1):** an explicit, user-started, **foreground** watcher. It only
observes and reports. It does **not** execute apps, install dependencies, launch
Wine/Proton/VM/container/Android, **apply fixes**, or install a permanent system
service. Every output is `DRAFT`; movement measured ≠ improvement.

## Commands

| Command | What it does |
|---|---|
| `once <path>` | One observation cycle (baseline / changed / no_change / error). |
| `watch <path>` | Foreground watch loop (bounded by `--limit`); polls every `--interval` s. |
| `status` | Latest daemon event summary. |
| `history` | Recent daemon events (newest first). |
| `explain last` | Human-readable breakdown of the latest event. |

Flags: `--name`, `--include-docs`, `--uef <workload>`, `--interval` (default 5,
watch), `--limit` (max cycles, watch), `--record-no-change` (watch), `--state-dir`
(default `dsiu_daemon_state/`), `--oil-state-dir` (default `dsiu_state/`).

```bash
python -m dsiu_daemon once dsiu --name "DSIU self" --include-docs
python -m dsiu_daemon watch dsiu --name "DSIU self" --include-docs --limit 1
python -m dsiu_daemon status
python -m dsiu_daemon history
python -m dsiu_daemon explain last
```

## How it observes

- **Change detection** is polling-based (stdlib only — no watchdog). Each file is
  fingerprinted as `mtime_ns:size` plus a short `sha256` for small files, so even
  same-size/same-mtime edits are caught.
- **Snapshots** are persisted per watched path; each cycle loads the previous
  snapshot **before** saving the current one, so a cycle can never compare to itself.
- **Event types:** `baseline` (first pass), `changed` (files moved → analysis runs),
  `no_change` (nothing moved → **no analysis, no movement claim**), `error` (path
  missing/unreadable → a DRAFT error event, never a crash).
- **No-change spam guard:** `watch` records the first `no_change` then suppresses
  repeats until something changes (override with `--record-no-change`).
- **Foreground only:** `watch` prints a notice that no background service is
  installed and runs in the foreground until `--limit` cycles complete or you stop it.

## Events & state

Events are saved under `dsiu_daemon_state/` (gitignored). Each event stores:
timestamp, watched path, event_type, changed files + detail, change summary, whether
analysis ran, `shell_session_path` **and** the raw `shell_session` (full OIL/UEF
trace) when analysis ran, `movement_score` (or none), attached UEF profile (if any),
`law0_status`, and `required_next_action`. `status`/`history`/`explain` are
**read-only** and safe on empty state.

## Law 0 & safety

Every output carries `DRAFT`. Movement measured ≠ improvement; no *upgrade complete /
supported / verified working / fix applied / executed* claims. The daemon only
observes and routes to existing DSIU APIs — it never uses `subprocess`, `os.system`,
`os.popen`, `exec`, `eval`, `pty`, `shutil.which`, or any app-launch/install
mechanism (enforced by a source-scan test). Polling uses `time.sleep` only.

## Roadmap

Skill ✅ → OIL ✅ → UEF ✅ → Shell ✅ → **Daemon ✅ (you are here)** → OS

Daemon is the continuous-observation organ — the last major organ before the first
OS-seed phase. It is not a permanent OS service yet; that comes much later, only once
each layer is stable.
