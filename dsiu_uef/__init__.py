"""DSIU-UEF — the DSIU Universal Execution Fabric (compatibility intelligence layer).

UEF does NOT execute anything. Its job is to *classify and route*: given a file,
folder, repo, manifest, or binary name, it identifies what the workload is, infers
the runtime lane it belongs in, flags dependency/permission risks, recommends a
sandbox, and emits a DRAFT compatibility profile. That profile can be attached to
the DSIU-OIL supervisor report.

The UEF promise is NOT "everything runs natively." It is: every workload gets
classified, routed, sandboxed, supervised, and given a best-available execution
lane with fallbacks — so a future OS absorbs the compatibility chaos instead of
throwing it at the user.

Hard boundary (v0.1): no execution, no dependency install, no Wine/Proton/VM/
container/Android runtime. Classification, routing, and planning only.
"""

__version__ = "0.1"
UEF_VERSION = "DSIU-UEF v0.1"
DRAFT_STAMP = "DRAFT"
