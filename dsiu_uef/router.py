"""Router — map a detected workload type to candidate execution lanes.

Returns a *recommended* primary lane plus fallbacks. These are candidates, never a
"supported" guarantee (Law 0) — nothing is executed to verify them.
"""

from __future__ import annotations

from . import lanes as L


def route(detected_type: str, signals: dict):
    """Return (primary_lane, [fallback_lanes], [unsupported_reasons])."""
    primary, fallbacks = L.LANE_TABLE.get(
        detected_type, (L.UNSUPPORTED_UNKNOWN, ()))

    unsupported_reasons = []
    if detected_type == L.UNKNOWN or primary == L.UNSUPPORTED_UNKNOWN:
        if not signals.get("exists", True):
            unsupported_reasons.append(
                "workload path does not exist — name-only, no signals to classify.")
        unsupported_reasons.append(
            "no recognized type, manifest, or magic signature — execution not "
            "performed; requires manual validation.")

    return primary, list(fallbacks), unsupported_reasons
