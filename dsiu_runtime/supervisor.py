"""Execution Supervisor — the operating layer's read-out.

Assembles the supervisor report: what was analyzed, what structure was detected,
candidate weaknesses, control points, the proposed mission packet, the required
next action, and (only if a prior pass exists) the movement score.

Execution itself is **dry-run only by default**. `--execute` records a gated,
supervised no-op — it performs no live change and claims no upgrade. The
universal execution fabric (UEF) that would actually route/run changes is a later
phase; here it is only a reserved seam.
"""

from __future__ import annotations

from datetime import date

from . import OIL_VERSION
from .engine import DRAFT_STAMP, LAYERS

# Reserved seam — intentionally inert in v0.1 (no Wine/Proton/container/VM/agent
# routing here). Documented so later phases have a named slot to fill.
EXECUTION_SEAM = {
    "execution_supervisor": "dry_run_only",
    "future_execution_fabric": "reserved",
}


def required_next_action(diff, policy_verdict) -> str:
    if not policy_verdict.get("draft_ok", True):
        return ("Fix Law-0 DRAFT stamping on the flagged artifacts before acting "
                "on this report.")
    if diff is None:
        return ("No prior pass on record. Make a change, then re-run the loop to "
                "measure movement against this baseline.")
    if policy_verdict.get("movement_measured"):
        return ("Movement measured (direction unverified). Review the diff, then "
                "hand the proposed mission packet to an agent or human for the "
                "next supervised pass.")
    return ("No movement since the last pass. Address the candidate weaknesses / "
            "fill the quality ratings, then re-run the loop.")


def build_supervisor_report(target: str, scorecard: dict, graph: dict,
                            packet: dict, diff, policy_verdict: dict,
                            execute_record=None, uef_profile=None) -> dict:
    counts = scorecard.get("layer_counts") or {}
    shares = scorecard.get("layer_share") or {}

    detected_layers = {
        layer: {"count": counts.get(layer, 0), "share": shares.get(layer, 0.0)}
        for layer in (*LAYERS, "unclassified")
    }

    report = {
        "kind": "supervisor_report",
        "oil_version": OIL_VERSION,
        "status": f"{DRAFT_STAMP} — DSIU-OIL supervisor report; review before acting (Law 0)",
        "date": date.today().isoformat(),
        "target_analyzed": target,
        "detected_layers": detected_layers,
        "key_weaknesses": graph.get("failure_points", []),       # candidates only
        "control_points": graph.get("control_points", {}),
        "proposed_mission_packet": packet,
        "movement_score": (diff or {}).get("movement_score") if diff else None,
        "required_next_action": required_next_action(diff, policy_verdict),
        "policy_verdict": policy_verdict,
        "execution": {**EXECUTION_SEAM,
                      "record": execute_record or "dry-run (no execution requested)"},
    }

    # Optional DSIU-UEF compatibility profile (attached when --uef was given).
    if uef_profile:
        report["uef_compatibility_profile"] = uef_profile
        report["uef_summary"] = {
            "workload": uef_profile.get("workload_name"),
            "detected_type": uef_profile.get("detected_type"),
            "primary_execution_lane": uef_profile.get("primary_execution_lane"),
            "fallback_execution_lanes": uef_profile.get("fallback_execution_lanes"),
            "permission_risk": uef_profile.get("permission_risk"),
            "sandbox_recommendation": uef_profile.get("sandbox_recommendation"),
        }
        report["required_next_action"] += (
            f" | UEF: recommend lane '{uef_profile.get('primary_execution_lane')}' "
            "(candidate, requires validation; execution not performed)."
        )

    return report


def render_report_md(report: dict) -> str:
    dl = report["detected_layers"]
    layer_rows = "\n".join(
        f"| {layer} | {dl[layer]['count']} | {dl[layer]['share']} |"
        for layer in (*LAYERS, "unclassified")
    )
    weaknesses = report["key_weaknesses"]
    if weaknesses:
        wk = "\n".join(f"- **[{w['kind']}]** ({w['layer']}) {w['detail']}"
                       for w in weaknesses)
    else:
        wk = "_(none flagged)_"
    cps = "\n".join(f"- **{layer}:** {', '.join(cp)}"
                    for layer, cp in report["control_points"].items())
    pv = report["policy_verdict"]
    ms = report["movement_score"]
    movement = (f"{ms} (direction unverified — movement ≠ improvement)"
                if ms is not None else "_(no prior pass — no movement to measure)_")

    uef_md = ""
    if report.get("uef_summary"):
        u = report["uef_summary"]
        fb = ", ".join(u["fallback_execution_lanes"]) or "_(none)_"
        uef_md = f"""
## Compatibility (DSIU-UEF)
- workload: `{u['workload']}`  ·  detected type: **{u['detected_type']}**
- primary lane (candidate): **{u['primary_execution_lane']}**
- fallback lanes: {fb}
- permission risk: **{u['permission_risk']}**
- sandbox: {u['sandbox_recommendation']}
- _execution not performed — lanes require validation (Law 0)._
"""

    return f"""# DSIU-OIL Supervisor Report — {report['target_analyzed']}

> {report['oil_version']}  ·  {DRAFT_STAMP}
> Observe → Map → Score → Packetize → Supervise → Diff → Feedback → Repeat
> A routing read-out, not a verdict. Review before acting (Law 0).

## Target analyzed
`{report['target_analyzed']}`

## Detected layers

| Layer | Files | Share |
|---|---|---|
{layer_rows}

## Key weaknesses (candidates — require review)
{wk}

## Control points
{cps}

## Movement
{movement}
{uef_md}
## Law 0 / policy verdict
- law_0: **{pv['law_0']}**
- draft_ok: **{pv['draft_ok']}**
- movement_measured: **{pv['movement_measured']}**
- improvement_claim_allowed: **{pv['improvement_claim_allowed']}**
- upgrade_claim_allowed: **{pv['upgrade_claim_allowed']}**
- direction: **{pv['direction']}**

## Execution
- execution_supervisor: **{report['execution']['execution_supervisor']}**
- future_execution_fabric: **{report['execution']['future_execution_fabric']}**
- record: {report['execution']['record']}

## Required next action
{report['required_next_action']}

---
*DSIU-OIL maps, scores, and proposes. It does not perform or claim upgrades.*
"""
