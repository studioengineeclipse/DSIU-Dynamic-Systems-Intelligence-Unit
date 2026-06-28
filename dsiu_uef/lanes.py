"""Execution lanes — the routing vocabulary of the fabric.

A *lane* is a candidate execution path. v0.1 only names and recommends lanes; it
never enters one. Nothing here runs.
"""

from __future__ import annotations

# --- Lane constants (the 11 lanes) -------------------------------------------
NATIVE_DSIU = "native_dsiu"
LINUX_NATIVE = "linux_native"
FLATPAK_APPIMAGE = "flatpak_appimage"
WINDOWS_WINE = "windows_wine"
WINDOWS_PROTON = "windows_proton"
ANDROID_CONTAINER = "android_container"
WEB_PWA = "web_pwa"
CONTAINER_RUNTIME = "container_runtime"
VM_RUNTIME = "vm_runtime"
REMOTE_CLOUD = "remote_cloud"
UNSUPPORTED_UNKNOWN = "unsupported_unknown"

LANES = (
    NATIVE_DSIU, LINUX_NATIVE, FLATPAK_APPIMAGE, WINDOWS_WINE, WINDOWS_PROTON,
    ANDROID_CONTAINER, WEB_PWA, CONTAINER_RUNTIME, VM_RUNTIME, REMOTE_CLOUD,
    UNSUPPORTED_UNKNOWN,
)

# --- Detected workload types -------------------------------------------------
WINDOWS_EXECUTABLE = "windows_executable"
STEAM_GAME = "steam_game"
ANDROID_PACKAGE = "android_package"
DOCKER_PROJECT = "docker_project"
WEB_APP = "web_app"
APPIMAGE_FLATPAK = "appimage_flatpak"
LINUX_BINARY = "linux_binary"
LINUX_SCRIPT = "linux_script"
DSIU_NATIVE = "dsiu_native"
VM_IMAGE = "vm_image"
UNKNOWN = "unknown"

# --- detected_type -> (primary lane, fallback lanes) -------------------------
# Candidate routing only — "recommended", never "supported" (Law 0).
LANE_TABLE = {
    WINDOWS_EXECUTABLE: (WINDOWS_WINE, (WINDOWS_PROTON, VM_RUNTIME)),
    STEAM_GAME:         (WINDOWS_PROTON, (LINUX_NATIVE, VM_RUNTIME)),
    ANDROID_PACKAGE:    (ANDROID_CONTAINER, (VM_RUNTIME,)),
    DOCKER_PROJECT:     (CONTAINER_RUNTIME, (VM_RUNTIME, REMOTE_CLOUD)),
    WEB_APP:            (WEB_PWA, (CONTAINER_RUNTIME,)),
    APPIMAGE_FLATPAK:   (FLATPAK_APPIMAGE, (LINUX_NATIVE,)),
    LINUX_BINARY:       (LINUX_NATIVE, (CONTAINER_RUNTIME,)),
    LINUX_SCRIPT:       (LINUX_NATIVE, (CONTAINER_RUNTIME,)),
    DSIU_NATIVE:        (NATIVE_DSIU, (LINUX_NATIVE,)),
    VM_IMAGE:           (VM_RUNTIME, (REMOTE_CLOUD,)),
    UNKNOWN:            (UNSUPPORTED_UNKNOWN, ()),
}
