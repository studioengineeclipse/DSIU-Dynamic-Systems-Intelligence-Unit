"""Profile builder — assemble the full DRAFT compatibility profile.

Orchestrates intake -> classify -> router -> sandbox into one artifact carrying
every required field. No execution anywhere in this path.
"""

from __future__ import annotations

from datetime import date

from . import DRAFT_STAMP
from . import classify as _classify
from . import intake as _intake
from . import router as _router
from . import sandbox as _sandbox


def build_profile(path: str) -> dict:
    signals = _intake.gather(path)
    detected = _classify.detect(signals)
    primary, fallbacks, unsupported = _router.route(detected["detected_type"], signals)
    risk, sandbox_reco = _sandbox.assess(detected["detected_type"], signals)

    next_action = _next_action(detected["detected_type"], primary, unsupported)

    return {
        "kind": "uef_compatibility_profile",
        "status": f"{DRAFT_STAMP} — classification only; execution not performed (Law 0)",
        "date": date.today().isoformat(),
        # required classification fields
        "workload_name": signals["workload_name"],
        "workload_path": signals["workload_path"],
        "detected_type": detected["detected_type"],
        "target_os": detected["target_os"],
        "cpu_architecture_signal": signals["cpu_architecture_signal"],
        "file_or_manifest_type": detected["file_or_manifest_type"],
        "runtime_requirements": detected["runtime_requirements"],
        "dependency_signals": detected["dependency_signals"],
        "gpu_requirement_signal": detected["gpu_requirement_signal"],
        "network_requirement_signal": detected["network_requirement_signal"],
        "filesystem_requirement_signal": detected["filesystem_requirement_signal"],
        "permission_risk": risk,
        "sandbox_recommendation": sandbox_reco,
        "primary_execution_lane": primary,
        "fallback_execution_lanes": fallbacks,
        "unsupported_reasons": unsupported,
        "confidence": detected["confidence"],
        "required_next_action": next_action,
    }


def _next_action(detected_type: str, primary: str, unsupported: list) -> str:
    if unsupported:
        return ("Unsupported unknown — manually identify the workload, then re-run "
                "intake. Execution not performed.")
    return (f"Candidate lane '{primary}' recommended (requires validation). "
            "Hand the profile to the OIL supervisor; do not execute until a lane "
            "is validated.")
