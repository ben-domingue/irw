#!/usr/bin/env python3
"""Tests for pipeline_gate.py's rotation clause.

The intake half of the gate needs Redivis and is not covered here; the
rotation half needs nothing but two CSVs, which is the point of checking it
first in decide().

Run: python3 -m unittest metadata.tests.test_pipeline_gate
"""
import csv
import datetime as dt
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GATE = REPO / ".claude" / "skills" / "irw-site-update" / "scripts" / "pipeline_gate.py"

spec = importlib.util.spec_from_file_location("pipeline_gate", GATE)
gate = importlib.util.module_from_spec(spec)
sys.modules["pipeline_gate"] = gate
spec.loader.exec_module(gate)

NOW = dt.datetime(2026, 10, 18, 12, 0, 0)


def write_metadata(path: Path, tables) -> None:
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["table", "n_responses"])
        for t in tables:
            w.writerow([t, 1])


def write_log(path: Path, rows) -> None:
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["table", "refreshed_at"])
        for name, when in rows:
            w.writerow([name, when])


class RotationClause(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.meta = self.dir / "metadata.csv"
        self.log = self.dir / "metadata_refresh_log.csv"
        self.addCleanup(self.tmp.cleanup)

    def behind(self, max_age=35.0):
        return gate.rotation_behind(self.meta, self.log, max_age, now=NOW)

    def test_never_refreshed_table_is_sweep_debt(self):
        write_metadata(self.meta, ["a", "b"])
        write_log(self.log, [("a", "2026-10-17 00:00:00")])
        run, why = self.behind()
        self.assertTrue(run)
        self.assertIn("1 described table(s) never re-checked", why)

    def test_all_recent_is_not_a_reason_to_run(self):
        write_metadata(self.meta, ["a", "b"])
        write_log(self.log, [("a", "2026-10-17 00:00:00"), ("b", "2026-10-16 00:00:00")])
        run, why = self.behind()
        self.assertFalse(run)
        self.assertIn("rolling refresh current", why)

    def test_oldest_past_the_limit_is_a_reason_to_run(self):
        write_metadata(self.meta, ["a"])
        write_log(self.log, [("a", "2026-08-01 00:00:00")])  # 78 days
        run, why = self.behind()
        self.assertTrue(run)
        self.assertIn("78 days old", why)

    def test_withdrawn_table_in_the_log_is_not_debt(self):
        ##a stale log entry for a table metadata.csv no longer describes must
        ##not keep the gate open forever
        write_metadata(self.meta, ["a"])
        write_log(self.log, [("a", "2026-10-17 00:00:00"), ("gone", "2026-01-01 00:00:00")])
        run, why = self.behind()
        self.assertFalse(run, why)

    def test_case_is_folded_on_both_sides(self):
        write_metadata(self.meta, ["MixedCase"])
        write_log(self.log, [("mixedcase", "2026-10-17 00:00:00")])
        run, why = self.behind()
        self.assertFalse(run, why)

    def test_missing_log_means_the_whole_corpus_is_debt(self):
        write_metadata(self.meta, ["a", "b"])
        run, why = self.behind()
        self.assertTrue(run)
        self.assertIn("2 described table(s) never re-checked", why)

    def test_unparseable_stamp_is_ignored_not_fatal(self):
        write_metadata(self.meta, ["a", "b"])
        write_log(self.log, [("a", "not a date"), ("b", "2026-10-17 00:00:00")])
        run, why = self.behind()
        ##"a" has an entry, so it is not "never re-checked"; its unreadable
        ##stamp simply does not contribute an age
        self.assertFalse(run, why)

    def test_unreadable_log_fails_open(self):
        write_metadata(self.meta, ["a"])
        self.log.write_bytes(b"\xff\xfe\x00bad")
        run, why = gate.rotation_behind(self.meta, self.log, 35.0, now=NOW)
        self.assertTrue(run)
        self.assertIn("could not read", why)


if __name__ == "__main__":
    unittest.main()
