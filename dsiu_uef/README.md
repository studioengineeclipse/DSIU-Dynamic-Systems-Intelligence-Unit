# DSIU Universal Execution Fabric — v0.1

DSIU-UEF is the **compatibility intelligence layer**. Given a file, folder, repo,
manifest, or binary name, it answers: *what is this, what can run it, what lane does
it need, what risks does it carry, what's the fallback, and what should the system
do next?*

**UEF does not run anything yet.** It classifies, routes, sandbox-plans, and
profiles. It is the foundation that lets a future DSIU Shell/OS "run anything" by
knowing what lane anything belongs in — the OS absorbs the compatibility chaos
instead of throwing it at the user.

> The UEF promise is **not** "everything runs natively." It is: every workload gets
> classified, routed, sandboxed, supervised, and given a best-available lane with
> fallbacks.

**Hard boundary (v0.1):** no execution. No dependency install. No Wine/Proton/VM/
container/Android runtime. No app store or package manager. Classification, routing,
and planning only.

## Pipeline

```
intake.gather → classify.detect → router.route → sandbox.assess → profile.build_profile → report
   (signals)      (detected_type)   (lanes)        (risk+plan)       (DRAFT profile)        (JSON/MD)
```

| Module | Job |
|---|---|
| `intake.py` | Gather raw signals (name, ext, magic bytes, dir manifests, arch). Reads metadata/first bytes only — never runs the workload. |
| `classify.py` | Signals → `detected_type` + runtime/dependency/gpu/network/fs signals + confidence. |
| `lanes.py` | The 11 execution lanes + the detected-type → lane table. |
| `router.py` | detected_type → primary lane, fallback lanes, unsupported reasons. |
| `sandbox.py` | Permission-risk level + sandbox recommendation (a plan, not enforcement). |
| `profile.py` | Assembles the full DRAFT compatibility profile. |
| `report.py` | Markdown view of a profile (JSON is the raw profile). |

## Execution lanes

`native_dsiu`, `linux_native`, `flatpak_appimage`, `windows_wine`,
`windows_proton`, `android_container`, `web_pwa`, `container_runtime`,
`vm_runtime`, `remote_cloud`, `unsupported_unknown`.

## Detection → lane (examples)

| Workload | Detected | Primary lane | Fallbacks |
|---|---|---|---|
| `.exe` / PE `MZ` | windows_executable | `windows_wine` | windows_proton, vm_runtime |
| steam `appmanifest_*.acf` | steam_game | `windows_proton` | linux_native, vm_runtime |
| `.apk` / AndroidManifest | android_package | `android_container` | vm_runtime |
| `Dockerfile` / compose | docker_project | `container_runtime` | vm_runtime, remote_cloud |
| `package.json` | web_app | `web_pwa` | container_runtime |
| AppImage / Flatpak | appimage_flatpak | `flatpak_appimage` | linux_native |
| ELF / `.sh` | linux_binary / linux_script | `linux_native` | container_runtime |
| `.iso`/`.qcow2`/`.ova` | vm_image | `vm_runtime` | remote_cloud |
| SKILL.md / `.skill` | dsiu_native | `native_dsiu` | linux_native |
| anything else | unknown | `unsupported_unknown` | _(none)_ + reasons |

## Run it

```bash
# Classify a workload into a DRAFT compatibility profile (Markdown to stdout)
python -m dsiu_uef intake --path ./some_app

# Write JSON + Markdown
python -m dsiu_uef intake --path ./some_app --json profile.json --md profile.md
```

### Attach to the OIL supervisor loop

```bash
python -m dsiu_runtime loop --path ./repo --name "Repo" --include-docs --uef ./some_app
```

The supervisor report then includes the UEF compatibility profile, primary lane,
fallback lanes, permission risk, sandbox recommendation, and a UEF-aware
required-next-action — all DRAFT.

## Law 0 (enforced)

Every UEF artifact carries `DRAFT`. There is **no "supported" claim** — v0.1 never
executes. Allowed wording: *candidate lane, recommended lane, likely runtime,
requires validation, unsupported unknown, execution not performed.* Forbidden:
*supported, verified working, runs natively (as a claim), installed.*

## Roadmap

Skill ✅ → OIL ✅ → **UEF ✅ (you are here)** → Shell → Daemon → OS

OIL gave DSIU a brain (Observe→Map→Score→Packetize→Supervise→Diff→Feedback). UEF
gives that brain a **compatibility sense**. The OS body comes much later — only once
the compatibility intelligence layer is stable.
