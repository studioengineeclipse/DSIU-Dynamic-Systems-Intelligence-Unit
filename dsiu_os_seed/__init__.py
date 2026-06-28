"""DSIU-OS-Seed — the operating-environment scaffold / control plane.

The first OS-seed layer: it unifies the five DSIU organs (Skill, OIL, UEF, Shell,
Daemon) into one documented operating environment — a system manifest, a topology
map, a capability registry, a readiness report, a status view, and the OS roadmap.

It answers "what would the DSIU OS look like if all five organs were one system?"
by *describing* the system, not by booting it.

Hard boundary (v0.1): read-only introspection + documentation. It does NOT boot,
install, execute, launch apps, build a kernel, create a desktop, run a package
manager, or replace the host OS. Every artifact is DRAFT (Law 0) and makes no
"OS complete / bootable / installed / ready" claims.
"""

__version__ = "0.1"
OS_SEED_VERSION = "DSIU-OS-Seed v0.1"
DRAFT_STAMP = "DRAFT"

# The phased path to the (much later) OS. Done phases are marked; future phases
# are clearly future — never claimed as present.
ROADMAP = [
    ("skill", "DSIU executable skill", "done"),
    ("oil", "DSIU-OIL operating intelligence loop", "done"),
    ("uef", "DSIU-UEF compatibility intelligence", "done"),
    ("shell", "DSIU-Shell command cockpit", "done"),
    ("daemon", "DSIU-Daemon continuous observation", "done"),
    ("os_seed", "DSIU-OS-Seed operating-environment scaffold", "current"),
    ("desktop_layer", "DSIU-Desktop Layer (local user environment)", "future"),
    ("linux_distribution", "DSIU Linux distribution", "future"),
    ("native_os", "DSIU native OS research", "future"),
]
