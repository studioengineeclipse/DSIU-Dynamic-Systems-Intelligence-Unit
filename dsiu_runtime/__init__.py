"""DSIU-OIL — the DSIU Operating Intelligence Layer.

Turns the discrete DSIU engine modes (scan / scorecard / packet / diff) into one
coherent operating loop:

    Observe -> Map -> Score -> Packetize -> Supervise -> Diff -> Feedback -> Repeat

This is the operating *intelligence* layer — the brainstem before the body. It is
NOT a kernel, daemon, shell, universal execution fabric, or OS. Those are later
phases. v0.1 keeps strictly to the loop.

Law 0 holds throughout: every artifact is DRAFT until human-verified, and nothing
claims an upgrade was completed. Movement is measured; improvement is never claimed.
"""

__version__ = "0.1"
OIL_VERSION = "DSIU-OIL v0.1"
