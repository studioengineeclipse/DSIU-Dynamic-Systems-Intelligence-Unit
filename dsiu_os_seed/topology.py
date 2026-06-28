"""Topology — how the organs connect into one operating environment."""

from __future__ import annotations

from datetime import date

from . import DRAFT_STAMP
from .registry import ORGANS

# Future OS layers — clearly marked future, never claimed as present.
FUTURE_NODES = [
    {"id": "desktop_layer", "kind": "future", "role": "local user environment"},
    {"id": "linux_distribution", "kind": "future", "role": "DSIU Linux distro"},
    {"id": "native_os", "kind": "future", "role": "native OS research"},
]


def build_topology() -> dict:
    nodes = [{"id": o["name"], "kind": "organ", "role": o["future_os_role"]}
             for o in ORGANS] + FUTURE_NODES

    # Skill -> OIL -> UEF -> Shell -> Daemon, then the future expansion edges.
    edges = [
        {"from": "skill", "to": "oil", "relation": "doctrine feeds the loop"},
        {"from": "oil", "to": "uef", "relation": "loop may attach compatibility"},
        {"from": "uef", "to": "shell", "relation": "lanes surface in the cockpit"},
        {"from": "shell", "to": "daemon", "relation": "cockpit commands are watched over time"},
        {"from": "daemon", "to": "os_seed", "relation": "observation feeds the control plane"},
        {"from": "os_seed", "to": "desktop_layer", "relation": "scaffold -> user environment (future)"},
        {"from": "desktop_layer", "to": "linux_distribution", "relation": "future"},
        {"from": "linux_distribution", "to": "native_os", "relation": "future"},
    ]

    return {
        "schema": "dsiu.os_seed_topology/v0.1",
        "status": f"{DRAFT_STAMP} — operating topology map; future nodes are not built (Law 0)",
        "date": date.today().isoformat(),
        "nodes": nodes,
        "edges": edges,
        "data_flow": "workload/repo -> intake -> processing -> output (Skill/OIL)",
        "control_flow": "Shell command -> OIL loop / UEF profile -> supervisor report",
        "feedback_flow": "OIL diff + Daemon events -> movement measured (not improvement)",
        "state_flow": "dsiu_state / dsiu_shell_state / dsiu_daemon_state (created by use)",
        "future_expansion_points": [n["id"] for n in FUTURE_NODES],
    }
