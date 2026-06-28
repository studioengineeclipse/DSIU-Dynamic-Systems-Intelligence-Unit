"""Tests for DSIU-Shell — the command cockpit over OIL + UEF.

Stdlib unittest only. Run: python -m unittest discover -s tests
"""

import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dsiu_shell import DRAFT_STAMP  # noqa: E402
from dsiu_shell import commands as C  # noqa: E402
from dsiu_shell import render as R  # noqa: E402

REPO = os.path.join(ROOT, "tests", "fixtures", "mini_repo")
EXE = os.path.join(ROOT, "tests", "fixtures", "uef", "windows_app.exe")


class ShellTestBase(unittest.TestCase):
    def setUp(self):
        self.ss = tempfile.mkdtemp()       # shell state
        self.os_ = tempfile.mkdtemp()      # oil state

    def tearDown(self):
        shutil.rmtree(self.ss, ignore_errors=True)
        shutil.rmtree(self.os_, ignore_errors=True)

    def _count_sessions(self):
        return len([f for f in os.listdir(self.ss) if f.startswith("session-")])


class TestWriteCommands(ShellTestBase):
    def test_inspect_calls_oil_and_saves(self):
        sess = C.inspect(REPO, name="T", state_dir=self.ss, oil_state_dir=self.os_)
        self.assertIsNotNone(sess["oil_report"])
        self.assertIsNone(sess["uef_profile"])
        self.assertEqual(self._count_sessions(), 1)

    def test_profile_calls_uef_and_saves(self):
        sess = C.profile(EXE, state_dir=self.ss)
        self.assertIsNotNone(sess["uef_profile"])
        self.assertIsNone(sess["oil_report"])
        self.assertEqual(sess["uef_profile"]["primary_execution_lane"], "windows_wine")
        self.assertEqual(self._count_sessions(), 1)

    def test_analyze_attaches_both(self):
        sess = C.analyze(REPO, name="T", with_path=EXE,
                         state_dir=self.ss, oil_state_dir=self.os_)
        self.assertIsNotNone(sess["oil_report"])
        self.assertIsNotNone(sess["uef_profile"])
        self.assertIn("uef_compatibility_profile", sess["oil_report"])
        self.assertEqual(self._count_sessions(), 1)

    def test_analyze_requires_with(self):
        with self.assertRaises(ValueError):
            C.analyze(REPO, with_path=None, state_dir=self.ss, oil_state_dir=self.os_)


class TestReadCommands(ShellTestBase):
    def test_status_reads_latest(self):
        C.inspect(REPO, name="T", state_dir=self.ss, oil_state_dir=self.os_)
        latest = C.status(state_dir=self.ss)
        self.assertEqual(latest["command"], "inspect")

    def test_history_lists_recent(self):
        C.inspect(REPO, name="T", state_dir=self.ss, oil_state_dir=self.os_)
        C.profile(EXE, state_dir=self.ss)
        sessions = C.history(state_dir=self.ss)
        self.assertEqual(len(sessions), 2)
        self.assertEqual(sessions[0]["command"], "profile")  # newest first

    def test_explain_last_renders(self):
        C.analyze(REPO, name="T", with_path=EXE,
                  state_dir=self.ss, oil_state_dir=self.os_)
        md = R.render_explain(C.explain_last(state_dir=self.ss))
        self.assertIn("What was analyzed", md)
        self.assertIn(DRAFT_STAMP, md)

    def test_read_commands_do_not_write(self):
        C.inspect(REPO, name="T", state_dir=self.ss, oil_state_dir=self.os_)
        before = self._count_sessions()
        C.status(state_dir=self.ss)
        C.history(state_dir=self.ss)
        C.explain_last(state_dir=self.ss)
        self.assertEqual(self._count_sessions(), before)  # still 1


class TestEmptyState(ShellTestBase):
    def test_status_empty_is_safe(self):
        md = R.render_status(C.status(state_dir=self.ss))
        self.assertIn("No shell sessions found", md)
        self.assertIn(DRAFT_STAMP, md)

    def test_history_empty_is_safe(self):
        md = R.render_history(C.history(state_dir=self.ss))
        self.assertIn("No shell sessions found", md)

    def test_explain_empty_is_safe(self):
        md = R.render_explain(C.explain_last(state_dir=self.ss))
        self.assertIn("No shell sessions found", md)


class TestLaw0(ShellTestBase):
    def test_all_outputs_draft(self):
        s1 = C.inspect(REPO, name="T", state_dir=self.ss, oil_state_dir=self.os_)
        s2 = C.profile(EXE, state_dir=self.ss)
        s3 = C.analyze(REPO, name="T", with_path=EXE,
                       state_dir=self.ss, oil_state_dir=self.os_)
        for s in (s1, s2, s3):
            self.assertIn(DRAFT_STAMP, s["rendered_summary"])
        self.assertIn(DRAFT_STAMP, R.render_status(s3))
        self.assertIn(DRAFT_STAMP, R.render_history([s1, s2, s3]))

    def test_no_forbidden_claims(self):
        s = C.analyze(REPO, name="T", with_path=EXE,
                      state_dir=self.ss, oil_state_dir=self.os_)
        text = (s["rendered_summary"] + R.render_explain(s)).lower()
        for forbidden in ("upgrade complete", "verified working", "app executed",
                          "system fixed"):
            self.assertNotIn(forbidden, text)

    def test_shell_has_no_execution_mechanisms(self):
        """Shell v0.1 must not import/use any execution mechanism."""
        shell_dir = os.path.join(ROOT, "dsiu_shell")
        banned = ("import subprocess", "os.system", "os.popen", "shutil.which",
                  "exec(", "eval(", "import pty")
        offenders = {}
        for fn in os.listdir(shell_dir):
            if not fn.endswith(".py"):
                continue
            with open(os.path.join(shell_dir, fn), encoding="utf-8") as fh:
                src = fh.read()
            hits = [b for b in banned if b in src]
            if hits:
                offenders[fn] = hits
        self.assertEqual(offenders, {})


if __name__ == "__main__":
    unittest.main()
