"""Policy gate layer — Law 0, enforced.

Two jobs:

1. Every artifact the loop emits must carry the DRAFT stamp (scorecard, graph,
   packet, diff, supervisor report, policy verdict, execute stub).
2. The loop may report **measured movement** but must never claim a verified
   **improvement** or a completed upgrade. Movement is change; improvement is a
   judgement v0.1 is not allowed to make.
"""

from __future__ import annotations

from datetime import date

from .engine import DRAFT_STAMP

# Wording the engine must never emit as a claim.
FORBIDDEN_CLAIMS = (
    "upgrade completed", "upgrade complete", "system fixed", "fixed the",
    "weakness solved", "confirmed improvement", "improved the system",
    "successfully upgraded",
)

# Wording that is allowed (honest, non-asserting).
ALLOWED_WORDING = (
    "candidate weakness", "proposed control point", "movement measured",
    "direction unverified", "requires review", "DRAFT",
)


def has_draft_stamp(artifact) -> bool:
    """True if an artifact carries the DRAFT stamp in its status/text."""
    if artifact is None:
        return True  # absent artifact (e.g. no diff on first pass) is fine
    if isinstance(artifact, dict):
        status = str(artifact.get("status", ""))
        return DRAFT_STAMP in status
    return DRAFT_STAMP in str(artifact)


def enforce_draft(**artifacts) -> list:
    """Return a list of names of artifacts missing the DRAFT stamp."""
    return [name for name, art in artifacts.items() if not has_draft_stamp(art)]


def build_policy_verdict(diff: "dict | None", draft_violations: list) -> dict:
    """The policy verdict — itself a DRAFT artifact."""
    movement_measured = bool(diff) and diff.get("movement_score", 0) > 0
    return {
        "kind": "policy_verdict",
        "status": f"{DRAFT_STAMP} — Law 0 policy verdict (routing signal, not a verdict on truth)",
        "date": date.today().isoformat(),
        "law_0": "enforced",
        "draft_ok": not draft_violations,
        "draft_violations": draft_violations,
        # The core hard-lock: movement != improvement.
        "movement_measured": movement_measured,
        "movement_score": (diff or {}).get("movement_score") if diff else None,
        "improvement_claim_allowed": False,
        "upgrade_claim_allowed": False,
        "direction": "unverified",
        "reason": (
            "v0.1 measures that the system changed, never that it improved. "
            "An improvement evaluator is a later phase. No artifact may claim an "
            "upgrade was completed."
        ),
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        "allowed_wording": list(ALLOWED_WORDING),
    }
