"""DSIU-Shell — the user-facing command cockpit over OIL + UEF.

One front door instead of separate module commands. The shell routes intent into
the operating loop (OIL) and the compatibility fabric (UEF), records each session,
shows status/history, and explains the last report.

Hard boundary (v0.1): the shell is thin. It routes, renders, and records sessions.
It does NOT analyze or classify directly (that is OIL/UEF), does NOT execute apps,
install dependencies, launch Wine/Proton/VM/container/Android, run a background
watcher, or replace the OS. Every output stays DRAFT (Law 0).
"""

__version__ = "0.1"
SHELL_VERSION = "DSIU-Shell v0.1"
DRAFT_STAMP = "DRAFT"

SHELL_STATE_DIR = "dsiu_shell_state"   # where shell sessions are saved
OIL_STATE_DIR = "dsiu_state"           # where OIL feedback memory is saved

EMPTY_STATE_MESSAGE = (
    f"{DRAFT_STAMP} — No shell sessions found yet. Run `inspect`, `profile`, or "
    "`analyze` first. Execution not performed."
)
