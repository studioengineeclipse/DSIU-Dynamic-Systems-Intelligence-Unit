"""Commands — the shell's programmatic API.

Write commands (inspect / profile / analyze) orchestrate the organs, render a
summary, and save a session. Read commands (status / history / explain_last) only
read saved sessions and never write.
"""

from __future__ import annotations

from . import OIL_STATE_DIR, SHELL_STATE_DIR
from . import history as _history
from . import render as _render
from . import router as _router
from . import session as _session


# --- write commands (create + save a session) --------------------------------

def inspect(path: str, name: "str | None" = None, include_docs: bool = False,
            state_dir: str = SHELL_STATE_DIR,
            oil_state_dir: str = OIL_STATE_DIR) -> dict:
    bundle = _router.run_inspect(path, name, include_docs, oil_state_dir)
    sess = _session.build_session("inspect", path,
                                  summary="", oil_bundle=bundle)
    sess["rendered_summary"] = _render.render_command_report(sess)
    _session.save_session(state_dir, sess)
    return sess


def profile(path: str, state_dir: str = SHELL_STATE_DIR) -> dict:
    prof = _router.run_profile(path)
    sess = _session.build_session("profile", path,
                                  summary="", uef_profile=prof)
    sess["rendered_summary"] = _render.render_command_report(sess)
    _session.save_session(state_dir, sess)
    return sess


def analyze(path: str, name: "str | None" = None, include_docs: bool = False,
            with_path: "str | None" = None, state_dir: str = SHELL_STATE_DIR,
            oil_state_dir: str = OIL_STATE_DIR) -> dict:
    if not with_path:
        raise ValueError("analyze requires --with <workload>")
    bundle = _router.run_analyze(path, name, include_docs, with_path, oil_state_dir)
    sess = _session.build_session("analyze", path, summary="",
                                  oil_bundle=bundle,
                                  uef_profile=bundle.get("uef_profile"))
    sess["rendered_summary"] = _render.render_command_report(sess)
    _session.save_session(state_dir, sess)
    return sess


# --- read commands (no writes) -----------------------------------------------

def status(state_dir: str = SHELL_STATE_DIR) -> "dict | None":
    return _history.latest_session(state_dir)


def history(state_dir: str = SHELL_STATE_DIR, limit: int = 10) -> list:
    return _history.list_sessions(state_dir, limit=limit)


def explain_last(state_dir: str = SHELL_STATE_DIR) -> "dict | None":
    return _history.latest_session(state_dir)
