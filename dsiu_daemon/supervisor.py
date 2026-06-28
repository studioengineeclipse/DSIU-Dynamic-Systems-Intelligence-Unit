"""Supervisor — the observation core.

Thin: it detects change (watch.py), routes analysis to DSIU-Shell when something
changed, and records events (events.py). It never executes, installs, or fixes.
"""

from __future__ import annotations

import os
import time

from . import EVENT_BASELINE, EVENT_CHANGED, EVENT_ERROR, EVENT_NO_CHANGE
from . import events as _events
from . import watch as _watch


def _run_shell(config):
    """Route to the Shell command layer (which chains OIL + optional UEF)."""
    from dsiu_shell import commands as C
    if config.uef_path:
        session = C.analyze(config.path, name=config.name,
                            include_docs=config.include_docs,
                            with_path=config.uef_path,
                            state_dir=config.shell_state_dir,
                            oil_state_dir=config.oil_state_dir)
    else:
        session = C.inspect(config.path, name=config.name,
                           include_docs=config.include_docs,
                           state_dir=config.shell_state_dir,
                           oil_state_dir=config.oil_state_dir)
    # save_session writes session-<timestamp>.json deterministically.
    path = os.path.join(config.shell_state_dir,
                        f"session-{session.get('timestamp')}.json")
    return session, (path if os.path.isfile(path) else None)


def run_once(config, suppress_no_change: bool = False) -> dict:
    """One observation cycle. Always returns an event; `_event_path` is the saved
    path or None (None when a redundant no_change was suppressed)."""
    slug = config.slug()
    prev = _events.load_snapshot(config.state_dir, slug)

    # Detect change; a missing/unreadable path becomes a DRAFT error event.
    try:
        new = _watch.snapshot(config.path)
    except OSError as exc:
        event = _events.build_event(
            config, EVENT_ERROR, {"changed_files": []},
            f"cannot read watched path: {exc}", error=str(exc))
        event["_event_path"] = _events.save_event(config.state_dir, event)
        return event

    change = _watch.diff(prev, new)
    _events.save_snapshot(config.state_dir, slug, new)

    if prev is None:
        event_type = EVENT_BASELINE
        summary = "baseline observation — first pass on this path"
        analyze = True
    elif change["changed_files"]:
        event_type = EVENT_CHANGED
        summary = (f"{len(change['changed_files'])} file(s) changed "
                   f"(+{len(change['added'])} / -{len(change['removed'])} / "
                   f"~{len(change['modified'])})")
        analyze = True
    else:
        event_type = EVENT_NO_CHANGE
        summary = "no changes detected"
        analyze = False

    if analyze:
        session, session_path = _run_shell(config)
        event = _events.build_event(config, event_type, change, summary,
                                    session=session,
                                    shell_session_path=session_path)
    else:
        event = _events.build_event(config, event_type, change, summary)

    # No-change spam guard: skip saving a redundant no_change unless requested.
    if (event_type == EVENT_NO_CHANGE and suppress_no_change
            and not config.record_no_change):
        event["_event_path"] = None
        return event

    event["_event_path"] = _events.save_event(config.state_dir, event)
    return event


def run_watch(config, max_cycles: "int | None" = None) -> list:
    """Foreground watch loop. Bounded by max_cycles (from --limit) for explicit/
    testable runs. Suppresses consecutive duplicate no_change events."""
    events = []
    standing_no_change = False
    cycle = 0
    while max_cycles is None or cycle < max_cycles:
        ev = run_once(config, suppress_no_change=standing_no_change)
        events.append(ev)
        if ev["event_type"] == EVENT_NO_CHANGE:
            standing_no_change = True
        else:
            standing_no_change = False
        cycle += 1
        last = (max_cycles is not None and cycle >= max_cycles)
        if not last and config.interval > 0:
            time.sleep(config.interval)
    return events
