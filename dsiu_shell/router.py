"""Router — the only place the shell reaches into OIL and UEF.

Thin orchestration: it calls the existing organ APIs and returns their artifacts.
It does not analyze, classify, or execute anything itself.
"""

from __future__ import annotations

from . import OIL_STATE_DIR


def run_inspect(path: str, name: "str | None", include_docs: bool,
                oil_state_dir: str = OIL_STATE_DIR) -> dict:
    """OIL operating-loop pass (no UEF)."""
    from dsiu_runtime.loop import run_loop
    return run_loop(path, name=name, state_dir=oil_state_dir,
                    include_docs=include_docs)


def run_analyze(path: str, name: "str | None", include_docs: bool,
                with_path: str, oil_state_dir: str = OIL_STATE_DIR) -> dict:
    """OIL operating-loop pass with an attached UEF compatibility profile."""
    from dsiu_runtime.loop import run_loop
    return run_loop(path, name=name, state_dir=oil_state_dir,
                    include_docs=include_docs, uef_path=with_path)


def run_profile(path: str) -> dict:
    """UEF compatibility profile only (no OIL)."""
    from dsiu_uef.profile import build_profile
    return build_profile(path)
