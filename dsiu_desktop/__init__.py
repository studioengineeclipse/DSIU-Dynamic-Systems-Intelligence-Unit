"""DSIU-Desktop Layer — the first local workspace / control surface over DSIU.

OS-Seed tells the system *what DSIU is*; the Desktop Layer gives the user a
*workspace to operate it*: a read-only dashboard that organizes organs, state,
sessions, daemon events, compatibility profiles, readiness, roadmap, and the next
recommended action into one operating-environment surface.

Hard boundary (v0.1): a read-only dashboard/workspace scaffold (CLI + Markdown/JSON,
not a GUI). It does NOT boot, install, execute, launch apps, watch, replace the host
OS, or run any organ command (no Shell inspect/profile/analyze, no Daemon once/watch,
no OIL/UEF analysis). It reads organ state + OS-Seed pure functions and writes only
its own desktop state. Every artifact is DRAFT (Law 0); no execution performed.
"""

__version__ = "0.1"
DESKTOP_VERSION = "DSIU-Desktop Layer v0.1"
DRAFT_STAMP = "DRAFT"

DESKTOP_STATE_DIR = "dsiu_desktop_state"
DESKTOP_STATE_VERSION = "dsiu.desktop_state/v0.1"
