"""Tests for DSIU-Daemon — the explicit watcher/supervisor.

Stdlib unittest only. Run: python -m unittest discover -s tests
"""

import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dsiu_daemon import DRAFT_STAMP  # noqa: E402
from dsiu_daemon import events as E  # noqa: E402
from dsiu_daemon import render as R  # noqa: E402
from dsiu_daemon import supervisor as S  # noqa: E402
from dsiu_daemon.config import WatchConfig  # noqa: E402


class DaemonBase(unittest.TestCase):
    def setUp(self):
        self.state = tempfile.mkdtemp()
        self.oil = tempfile.mkdtemp()
        self.shell = tempfile.mkdtemp()
        self.target = tempfile.mkdtemp()
        with open(os.path.join(self.target, "parser.py"), "w") as fh:
            fh.write("def parse(x):\n    return x\n")

    def tearDown(self):
        for d in (self.state, self.oil, self.shell, self.target):
            shutil.rmtree(d, ignore_errors=True)

    def _config(self, **kw):
        return WatchConfig(path=self.target, name="T", interval=0,
                           state_dir=self.state, oil_state_dir=self.oil,
                           shell_state_dir=self.shell, **kw)

    def _event_count(self):
        return len([f for f in os.listdir(self.state) if f.startswith("event-")])


class TestOnce(DaemonBase):
    def test_once_creates_one_event(self):
        ev = S.run_once(self._config())
        self.assertEqual(ev["event_type"], "baseline")
        self.assertEqual(self._event_count(), 1)

    def test_change_is_detected(self):
        S.run_once(self._config())  # baseline
        with open(os.path.join(self.target, "renderer.py"), "w") as fh:
            fh.write("def render(x):\n    return x\n")
        ev = S.run_once(self._config())
        self.assertEqual(ev["event_type"], "changed")
        self.assertTrue(ev["analyzed"])
        self.assertIn("renderer.py", ev["changed_files"])

    def test_unchanged_no_fake_movement(self):
        S.run_once(self._config())  # baseline
        ev = S.run_once(self._config())  # nothing changed
        self.assertEqual(ev["event_type"], "no_change")
        self.assertFalse(ev["analyzed"])
        self.assertIsNone(ev["movement_score"])
        md = R.render_event_report(ev).lower()
        self.assertNotIn("improvement", md.split("movement ≠ improvement")[0]
                         if "movement ≠ improvement" in md else md)

    def test_analysis_records_shell_session_path_and_raw(self):
        ev = S.run_once(self._config())
        self.assertIsNotNone(ev["shell_session"])
        self.assertIsNotNone(ev["shell_session_path"])
        self.assertTrue(os.path.isfile(ev["shell_session_path"]))


class TestWatch(DaemonBase):
    def test_watch_is_bounded(self):
        events = S.run_watch(self._config(), max_cycles=1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "baseline")

    def test_watch_suppresses_no_change_spam(self):
        # baseline + 2 no_change cycles -> only baseline + ONE no_change saved
        S.run_watch(self._config(), max_cycles=3)
        self.assertEqual(self._event_count(), 2)

    def test_watch_record_no_change_writes_each(self):
        S.run_watch(self._config(record_no_change=True), max_cycles=3)
        self.assertEqual(self._event_count(), 3)


class TestErrors(DaemonBase):
    def test_missing_path_is_draft_error_event(self):
        cfg = WatchConfig(path=os.path.join(self.target, "nope"), name="E",
                          interval=0, state_dir=self.state)
        ev = S.run_once(cfg)
        self.assertEqual(ev["event_type"], "error")
        self.assertFalse(ev["analyzed"])
        self.assertIn(DRAFT_STAMP, ev["status"])


class TestReadCommands(DaemonBase):
    def test_status_reads_latest(self):
        S.run_once(self._config())
        self.assertIsNotNone(E.latest_event(self.state))

    def test_history_lists(self):
        S.run_once(self._config())
        with open(os.path.join(self.target, "b.py"), "w") as fh:
            fh.write("x=2\n")
        S.run_once(self._config())
        self.assertEqual(len(E.list_events(self.state)), 2)

    def test_explain_renders(self):
        S.run_once(self._config())
        md = R.render_explain(E.latest_event(self.state))
        self.assertIn("What was observed", md)
        self.assertIn(DRAFT_STAMP, md)

    def test_read_views_do_not_write(self):
        S.run_once(self._config())
        before = self._event_count()
        E.latest_event(self.state)
        E.list_events(self.state)
        R.render_status(E.latest_event(self.state))
        self.assertEqual(self._event_count(), before)


class TestLaw0AndSafety(DaemonBase):
    def test_all_outputs_draft(self):
        ev = S.run_once(self._config())
        self.assertIn(DRAFT_STAMP, ev["status"])
        for md in (R.render_event_report(ev), R.render_status(ev),
                   R.render_history([ev]), R.render_explain(ev)):
            self.assertIn(DRAFT_STAMP, md)

    def test_no_execution_mechanisms_in_source(self):
        daemon_dir = os.path.join(ROOT, "dsiu_daemon")
        banned = ("import subprocess", "os.system", "os.popen", "shutil.which",
                  "exec(", "eval(", "import pty")
        offenders = {}
        for fn in os.listdir(daemon_dir):
            if not fn.endswith(".py"):
                continue
            with open(os.path.join(daemon_dir, fn), encoding="utf-8") as fh:
                src = fh.read()
            hits = [b for b in banned if b in src]
            if hits:
                offenders[fn] = hits
        self.assertEqual(offenders, {})


if __name__ == "__main__":
    unittest.main()
