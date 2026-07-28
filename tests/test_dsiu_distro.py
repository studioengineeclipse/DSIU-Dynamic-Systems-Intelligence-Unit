"""Tests for DSIU-Distro — the Linux-distribution scaffold / spec control plane.

Stdlib unittest only. Run: python -m unittest discover -s tests
"""

import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dsiu_distro import DRAFT_STAMP  # noqa: E402
from dsiu_distro import __main__ as M  # noqa: E402
from dsiu_distro import render as R  # noqa: E402
from dsiu_distro.boot import build_boot_topology  # noqa: E402
from dsiu_distro.image import build_image_plan  # noqa: E402
from dsiu_distro.manifest import build_manifest  # noqa: E402
from dsiu_distro.packages import build_package_set  # noqa: E402

ORGAN_NAMES = {"skill", "oil", "uef", "shell", "daemon"}


class TestPackages(unittest.TestCase):
    def test_all_organs_present_as_components(self):
        p = build_package_set()
        organs = {c["organ"] for c in p["organ_components"]}
        self.assertEqual(organs, ORGAN_NAMES)
        self.assertEqual(p["organ_count"], 5)
        self.assertIn(DRAFT_STAMP, p["status"])

    def test_nothing_built_or_installed(self):
        p = build_package_set()
        self.assertTrue(p["no_build_performed"])
        self.assertTrue(p["no_packages_installed"])
        for c in p["components"]:
            self.assertEqual(c["status"], "planned")


class TestBoot(unittest.TestCase):
    def test_ordered_stack_ends_at_operator_surface(self):
        b = build_boot_topology()
        orders = [s["order"] for s in b["stages"]]
        self.assertEqual(orders, sorted(orders))  # strictly ordered
        self.assertEqual(b["layer_order"][0], "firmware")
        self.assertEqual(b["operator_surface"], "dsiu-desktop-tui")
        self.assertTrue(b["no_boot_performed"])
        self.assertIn(DRAFT_STAMP, b["status"])


class TestImage(unittest.TestCase):
    def test_targets_planned_and_no_image_built(self):
        im = build_image_plan()
        self.assertTrue(im["all_targets_planned"])
        self.assertTrue(im["no_image_built"])
        for t in im["targets"]:
            self.assertEqual(t["status"], "planned")
        self.assertIn("iso", im["target_formats"])
        self.assertIn(DRAFT_STAMP, im["status"])


class TestManifest(unittest.TestCase):
    def test_schema_phase_and_draft(self):
        m = build_manifest()
        self.assertEqual(m["schema"], "dsiu.distro_manifest/v0.1")
        self.assertEqual(m["current_phase"], "linux_distribution")
        self.assertEqual(m["next_phase"], "native_os")
        self.assertTrue(m["no_build_performed"])
        self.assertTrue(m["no_image_built"])
        self.assertIn(DRAFT_STAMP, m["status"])
        self.assertEqual(m["components"]["organs"], 5)


class TestCLI(unittest.TestCase):
    def test_json_and_md_written(self):
        d = tempfile.mkdtemp()
        jp = os.path.join(d, "m.json")
        mp = os.path.join(d, "m.md")
        rc = M.main(["manifest", "--json", jp, "--md", mp])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.isfile(jp) and os.path.isfile(mp))
        with open(jp) as fh:
            self.assertEqual(json.load(fh)["schema"], "dsiu.distro_manifest/v0.1")
        with open(mp) as fh:
            self.assertIn(DRAFT_STAMP, fh.read())

    def test_all_commands_run(self):
        for cmd in ("manifest", "packages", "boot", "image", "status", "roadmap"):
            self.assertEqual(M.main([cmd, "--md", os.devnull]), 0)


class TestRendersDraft(unittest.TestCase):
    def test_every_render_is_draft(self):
        m, p = build_manifest(), build_package_set()
        self.assertIn(DRAFT_STAMP, R.render_manifest_md(m))
        self.assertIn(DRAFT_STAMP, R.render_packages_md(p))
        self.assertIn(DRAFT_STAMP, R.render_boot_md(build_boot_topology()))
        self.assertIn(DRAFT_STAMP, R.render_image_md(build_image_plan()))
        self.assertIn(DRAFT_STAMP, R.render_status_md(m, p))
        self.assertIn(DRAFT_STAMP, R.render_roadmap_md())


class TestSafety(unittest.TestCase):
    def test_no_execution_mechanisms(self):
        pkg_dir = os.path.join(ROOT, "dsiu_distro")
        banned = ("import subprocess", "os.system", "os.popen", "shutil.which",
                  "exec(", "eval(", "import pty")
        offenders = {}
        for fn in os.listdir(pkg_dir):
            if not fn.endswith(".py"):
                continue
            with open(os.path.join(pkg_dir, fn), encoding="utf-8") as fh:
                src = fh.read()
            hits = [b for b in banned if b in src]
            if hits:
                offenders[fn] = hits
        self.assertEqual(offenders, {})

    def test_no_forbidden_claims_in_render(self):
        from dsiu_distro.policy import FORBIDDEN_CLAIMS
        m, p = build_manifest(), build_package_set()
        blob = (R.render_manifest_md(m) + R.render_packages_md(p)
                + R.render_boot_md(build_boot_topology())
                + R.render_image_md(build_image_plan())
                + R.render_status_md(m, p) + R.render_roadmap_md()).lower()
        for claim in FORBIDDEN_CLAIMS:
            self.assertNotIn(claim, blob)


if __name__ == "__main__":
    unittest.main()
