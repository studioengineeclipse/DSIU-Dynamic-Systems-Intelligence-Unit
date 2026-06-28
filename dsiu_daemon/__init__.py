"""DSIU-Daemon — the explicit watcher/supervisor over Shell + OIL + UEF.

The continuous-observation organ: it watches a folder/project over time, detects
file changes by polling, triggers a DSIU-Shell analysis (OIL + optional UEF) only
when something changed, records an event history, tracks movement across runs, and
recommends the next action.

Hard boundary (v0.1): an explicit, user-started, FOREGROUND watcher. It only
observes and reports. It does NOT execute apps, install dependencies, launch
Wine/Proton/VM/container/Android, apply fixes, or install itself as a permanent
system service. Every output stays DRAFT (Law 0); movement measured ≠ improvement.
"""

__version__ = "0.1"
DAEMON_VERSION = "DSIU-Daemon v0.1"
DRAFT_STAMP = "DRAFT"

DAEMON_STATE_DIR = "dsiu_daemon_state"
DEFAULT_INTERVAL = 5  # seconds between polls in watch mode

# Event taxonomy.
EVENT_BASELINE = "baseline"
EVENT_CHANGED = "changed"
EVENT_NO_CHANGE = "no_change"
EVENT_ERROR = "error"

EMPTY_STATE_MESSAGE = (
    f"{DRAFT_STAMP} — No daemon events yet. Run `once` or `watch` first. "
    "Observation only; no execution performed."
)

FOREGROUND_NOTICE = (
    f"{DAEMON_VERSION} running in foreground observation mode. "
    "No background service installed. No execution performed."
)
