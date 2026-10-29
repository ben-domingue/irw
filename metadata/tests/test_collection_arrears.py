"""The collection arrears ledger: does the nag fire once, and only on what is new?

Why this exists: the thing being protected is an exit code that must mean
something. `collection_recall.py --report` is wired into the pipeline as an
advisory stage (#3225), so a non-zero exit becomes a line in the run's pull
request body. If it fired on the standing backlog it would fire every run, and
an advisory that always fires is one nobody reads -- the review's own finding
about a check that cries wolf. If it never fired, 126 arrears could sit
invisible for a month again, which is what happened.

So: new arrear fires, unchanged backlog is silent, promotion and withdrawal
take a row OUT, and `first_seen` survives every run because the age of a queue
entry is the whole point.

Offline, synthetic: the script is copied into a tmp tree with four small CSVs
beside it, because it reads its inputs from its own directory. Nothing here
touches the real corpus.
"""
import csv
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "metadata" / "collection_recall.py"


def write_csv(path: Path, rows: list[dict], fields: list[str], eol="\n") -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator=eol)
        w.writeheader()
        w.writerows(rows)


class ArrearsLedger(unittest.TestCase):
    def setUp(self):
        self.dir = Path(self.enterContext(__import__("tempfile").TemporaryDirectory()))
        shutil.copy(SCRIPT, self.dir / "collection_recall.py")
        self.ledger = self.dir / "collection_arrears.csv"
        #: One curated instrument collection. `dass21` is a real id and the
        #: token test is the id itself, so a table named *_dass21 is a candidate.
        write_csv(self.dir / "collections.csv", [
            {"collection": "dass21", "label": "DASS-21", "kind": "instrument",
             "definition": "Tables that administered the DASS-21.", "rule": "curated",
             "coverage": "curated-only", "basis": "curated", "n_tables": "1",
             "maintainer": "bd", "added": "2026-09-30"},
        ], ["collection", "label", "kind", "definition", "rule", "coverage",
            "basis", "n_tables", "maintainer", "added"])
        self.members = [{"table": "alpha_2020_dass21", "collection": "dass21",
                         "basis": "wording"}]
        self.meta = ["alpha_2020_dass21", "beta_2021_dass21"]
        self.sync()

    def sync(self):
        write_csv(self.dir / "collection_members.csv", self.members,
                  ["table", "collection", "basis"])
        write_csv(self.dir / "metadata.csv",
                  [{"table": t, "variables": "id| item| resp"} for t in self.meta],
                  ["table", "variables"])
        write_csv(self.dir / "tags.csv",
                  [{"table": t.lower(), "construct name": ""} for t in self.meta],
                  ["table", "construct name"])

    def run_report(self, today):
        p = subprocess.run([sys.executable, "-I", "collection_recall.py",
                            "--report", "--today", today],
                           cwd=self.dir, capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def rows(self):
        with self.ledger.open(encoding="utf-8", newline="") as fh:
            return {r["table"]: r for r in csv.DictReader(fh)}

    def test_first_run_seeds_the_ledger_and_fires(self):
        rc, out = self.run_report("2026-11-02")
        self.assertEqual(rc, 1, out)
        self.assertIn("1 NEW candidate(s)", out)
        self.assertIn("beta_2021_dass21", out)
        rows = self.rows()
        self.assertEqual(list(rows), ["beta_2021_dass21"])
        self.assertEqual(rows["beta_2021_dass21"]["first_seen"], "2026-11-02")
        self.assertEqual(rows["beta_2021_dass21"]["coverage"], "curated-only")

    def test_unchanged_backlog_is_silent_and_keeps_its_age(self):
        self.run_report("2026-11-02")
        rc, out = self.run_report("2026-11-04")
        self.assertEqual(rc, 0, out)
        self.assertIn("no new arrears", out)
        row = self.rows()["beta_2021_dass21"]
        #: first_seen is the age of the arrear, last_seen is this run.
        self.assertEqual(row["first_seen"], "2026-11-02")
        self.assertEqual(row["last_seen"], "2026-11-04")

    def test_a_new_candidate_fires_and_names_only_itself(self):
        self.run_report("2026-11-02")
        self.meta.append("gamma_2026_dass21")
        self.sync()
        rc, out = self.run_report("2026-11-04")
        self.assertEqual(rc, 1, out)
        self.assertIn("1 NEW candidate(s)", out)
        self.assertIn("new       dass21           gamma_2026_dass21", out)
        rows = self.rows()
        self.assertEqual(rows["beta_2021_dass21"]["first_seen"], "2026-11-02")
        self.assertEqual(rows["gamma_2026_dass21"]["first_seen"], "2026-11-04")

    def test_promotion_takes_the_row_out_and_does_not_fire(self):
        self.run_report("2026-11-02")
        self.members.append({"table": "beta_2021_dass21", "collection": "dass21",
                             "basis": "name"})
        self.sync()
        rc, out = self.run_report("2026-11-04")
        self.assertEqual(rc, 0, out)
        self.assertIn("resolved  dass21           beta_2021_dass21", out)
        self.assertEqual(self.rows(), {})

    def test_withdrawing_the_table_also_resolves_the_row(self):
        self.run_report("2026-11-02")
        self.meta.remove("beta_2021_dass21")
        self.sync()
        rc, out = self.run_report("2026-11-04")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.rows(), {})

    def test_the_ledgers_line_ending_is_preserved(self):
        #: Tracked IRW CSVs are CRLF in some places and LF in others, and a
        #: wholesale conversion puts the entire file in the diff and buries the
        #: row that moved. Detect per file, never per repository.
        self.run_report("2026-11-02")
        raw = self.ledger.read_bytes().replace(b"\n", b"\r\n")
        self.ledger.write_bytes(raw)
        self.meta.append("gamma_2026_dass21")
        self.sync()
        self.run_report("2026-11-04")
        out = self.ledger.read_bytes()
        #: header + two rows, and every LF is part of a CRLF -- no mixed file,
        #: and no stray \r\r\n, which some batch CSVs here really do have.
        self.assertEqual(out.count(b"\r\n"), 3)
        self.assertEqual(out.count(b"\n"), 3)
        self.assertNotIn(b"\r\r", out)

    def test_report_refuses_to_write_a_ledger_for_one_collection(self):
        p = subprocess.run([sys.executable, "-I", "collection_recall.py",
                            "--report", "--collection", "dass21"],
                           cwd=self.dir, capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn("cannot be scoped", p.stdout + p.stderr)
        self.assertFalse(self.ledger.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
