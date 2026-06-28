"""Tests for DSIU-OS-Seed — the operating-environment scaffold / control plane.

Stdlib unittest only. Run: python -m unittest discover -s tests
"""

import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dsiu_os_seed import DRAFT_STAMP  # noqa: E402
from dsiu_os_seed import __main__ as M  # noqa: E402
from dsiu_os_seed.manifest import build_manifest  # noqa: E402
from dsiu_os_seed.readiness import build_readiness  # noqa: E402
from dsiu_os_seed.topology import build_topology  # noqa: E402

ORGAN_NAMES = {"skill", "oil", "uef", "shell", "daemon"}


class TestManifest(unittest.TestCase):
    def test_includes_all_five_organs(self):
        m = build_manifest()
        self.assertEqual({o["name"] for o in m["organs"]}, ORGAN_NAMES)
        self.assertIn(DRAFT_STAMP, m["status"])

    def test_organs_have_capabilities(self):
        for o in build_manifest()["organs"]:
            self.assertTrue(o["capabilities"])  # capability registry, not just modules


class TestTopology(unittest.TestCase):
    def test_organ_and_future_nodes(self):
        t = build_topology()
        ids = {n["id"] for n in t["nodes"]}
        self.assertTrue(ORGAN_NAMES.issubset(ids))
        for future in ("desktop_layer", "linux_distribution", "native_os"):
            self.assertIn(future, ids)
        self.assertIn(DRAFT_STAMP, t["status"])

    def test_chain_edges(self):
        edges = {(e["from"], e["to"]) for e in build_topology()["edges"]}
        for pair in (("skill", "oil"), ("oil", "uef"), ("uef", "shell"),
                     ("shell", "daemon")):
            self.assertIn(pair, edges)


class TestReadiness(unittest.TestCase):
    def test_detects_organs_without_claiming_complete(self):
        r = build_readiness()
        self.assertEqual(set(r["organs_detected"]), ORGAN_NAMES)
        self.assertEqual(r["missing_organs"], [])
        # never claims the OS is ready/complete/production-ready
        level = r["os_readiness_level"].lower()
        for banned in ("ready", "complete", "production"):
            if banned == "complete":
                # "seed-scaffold-complete (candidate)" is allowed; "os complete" is not
                self.assertNotIn("os complete", level)
            else:
                self.assertNotIn(banned, level)
        self.assertIn(DRAFT_STAMP, r["status"])

    def test_state_dirs_known_even_if_absent(self):
        r = build_readiness()
        self.assertTrue(r["state_dirs_known"])
        for s in r["state_dirs"]:
            self.assertTrue(s["known"])  # known regardless of present


class TestStatusRoadmap(unittest.TestCase):
    def test_status_has_law0(self):
        from dsiu_os_seed.render import render_status_md
        md = render_status_md(build_manifest(), build_readiness())
        self.assertIn(DRAFT_STAMP, md)
        self.assertIn("Law 0", md)

    def test_roadmap_sequence(self):
        from dsiu_os_seed import ROADMAP
        keys = [k for k, _, _ in ROADMAP]
        self.assertEqual(keys[:6], ["skill", "oil", "uef", "shell", "daemon", "os_seed"])
        self.assertIn("desktop_layer", keys)


class TestCLIOutputs(unittest.TestCase):
    def test_json_and_md_written(self):
        d = tempfile.mkdtemp()
        jp = os.path.join(d, "m.json")
        mp = os.path.join(d, "m.md")
        rc = M.main(["manifest", "--json", jp, "--md", mp])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.isfile(jp) and os.path.isfile(mp))
        with open(jp) as fh:
            data = json.load(fh)
        self.assertEqual(data["schema"], "dsiu.os_seed_manifest/v0.1")
        with open(mp) as fh:
            self.assertIn(DRAFT_STAMP, fh.read())

    def test_all_commands_render_draft(self):
        from dsiu_os_seed import render as R
        self.assertIn(DRAFT_STAMP, R.render_manifest_md(build_manifest()))
        self.assertIn(DRAFT_STAMP, R.render_topology_md(build_topology()))
        self.assertIn(DRAFT_STAMP, R.render_readiness_md(build_readiness()))
        self.assertIn(DRAFT_STAMP, R.render_roadmap_md())


class TestSafety(unittest.TestCase):
    def test_no_execution_mechanisms(self):
        seed_dir = os.path.join(ROOT, "dsiu_os_seed")
        banned = ("import subprocess", "os.system", "os.popen", "shutil.which",
                  "exec(", "eval(", "import pty")
        offenders = {}
        for fn in os.listdir(seed_dir):
            if not fn.endswith(".py"):
                continue
            with open(os.path.join(seed_dir, fn), encoding="utf-8") as fh:
                src = fh.read()
            hits = [b for b in banned if b in src]
            if hits:
                offenders[fn] = hits
        self.assertEqual(offenders, {})

    def test_no_forbidden_claims_in_render(self):
        from dsiu_os_seed import render as R
        from dsiu_os_seed.policy import FORBIDDEN_CLAIMS
        blob = (R.render_manifest_md(build_manifest())
                + R.render_readiness_md(build_readiness())
                + R.render_status_md(build_manifest(), build_readiness())
                + R.render_roadmap_md()).lower()
        for claim in FORBIDDEN_CLAIMS:
            self.assertNotIn(claim, blob)


if __name__ == "__main__":
    unittest.main()
