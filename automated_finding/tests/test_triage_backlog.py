"""irw_batch_updated.py --backlog: what a capped or failed run still owes comes back (irw#3388)."""
import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import irw_batch_updated as b  # noqa: E402

COLS = ["source", "title", "doi", "published", "url"]


def _write(path, rows, cols=COLS):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def _read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cand(n, src="zenodo"):
    return {"source": src, "title": f"t{n}", "doi": f"10.5281/zenodo.{n}", "published": "", "url": ""}


class BacklogTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = os.getcwd()
        os.chdir(self.tmp.name)
        self.addCleanup(os.chdir, self.cwd)
        self.flags = {}          # doi -> flag process_one returns; default no_usable_file
        self.calls = []

        def fake(row):
            self.calls.append(row["doi"])
            flag = self.flags.get(row["doi"], "no_usable_file")
            reasons = "skipped -- zenodo blocked earlier this run" if flag == "skipped" else "x"
            return {"source": row["source"], "title": row["title"], "url": row["url"],
                    "doi": row["doi"], "license": "", "n_responses": "", "n_participants": "",
                    "n_items": "", "density": "", "data_file": "",
                    "flag": "download_failed" if flag == "skipped" else flag, "reasons": reasons}
        p = mock.patch.object(b, "process_one", side_effect=fake)
        p.start()
        self.addCleanup(p.stop)

    def run_(self, cands, limit=None, backlog="backlog.csv"):
        _write("cands.csv", cands)
        b.run_batch("cands.csv", "out.csv", limit, resume=False, checkpoint="ck.jsonl", backlog=backlog)
        return _read(backlog) if backlog and os.path.exists(backlog) else None

    def test_cap_remainder_is_written_back_and_triaged_first_next_time(self):
        owed = self.run_([cand(i) for i in range(5)], limit=2)
        self.assertEqual([r["doi"] for r in owed], [f"10.5281/zenodo.{i}" for i in (2, 3, 4)])
        self.assertTrue(all(r["attempts"] == "0" and r["first_seen"] for r in owed))
        first_seen = owed[0]["first_seen"]
        self.calls.clear()
        owed = self.run_([cand(9)], limit=2)          # a new candidate arrives
        self.assertEqual(self.calls, ["10.5281/zenodo.2", "10.5281/zenodo.3"])  # backlog first
        self.assertEqual([r["doi"] for r in owed], ["10.5281/zenodo.4", "10.5281/zenodo.9"])
        self.assertEqual(owed[0]["first_seen"], first_seen)   # carried, not reset

    def test_download_failed_retries_then_drops_after_three(self):
        self.flags["10.5281/zenodo.1"] = "download_failed"
        for attempt in (1, 2):
            owed = self.run_([cand(1)])
            self.assertEqual([(r["doi"], r["attempts"]) for r in owed], [("10.5281/zenodo.1", str(attempt))])
        owed = self.run_([])
        self.assertEqual(owed, [])
        self.assertNotIn("10.5281/zenodo.1", b.load_seen_keys())   # never a sticky verdict

    def test_a_blocked_source_skip_is_not_an_attempt(self):
        self.flags["10.5281/zenodo.1"] = "skipped"
        owed = self.run_([cand(1)])
        self.assertEqual(owed[0]["attempts"], "0")

    def test_verdicts_leave_the_backlog_and_enter_the_ledger(self):
        self.flags["10.5281/zenodo.1"] = "good"
        owed = self.run_([cand(1), cand(2)])
        self.assertEqual(owed, [])
        self.assertTrue({"10.5281/zenodo.1", "10.5281/zenodo.2"} <= b.load_seen_keys())

    def test_rows_already_in_the_ledger_are_dropped_from_the_backlog(self):
        b.append_seen_keys([("10.5281/zenodo.3", "no_usable_file")])
        _write("backlog.csv", [{**cand(3), "first_seen": "2026-11-02", "attempts": "0"}],
               COLS + b.BACKLOG_EXTRA)
        owed = self.run_([])
        self.assertEqual(self.calls, [])
        self.assertEqual(owed, [])

    def test_a_candidate_already_in_the_backlog_is_not_doubled(self):
        _write("backlog.csv", [{**cand(4), "first_seen": "2026-11-02", "attempts": "1"}],
               COLS + b.BACKLOG_EXTRA)
        owed = self.run_([cand(4), cand(5)], limit=0 or None)
        self.assertEqual(self.calls, ["10.5281/zenodo.4", "10.5281/zenodo.5"])
        self.assertEqual(owed, [])

    def test_without_backlog_nothing_is_written(self):
        self.assertIsNone(self.run_([cand(i) for i in range(3)], limit=1, backlog=None))
        self.assertFalse(os.path.exists("backlog.csv"))


if __name__ == "__main__":
    unittest.main()
