"""Smoke tests for the DSIU engine — stdlib unittest, no third-party deps.

Run:  python -m unittest discover -s tests
"""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "dsiu", "scripts"))
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "mini_repo")

import dsiu_analyze as m  # noqa: E402


class TestClassify(unittest.TestCase):
    def test_known_buckets(self):
        self.assertEqual(m.classify("src/parser.py"), "intake")
        self.assertEqual(m.classify("src/service.py"), "processing")
        self.assertEqual(m.classify("src/renderer.py"), "output")

    def test_self_is_processing(self):
        # F2: the engine must be able to classify its own tooling.
        self.assertEqual(m.classify("scripts/dsiu_analyze.py"), "processing")

    def test_unclassified_fallback(self):
        self.assertEqual(m.classify("zzz/qqq.py"), "unclassified")


class TestTemplate(unittest.TestCase):
    def test_header_and_name(self):
        out = m.render_template("My System")
        self.assertIn("DSIU Field Template — My System", out)
        self.assertIn(m.HEADER, out)


class TestScan(unittest.TestCase):
    def setUp(self):
        self.items = list(m.walk_repo(FIXTURE))

    def test_fixture_classification(self):
        mapping = dict(self.items)
        self.assertEqual(mapping["parser.py"], "intake")
        self.assertEqual(mapping["service.py"], "processing")
        self.assertEqual(mapping["renderer.py"], "output")

    def test_scan_md_carries_draft_stamp(self):
        md = m.render_scan("Fix", FIXTURE, self.items)
        self.assertIn(m.DRAFT_STAMP, md)

    def test_include_docs_widens_inventory(self):
        code_only = list(m.walk_repo(ROOT))
        with_docs = list(m.walk_repo(ROOT, include_docs=True))
        self.assertGreater(len(with_docs), len(code_only))


class TestScorecard(unittest.TestCase):
    def test_structured_layers(self):
        card = m.build_scorecard("X", None, None)
        self.assertEqual(set(card["layers"]), set(m.LAYERS))
        for layer in m.LAYERS:
            block = card["layers"][layer]
            for key in ("qualities", "skills", "strengths", "weaknesses",
                        "control_points"):
                self.assertIn(key, block)
            # ratings start null (engine maps structure, not condition)
            self.assertTrue(all(q["rating"] is None for q in block["qualities"]))

    def test_scan_scorecard_seeds_files(self):
        items = list(m.walk_repo(FIXTURE))
        card = m.build_scorecard("Fix", FIXTURE, items)
        self.assertEqual(card["kind"], "scan")
        self.assertIn("parser.py", card["layers"]["intake"]["files"])

    def test_scorecard_md_renders(self):
        layers = m.build_attribute_layers()
        md = m.render_scorecard_md("X", layers)
        self.assertIn("DSIU Attribute Scorecard — X", md)
        self.assertIn(m.DRAFT_STAMP, md)


class TestDiff(unittest.TestCase):
    def test_movement_score(self):
        items = list(m.walk_repo(FIXTURE))
        before = m.build_scorecard("Fix", FIXTURE, items)
        # after: drop the intake file -> 1 removal expected
        after = m.build_scorecard("Fix", FIXTURE,
                                  [(p, l) for p, l in items if p != "parser.py"])
        d = m.build_diff(before, after)
        self.assertEqual(d["files_removed_total"], 1)
        self.assertEqual(d["movement_score"], 1)
        self.assertIn("parser.py", d["per_layer"]["intake"]["files_removed"])

    def test_rating_delta_counts(self):
        before = m.build_scorecard("X", None, None)
        after = json.loads(json.dumps(before))  # deep copy
        after["layers"]["intake"]["qualities"][0]["rating"] = 3
        before["layers"]["intake"]["qualities"][0]["rating"] = 1
        d = m.build_diff(before, after)
        self.assertEqual(d["rating_points_changed"], 2)

    def test_diff_md_carries_draft_stamp(self):
        before = m.build_scorecard("X", None, None)
        d = m.build_diff(before, before)
        self.assertIn(m.DRAFT_STAMP, m.render_diff_md(d))
        self.assertEqual(d["movement_score"], 0)


class TestPacket(unittest.TestCase):
    def test_shape_from_name(self):
        p = m.build_packet("Bare", None)
        for key in ("inputs", "hard_locks", "failure_bans"):
            self.assertIn(key, p)
        self.assertTrue(p["failure_bans"])
        self.assertEqual(p["mission"], "Bare")

    def test_shape_from_scorecard(self):
        items = list(m.walk_repo(FIXTURE))
        card = m.build_scorecard("Fix", FIXTURE, items)
        p = m.build_packet("Fix", card)
        self.assertIn("parser.py", p["inputs"]["layers"]["intake"]["files"])


if __name__ == "__main__":
    unittest.main()
