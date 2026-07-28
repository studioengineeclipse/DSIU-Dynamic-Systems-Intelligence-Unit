"""DSIU-Distro — the Linux-distribution scaffold (spec / manifest control plane).

OS-Seed describes *what DSIU is* as an operating environment; DSIU-Distro describes
*what a DSIU Linux distribution would be* if the environment were packaged as a boot-
able OS image: a component/package set, a boot topology (the layer stack from firmware
to the DSIU login surface), and an image build plan (stages + target formats). It is
the next roadmap phase after the Desktop Layer.

It answers "if DSIU shipped as a Linux distro, what would go in it and how would it
boot?" by *describing* the distribution — it does NOT build one.

Hard boundary (v0.1): read-only spec/manifest scaffold. It does NOT build an image,
produce an ISO/qcow2/raw file, install packages, run a package manager, build a
kernel, boot anything, or execute any workload. Every artifact is DRAFT (Law 0) and
makes no "bootable / installed / image built / distro ready / OS complete" claims.
The five DSIU organs are described *as* distribution components by reusing the OS-Seed
registry — they are not re-listed here.
"""

__version__ = "0.1"
DISTRO_VERSION = "DSIU-Distro v0.1"
DRAFT_STAMP = "DRAFT"
