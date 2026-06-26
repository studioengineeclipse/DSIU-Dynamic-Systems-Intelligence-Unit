"""Engine loader — the single place that imports the DSIU skill engine.

DSIU-OIL is a layer *above* the installable skill. It reuses every analysis
primitive from `dsiu/scripts/dsiu_analyze.py` (no engine code is moved or
rewritten) by putting that directory on sys.path — the same shim
`tests/test_dsiu_analyze.py` uses. Every other runtime module imports the engine
from here, so the path coupling lives in exactly one file.
"""

from __future__ import annotations

import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENGINE_DIR = os.path.join(_REPO_ROOT, "dsiu", "scripts")
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

import dsiu_analyze as _engine  # noqa: E402

# Re-exported primitives (the only DSIU engine surface OIL depends on).
LAYERS = _engine.LAYERS
ATTRIBUTE_LAYERS = _engine.ATTRIBUTE_LAYERS
DRAFT_STAMP = _engine.DRAFT_STAMP

walk_repo = _engine.walk_repo
classify = _engine.classify
build_scorecard = _engine.build_scorecard
build_attribute_layers = _engine.build_attribute_layers
build_diff = _engine.build_diff
build_packet = _engine.build_packet

REPO_ROOT = _REPO_ROOT

__all__ = [
    "LAYERS", "ATTRIBUTE_LAYERS", "DRAFT_STAMP", "REPO_ROOT",
    "walk_repo", "classify", "build_scorecard", "build_attribute_layers",
    "build_diff", "build_packet",
]
