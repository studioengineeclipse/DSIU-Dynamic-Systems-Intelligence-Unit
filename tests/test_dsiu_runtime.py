"""Tests for DSIU-OIL — the operating intelligence layer.

Stdlib unittest, no third-party deps.  Run: python -m unittest discover -s tests
"""

import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dsiu_runtime import OIL_VERSION  # noqa: E402
from dsiu_runtime import graph, policy, state, supervisor  # noqa: E402
from dsiu_runtime.engine import DRAFT_STAMP, build_scorecard, walk_repo  # noqa: E402
from dsiu_runtime.loop import run_loop  # noqa: E402

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "mini_repo")


def _scorecard():
    items = list(walk_repo(FIXTURE))
    return build_scorecard("Fix", FIXTURE, items)


class TestGraph(unittest.TestCase):
    def test_schema_and_nodes(self):
        g = graph.build_process_graph("Fix", _scorecard())
        self.assertEqual(g["schema"], "dsiu.process_graph/v0.1")
        ids = [n["id"] for n in g["nodes"]]
        self.assertEqual(ids, ["intake", "processing", "output", "feedback"])
        self.assertIn(DRAFT_STAMP, g["status"])

    def test_loop_edges_and_control_points(self):
        g = graph.build_process_graph("Fix", _scorecard())
        edges = {(e["from"], e["to"]) for e in g["edges"]}
        self.assertIn(("output", "feedback"), edges)
        self.assertIn(("feedback", "intake"), edges)  # the loop closes
        self.assertEqual(set(g["control_points"]), {"intake", "processing", "output"})

    def test_failure_points_are_candidates(self):
        g = graph.build_process_graph("Fix", _scorecard())
        self.assertTrue(g["failure_points"])
        for fp in g["failure_points"]:
            self.assertIn("kind", fp)
            self.assertIn("layer", fp)
            self.assertIn("detail", fp)
        # at least one is explicitly framed as a candidate (never asserted)
        kinds = " ".join(fp["kind"] for fp in g["failure_points"])
        self.assertIn("candidate", kinds)


class TestState(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_previous_before_save_is_none_then_prior(self):
        card1 = _scorecard()
        # No prior pass yet.
        self.assertIsNone(state.previous_state(self.dir, "Fix"))
        state.save_state(self.dir, "Fix", card1)
        # After one save, previous (called before a hypothetical next save) is card1.
        prev = state.previous_state(self.dir, "Fix")
        self.assertIsNotNone(prev)
        self.assertEqual(prev["system"], "Fix")

    def test_latest_is_most_recent(self):
        a = _scorecard(); a["files_mapped"] = 1
        b = _scorecard(); b["files_mapped"] = 99
        state.save_state(self.dir, "Fix", a)
        state.save_state(self.dir, "Fix", b)
        latest = state.load_state(state.latest_state_path(self.dir, "Fix"))
        self.assertEqual(latest["files_mapped"], 99)


class TestPolicy(unittest.TestCase):
    def test_enforce_draft_flags_missing(self):
        good = {"status": f"{DRAFT_STAMP} ok"}
        bad = {"status": "all upgraded and fixed"}
        violations = policy.enforce_draft(good=good, bad=bad, absent=None)
        self.assertEqual(violations, ["bad"])

    def test_movement_not_improvement_with_diff(self):
        diff = {"movement_score": 5}
        v = policy.build_policy_verdict(diff, [])
        self.assertTrue(v["movement_measured"])
        self.assertFalse(v["improvement_claim_allowed"])
        self.assertFalse(v["upgrade_claim_allowed"])
        self.assertEqual(v["direction"], "unverified")
        self.assertIn(DRAFT_STAMP, v["status"])

    def test_no_diff_means_no_movement(self):
        v = policy.build_policy_verdict(None, [])
        self.assertFalse(v["movement_measured"])
        self.assertIsNone(v["movement_score"])


class TestSupervisor(unittest.TestCase):
    def test_report_has_required_fields(self):
        card = _scorecard()
        g = graph.build_process_graph("Fix", card)
        from dsiu_runtime.engine import build_packet
        pkt = build_packet("Fix", card)
        pv = policy.build_policy_verdict(None, [])
        rep = supervisor.build_supervisor_report("Fix", card, g, pkt, None, pv)
        for field in ("target_analyzed", "detected_layers", "key_weaknesses",
                      "control_points", "proposed_mission_packet",
                      "required_next_action"):
            self.assertIn(field, rep)
        self.assertIsNone(rep["movement_score"])  # no diff -> no movement
        self.assertIn(DRAFT_STAMP, rep["status"])
        self.assertEqual(rep["oil_version"], OIL_VERSION)
        # reserved UEF seam present, dry-run only
        self.assertEqual(rep["execution"]["future_execution_fabric"], "reserved")
        self.assertEqual(rep["execution"]["execution_supervisor"], "dry_run_only")

    def test_md_renders_and_is_draft(self):
        card = _scorecard()
        g = graph.build_process_graph("Fix", card)
        from dsiu_runtime.engine import build_packet
        pv = policy.build_policy_verdict(None, [])
        rep = supervisor.build_supervisor_report(
            "Fix", card, g, build_packet("Fix", card), None, pv)
        md = supervisor.render_report_md(rep)
        self.assertIn("DSIU-OIL Supervisor Report", md)
        self.assertIn(DRAFT_STAMP, md)


class TestOperatingLoop(unittest.TestCase):
    def setUp(self):
        self.state = tempfile.mkdtemp()
        self.target = tempfile.mkdtemp()
        shutil.copy(os.path.join(FIXTURE, "parser.py"),
                    os.path.join(self.target, "parser.py"))

    def tearDown(self):
        shutil.rmtree(self.state, ignore_errors=True)
        shutil.rmtree(self.target, ignore_errors=True)

    def test_first_pass_has_no_diff(self):
        r = run_loop(self.target, name="T", state_dir=self.state)
        self.assertIsNone(r["diff"])
        self.assertIsNone(r["supervisor_report"]["movement_score"])

    def test_second_pass_measures_movement(self):
        run_loop(self.target, name="T", state_dir=self.state)
        # change the target: add an output-layer file
        shutil.copy(os.path.join(FIXTURE, "renderer.py"),
                    os.path.join(self.target, "renderer.py"))
        r = run_loop(self.target, name="T", state_dir=self.state)
        self.assertIsNotNone(r["diff"])
        self.assertEqual(r["supervisor_report"]["movement_score"], 1)
        self.assertTrue(r["policy_verdict"]["movement_measured"])
        self.assertFalse(r["policy_verdict"]["improvement_claim_allowed"])

    def test_identical_pass_has_zero_movement(self):
        run_loop(self.target, name="T", state_dir=self.state)
        r = run_loop(self.target, name="T", state_dir=self.state)
        # diff exists (prior pass) but nothing changed -> no fake feedback
        self.assertIsNotNone(r["diff"])
        self.assertEqual(r["supervisor_report"]["movement_score"], 0)
        self.assertFalse(r["policy_verdict"]["movement_measured"])

    def test_all_artifacts_draft_stamped(self):
        r = run_loop(self.target, name="T", state_dir=self.state, include_docs=True)
        for key in ("scorecard", "graph", "packet", "policy_verdict",
                    "supervisor_report"):
            self.assertIn(DRAFT_STAMP, r[key]["status"])

    def test_execute_is_supervised_noop(self):
        r = run_loop(self.target, name="T", state_dir=self.state, execute=True)
        record = r["supervisor_report"]["execution"]["record"]
        self.assertIn("no-op", record)
        self.assertNotIn("upgrade completed", record.lower())


if __name__ == "__main__":
    unittest.main()
