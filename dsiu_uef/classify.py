"""Classify — turn raw signals into a detected workload type + requirement signals.

Pure heuristics over names/extensions/magic/manifests. No execution, no parsing of
untrusted code — at most a manifest filename is noted, never run.
"""

from __future__ import annotations

from . import lanes as L

_VM_EXTS = {".iso", ".qcow2", ".vmdk", ".ova", ".vdi"}

# Per-type metadata: human label, target OS, runtime requirements.
_TYPE_META = {
    L.WINDOWS_EXECUTABLE: ("Windows PE executable", "windows",
                           ["Win32/Windows API", "wine or proton compatibility layer"]),
    L.STEAM_GAME: ("Steam game manifest / game folder", "windows",
                   ["Steam runtime", "proton/wine for Windows titles", "GPU acceleration"]),
    L.ANDROID_PACKAGE: ("Android package", "android",
                        ["Android runtime (ART)", "emulator or android container"]),
    L.DOCKER_PROJECT: ("Container project (Dockerfile/compose)", "linux",
                       ["OCI container runtime"]),
    L.WEB_APP: ("Web application (package.json)", "cross",
                ["Node.js or a browser runtime"]),
    L.APPIMAGE_FLATPAK: ("AppImage / Flatpak bundle", "linux",
                         ["Linux userland", "FUSE (AppImage) or flatpak runtime"]),
    L.LINUX_BINARY: ("Linux ELF binary", "linux", ["glibc / Linux userland"]),
    L.LINUX_SCRIPT: ("Linux shell script", "linux", ["POSIX shell"]),
    L.DSIU_NATIVE: ("DSIU-native artifact (skill bundle)", "cross",
                    ["DSIU runtime"]),
    L.VM_IMAGE: ("Virtual machine image", "cross", ["hypervisor / VM runtime"]),
    L.UNKNOWN: ("Unknown workload", "unknown", []),
}


def _detect_type(s: dict) -> str:
    m = s.get("manifests") or {}
    ext = s.get("extension", "")
    magic = s.get("magic")

    # Directory / project signals first (most specific).
    if m.get("dockerfile") or m.get("compose"):
        return L.DOCKER_PROJECT
    if m.get("steam_manifest"):
        return L.STEAM_GAME
    if m.get("skill_md"):
        return L.DSIU_NATIVE
    if m.get("android_manifest") or m.get("apk"):
        return L.ANDROID_PACKAGE
    if m.get("package_json"):
        return L.WEB_APP
    if m.get("appimage") or m.get("flatpak"):
        return L.APPIMAGE_FLATPAK

    # File signals (extension + magic).
    if ext in (".exe", ".msi", ".dll") or magic == "pe":
        return L.WINDOWS_EXECUTABLE
    if ext == ".apk":
        return L.ANDROID_PACKAGE
    if ext == ".appimage" or ext == ".flatpakref":
        return L.APPIMAGE_FLATPAK
    if ext == ".sh" or magic == "script":
        return L.LINUX_SCRIPT
    if ext in _VM_EXTS:
        return L.VM_IMAGE
    if ext == ".skill":
        return L.DSIU_NATIVE
    if ext == ".dockerfile" or s.get("workload_name", "").lower() == "dockerfile":
        return L.DOCKER_PROJECT
    if ext == ".json" and s.get("workload_name", "").lower() == "package.json":
        return L.WEB_APP
    if magic == "elf":
        return L.LINUX_BINARY

    return L.UNKNOWN


def _confidence(s: dict, detected: str) -> str:
    if detected == L.UNKNOWN:
        return "low"
    ext = s.get("extension", "")
    magic = s.get("magic")
    manifests = any((s.get("manifests") or {}).values())
    # Strong: a manifest match, or extension + corroborating magic.
    if manifests:
        return "high"
    if detected == L.WINDOWS_EXECUTABLE and ext in (".exe", ".msi") and magic == "pe":
        return "high"
    if detected == L.LINUX_BINARY and magic == "elf":
        return "high"
    if detected == L.LINUX_SCRIPT and (ext == ".sh" or magic == "script"):
        return "high"
    if ext or magic:
        return "medium"
    return "low"


def detect(s: dict) -> dict:
    detected = _detect_type(s)
    label, target_os, runtime_reqs = _TYPE_META[detected]

    gpu = "likely" if detected in (L.STEAM_GAME, L.VM_IMAGE, L.WINDOWS_EXECUTABLE) else "unknown"
    network = "likely" if detected in (L.WEB_APP, L.DOCKER_PROJECT, L.ANDROID_PACKAGE) else "unknown"
    filesystem = "unknown" if detected == L.UNKNOWN else "likely"

    dependency_signals = []
    manifests = s.get("manifests") or {}
    for key, present in manifests.items():
        if present:
            dependency_signals.append(f"manifest: {key}")
    if s.get("magic") and s["magic"] not in ("text", "unreadable"):
        dependency_signals.append(f"magic: {s['magic']}")
    if not dependency_signals and s.get("extension"):
        dependency_signals.append(f"extension: {s['extension']}")

    return {
        "detected_type": detected,
        "file_or_manifest_type": label,
        "target_os": target_os,
        "runtime_requirements": runtime_reqs,
        "dependency_signals": dependency_signals or ["none detected"],
        "gpu_requirement_signal": gpu,
        "network_requirement_signal": network,
        "filesystem_requirement_signal": filesystem,
        "confidence": _confidence(s, detected),
    }
