"""Tests for DSIU-Desktop Layer — the local workspace / control surface.

Stdlib unittest only. Run: python -m unittest discover -s tests
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dsiu_desktop import DRAFT_STAMP  # noqa: E402
from dsiu_desktop import __main__ as M  # noqa: E402
from dsiu_desktop import render as R  # noqa: E402
from dsiu_desktop import tui as TUI  # noqa: E402
from dsiu_desktop import workspace as W  # noqa: E402
from dsiu_desktop.dashboard import build_dashboard  # noqa: E402

DASHBOARD_FIELDS = (
    "schema", "status", "organs_summary", "os_seed_status",
    "registered_workspaces", "latest_shell_session_summary",
    "latest_daemon_event_summary", "compatibility_summary", "readiness_summary",
    "roadmap", "policy_boundaries", "next_recommended_action",
    "no_execution_performed",
)
SIX_LAYERS = {"skill", "oil", "uef", "shell", "daemon"}  # + os_seed via readiness


class DesktopBase(unittest.TestCase):
    def setUp(self):
        self.state = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.state, ignore_errors=True)


class TestOverview(DesktopBase):
    def test_overview_draft_and_layers(self):
        md = R.render_overview_md(build_dashboard(self.state))
        self.assertIn(DRAFT_STAMP, md)
        for organ in SIX_LAYERS:
            self.assertIn(organ, md)
        self.assertIn("OS-Seed readiness", md)  # the sixth layer


class TestWorkspace(DesktopBase):
    def test_add_writes_record(self):
        rec = W.add_workspace(os.path.join(ROOT, "dsiu"), name="DSIU self",
                              state_dir=self.state)
        self.assertTrue(os.path.isfile(
            os.path.join(self.state, "registered_workspaces.json")))
        self.assertTrue(rec["path"].endswith("dsiu"))
        self.assertEqual(rec["name"], "DSIU self")

    def test_list_and_dedupe(self):
        W.add_workspace(os.path.join(ROOT, "dsiu"), state_dir=self.state)
        W.add_workspace(os.path.join(ROOT, "dsiu"), state_dir=self.state)  # dup
        W.add_workspace(os.path.join(ROOT, "tests"), state_dir=self.state)
        self.assertEqual(len(W.list_workspaces(self.state)), 2)


class TestDashboard(DesktopBase):
    def test_required_fields(self):
        d = build_dashboard(self.state)
        for field in DASHBOARD_FIELDS:
            self.assertIn(field, d)
        self.assertEqual(d["schema"], "dsiu.desktop_dashboard/v0.1")
        self.assertTrue(d["no_execution_performed"])
        self.assertIn(DRAFT_STAMP, d["status"])


class TestStatusRoadmap(DesktopBase):
    def test_status_law0(self):
        md = R.render_status_md(build_dashboard(self.state))
        self.assertIn(DRAFT_STAMP, md)
        self.assertIn("no execution performed", md.lower())

    def test_roadmap_sequence(self):
        d = build_dashboard(self.state)
        keys = [p["phase"] for p in d["roadmap"]]
        self.assertEqual(keys[:6],
                         ["skill", "oil", "uef", "shell", "daemon", "os_seed"])
        self.assertIn("desktop_layer", keys)


class TestEmptyState(DesktopBase):
    def test_empty_shell_daemon_safe(self):
        # point summarizers at empty temp dirs via build with no prior org state
        d = build_dashboard(self.state,
                            shell_state_dir=os.path.join(self.state, "no_shell"),
                            daemon_state_dir=os.path.join(self.state, "no_daemon"))
        self.assertFalse(d["latest_shell_session_summary"]["present"])
        self.assertFalse(d["latest_daemon_event_summary"]["present"])
        # rendering must not crash
        self.assertIn(DRAFT_STAMP, R.render_dashboard_md(d))


class TestCLI(DesktopBase):
    def test_json_md_written(self):
        jp = os.path.join(self.state, "d.json")
        mp = os.path.join(self.state, "d.md")
        rc = M.main(["dashboard", "--state-dir", self.state, "--json", jp, "--md", mp])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.isfile(jp) and os.path.isfile(mp))
        with open(jp) as fh:
            self.assertEqual(json.load(fh)["schema"], "dsiu.desktop_dashboard/v0.1")

    def test_workspace_add_via_cli(self):
        rc = M.main(["workspace", "add", os.path.join(ROOT, "dsiu"),
                     "--name", "DSIU self", "--state-dir", self.state])
        self.assertEqual(rc, 0)
        self.assertEqual(len(W.list_workspaces(self.state)), 1)


class TestTUI(DesktopBase):
    def test_frame_draft_layers_and_footer(self):
        frame = TUI.render_tui_frame(build_dashboard(self.state))
        self.assertIn(DRAFT_STAMP, frame)
        for organ in SIX_LAYERS:
            self.assertIn(organ, frame)
        self.assertIn("no execution performed", frame.lower())

    def test_frame_safe_on_empty_state_and_narrow_width(self):
        d = build_dashboard(self.state,
                            shell_state_dir=os.path.join(self.state, "no_shell"),
                            daemon_state_dir=os.path.join(self.state, "no_daemon"))
        # narrow width must not crash; every content row stays within the frame width
        frame = TUI.render_tui_frame(d, width=50)
        self.assertIn(DRAFT_STAMP, frame)
        for line in frame.splitlines():
            self.assertLessEqual(len(line), 50)

    def test_cli_tui_snapshot(self):
        rc = M.main(["tui", "--state-dir", self.state, "--width", "60"])
        self.assertEqual(rc, 0)


class TestSafety(DesktopBase):
    def test_no_execution_mechanisms(self):
        desk_dir = os.path.join(ROOT, "dsiu_desktop")
        banned = ("import subprocess", "os.system", "os.popen", "shutil.which",
                  "exec(", "eval(", "import pty")
        offenders = {}
        for fn in os.listdir(desk_dir):
            if not fn.endswith(".py"):
                continue
            with open(os.path.join(desk_dir, fn), encoding="utf-8") as fh:
                src = fh.read()
            hits = [b for b in banned if b in src]
            if hits:
                offenders[fn] = hits
        self.assertEqual(offenders, {})

    def test_no_forbidden_claims(self):
        from dsiu_desktop.policy import FORBIDDEN_CLAIMS
        d = build_dashboard(self.state)
        blob = (R.render_overview_md(d) + R.render_dashboard_md(d)
                + R.render_status_md(d) + R.render_roadmap_md(d)).lower()
        for claim in FORBIDDEN_CLAIMS:
            self.assertNotIn(claim, blob)


if __name__ == "__main__":
    unittest.main()
