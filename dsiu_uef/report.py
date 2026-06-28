"""Report — render a compatibility profile as Markdown (JSON is the raw profile)."""

from __future__ import annotations

from . import DRAFT_STAMP, UEF_VERSION


def render_profile_md(p: dict) -> str:
    fallbacks = ", ".join(p["fallback_execution_lanes"]) or "_(none)_"
    runtime = ", ".join(p["runtime_requirements"]) or "_(none detected)_"
    deps = ", ".join(p["dependency_signals"])
    unsupported = ""
    if p["unsupported_reasons"]:
        unsupported = "\n## Unsupported reasons\n" + "\n".join(
            f"- {r}" for r in p["unsupported_reasons"])

    return f"""# DSIU-UEF Compatibility Profile — {p['workload_name']}

> {UEF_VERSION}  ·  {DRAFT_STAMP}
> Classification, routing, and sandbox planning only. **Execution not performed.**
> Lanes are *candidates* requiring validation — not a "supported" claim (Law 0).

**Workload:** `{p['workload_path']}`
**Detected type:** {p['detected_type']}  ({p['file_or_manifest_type']})
**Target OS:** {p['target_os']}  ·  **CPU arch signal:** {p['cpu_architecture_signal']}
**Confidence:** {p['confidence']}

## Execution lanes (candidates)
- **Primary (recommended):** `{p['primary_execution_lane']}`
- **Fallbacks:** {fallbacks}

## Runtime & requirement signals
- **Likely runtime:** {runtime}
- **Dependency signals:** {deps}
- **GPU:** {p['gpu_requirement_signal']}  ·  **Network:** {p['network_requirement_signal']}  ·  **Filesystem:** {p['filesystem_requirement_signal']}

## Sandbox & risk (plan, not enforcement)
- **Permission risk:** {p['permission_risk']}
- **Sandbox recommendation:** {p['sandbox_recommendation']}
{unsupported}
## Required next action
{p['required_next_action']}

---
*DSIU-UEF classifies, routes, and plans. It does not run, install, or claim support.*
"""
