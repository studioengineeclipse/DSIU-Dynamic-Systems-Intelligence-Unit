"""Tests for DSIU-UEF — the compatibility intelligence layer.

Stdlib unittest only. Run: python -m unittest discover -s tests
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dsiu_uef import DRAFT_STAMP, lanes  # noqa: E402
from dsiu_uef.profile import build_profile  # noqa: E402
from dsiu_uef.report import render_profile_md  # noqa: E402

UEF_FIX = os.path.join(ROOT, "tests", "fixtures", "uef")

REQUIRED_FIELDS = (
    "workload_name", "workload_path", "detected_type", "target_os",
    "cpu_architecture_signal", "file_or_manifest_type", "runtime_requirements",
    "dependency_signals", "gpu_requirement_signal", "network_requirement_signal",
    "filesystem_requirement_signal", "permission_risk", "sandbox_recommendation",
    "primary_execution_lane", "fallback_execution_lanes", "unsupported_reasons",
    "confidence", "status",
)


def _profile(rel):
    return build_profile(os.path.join(UEF_FIX, rel))


class TestLaneSelection(unittest.TestCase):
    def test_windows_exe(self):
        p = _profile("windows_app.exe")
        self.assertEqual(p["detected_type"], lanes.WINDOWS_EXECUTABLE)
        self.assertEqual(p["primary_execution_lane"], lanes.WINDOWS_WINE)
        self.assertIn(lanes.WINDOWS_PROTON, p["fallback_execution_lanes"])
        self.assertIn(lanes.VM_RUNTIME, p["fallback_execution_lanes"])

    def test_android_apk(self):
        p = _profile("mobile_app.apk")
        self.assertEqual(p["detected_type"], lanes.ANDROID_PACKAGE)
        self.assertEqual(p["primary_execution_lane"], lanes.ANDROID_CONTAINER)

    def test_docker_project(self):
        p = _profile("docker_project")
        self.assertEqual(p["detected_type"], lanes.DOCKER_PROJECT)
        self.assertEqual(p["primary_execution_lane"], lanes.CONTAINER_RUNTIME)

    def test_web_app(self):
        p = _profile("web_app")
        self.assertEqual(p["detected_type"], lanes.WEB_APP)
        self.assertEqual(p["primary_execution_lane"], lanes.WEB_PWA)

    def test_linux_script(self):
        p = _profile("script.sh")
        self.assertEqual(p["detected_type"], lanes.LINUX_SCRIPT)
        self.assertEqual(p["primary_execution_lane"], lanes.LINUX_NATIVE)

    def test_steam_game(self):
        p = _profile("steam_game")
        self.assertEqual(p["detected_type"], lanes.STEAM_GAME)
        self.assertEqual(p["primary_execution_lane"], lanes.WINDOWS_PROTON)

    def test_fallbacks_exist_where_expected(self):
        # exe, docker, steam all carry fallback lanes
        for rel in ("windows_app.exe", "docker_project", "steam_game"):
            self.assertTrue(_profile(rel)["fallback_execution_lanes"])


class TestUnknown(unittest.TestCase):
    def test_unknown_is_unsupported(self):
        p = _profile("unknown.bin")
        self.assertEqual(p["detected_type"], lanes.UNKNOWN)
        self.assertEqual(p["primary_execution_lane"], lanes.UNSUPPORTED_UNKNOWN)
        self.assertEqual(p["fallback_execution_lanes"], [])
        self.assertTrue(p["unsupported_reasons"])
        self.assertIn("execution not performed", " ".join(p["unsupported_reasons"]).lower())


class TestLaw0(unittest.TestCase):
    def test_all_profiles_draft(self):
        for rel in ("windows_app.exe", "mobile_app.apk", "docker_project",
                    "web_app", "script.sh", "unknown.bin", "steam_game"):
            self.assertIn(DRAFT_STAMP, _profile(rel)["status"])

    def test_all_required_fields_present(self):
        p = _profile("windows_app.exe")
        for field in REQUIRED_FIELDS:
            self.assertIn(field, p)

    def test_no_supported_claim_in_markdown(self):
        md = render_profile_md(_profile("windows_app.exe")).lower()
        self.assertIn(DRAFT_STAMP.lower(), md)
        self.assertNotIn("verified working", md)
        self.assertIn("execution not performed", md)

    def test_uef_never_executes(self):
        """No UEF module may import subprocess or call os.system — it must not run
        anything. We assert against the source, not just runtime state."""
        uef_dir = os.path.join(ROOT, "dsiu_uef")
        offenders = []
        for fn in os.listdir(uef_dir):
            if not fn.endswith(".py"):
                continue
            with open(os.path.join(uef_dir, fn), encoding="utf-8") as fh:
                src = fh.read()
            if "import subprocess" in src or "os.system" in src or "os.popen" in src:
                offenders.append(fn)
        self.assertEqual(offenders, [])


class TestOILIntegration(unittest.TestCase):
    def test_loop_attaches_uef_without_breaking(self):
        import tempfile
        from dsiu_runtime.loop import run_loop
        state = tempfile.mkdtemp()
        r = run_loop(os.path.join(ROOT, "tests", "fixtures", "mini_repo"),
                     name="T", state_dir=state,
                     uef_path=os.path.join(UEF_FIX, "windows_app.exe"))
        rep = r["supervisor_report"]
        self.assertIsNotNone(r["uef_profile"])
        self.assertIn("uef_compatibility_profile", rep)
        self.assertEqual(rep["uef_summary"]["primary_execution_lane"],
                         lanes.WINDOWS_WINE)
        self.assertIn(DRAFT_STAMP, rep["status"])

    def test_loop_without_uef_has_no_uef_keys(self):
        import tempfile
        from dsiu_runtime.loop import run_loop
        state = tempfile.mkdtemp()
        r = run_loop(os.path.join(ROOT, "tests", "fixtures", "mini_repo"),
                     name="T2", state_dir=state)
        self.assertIsNone(r["uef_profile"])
        self.assertNotIn("uef_compatibility_profile", r["supervisor_report"])


if __name__ == "__main__":
    unittest.main()
