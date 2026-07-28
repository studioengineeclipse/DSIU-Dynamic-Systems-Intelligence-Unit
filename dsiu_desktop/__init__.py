"""DSIU-Desktop Layer — the first local workspace / control surface over DSIU.

OS-Seed tells the system *what DSIU is*; the Desktop Layer gives the user a
*workspace to operate it*: a read-only dashboard that organizes organs, state,
sessions, daemon events, compatibility profiles, readiness, roadmap, and the next
recommended action into one operating-environment surface.

v0.2 adds the first actual interface surface: a text-UI dashboard (`tui`) that renders
the same read-only state as a bordered full-screen text frame. A frame is a *snapshot*
taken at invocation time — the text UI still does NOT watch (no timers/threads/polling);
its optional interactive viewer redraws only on an explicit user keypress.

Hard boundary: a read-only dashboard/workspace surface (CLI + Markdown/JSON + text-UI
snapshot, not a GUI). It does NOT boot, install, execute, launch apps, watch, replace
the host OS, or run any organ command (no Shell inspect/profile/analyze, no Daemon
once/watch, no OIL/UEF analysis). It reads organ state + OS-Seed pure functions and
writes only its own desktop state. Every artifact is DRAFT (Law 0); no execution
performed.
"""

__version__ = "0.2"
DESKTOP_VERSION = "DSIU-Desktop Layer v0.2"
DRAFT_STAMP = "DRAFT"

DESKTOP_STATE_DIR = "dsiu_desktop_state"
DESKTOP_STATE_VERSION = "dsiu.desktop_state/v0.1"
