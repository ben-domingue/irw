"""Conjoint designs route to the `conj` source, not core (#2887).

Detection, the intake screen, and the append to data/conjoint/candidates.csv.
Offline, synthetic; every write goes to a temporary ledger, never the real one.
"""
import csv
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import irw_retriage_ha as R  # noqa: E402
import irw_discover_updated as D  # noqa: E402

HEADER = "doi,title,licence,lead,status,tables,notes\n"


def _row(**kw):
    base = {"source": "dataverse", "title": "A survey", "url": "https://x/y",
            "doi": "10.7910/DVN/AAAAAA", "license": "cc0", "flag": "human_assistance",
            "reasons": "", "n_participants": 1249, "n_items": 2, "n_responses": 2498}
    base.update(kw)
    return base


class Detect(unittest.TestCase):
    def test_title(self):
        self.assertTrue(R.looks_like_conjoint("A Conjoint Analysis of Judges", []))
        self.assertTrue(R.looks_like_conjoint("A discrete choice experiment on tourism", []))
        self.assertIsNone(R.looks_like_conjoint("Big Five inventory norms", []))

    def test_task_and_profile_columns(self):
        self.assertTrue(R.looks_like_conjoint("x", ["id", "task", "profile", "selected"]))
        self.assertIsNone(R.looks_like_conjoint("x", ["id", "task", "rt"]))

    def test_classify_puts_conj_ahead_of_parse_rules(self):
        reasons = "Re-read with sep=';' | Columns present: ['id', 'task', 'profile']"
        flag, _ = R.classify(pd.Series(_row(title="Ideology and LGBTQ judges",
                                            reasons=reasons)))
        self.assertEqual(flag, "conj")

    def test_find_conjoints_covers_good_rows(self):
        df = pd.DataFrame([_row(flag="good", title="A conjoint experiment"),
                           _row(flag="good", doi="10.1/other")])
        self.assertEqual(len(R.find_conjoints(df)), 1)


class Screen(unittest.TestCase):
    def status(self, **kw):
        return R.conj_ledger_row(pd.Series(_row(**kw)), lead="t")["status"]

    def test_open_licences_are_todo(self):
        for lic in ("cc0", "cc-by", "cc-by-sa", "cc-by-+-cc0",
                    "this-work-is-licensed-under-a-cc-by-license.-for-more-information-see-cc-by"):
            self.assertEqual(self.status(license=lic), "todo", lic)

    def test_unknown_licence_stays_todo(self):
        self.assertEqual(self.status(license="unknown"), "todo")
        self.assertEqual(self.status(license=float("nan")), "todo")

    def test_nc_nd_and_no_licence_are_held(self):
        self.assertTrue(self.status(license="cc-by-nc").startswith("held: licence"))
        self.assertTrue(self.status(license="cc-by-nd-4.0").startswith("held: licence"))
        self.assertEqual(self.status(
            license="this-dataset-is-made-available-with-limited-information-on-how-it-can-be-used."),
            "held: no licence")

    def test_under_100_respondents_is_held(self):
        self.assertIn("fewer than 100", self.status(n_participants=41))

    def test_doi_is_normalised(self):
        rec = R.conj_ledger_row(pd.Series(_row(doi="https://doi.org/10.7910/DVN/CDLVDH")), lead="t")
        self.assertEqual(rec["doi"], "10.7910/dvn/cdlvdh")


class Ledger(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "candidates.csv")
        with open(self.path, "w") as f:
            f.write(HEADER + "10.7910/dvn/thjyqr,Old,CC0 1.0,pilot,uploaded,t,n")  # no final newline

    def tearDown(self):
        self.dir.cleanup()

    def route(self, rows):
        with redirect_stdout(io.StringIO()):
            return R.route_conjoints(pd.DataFrame(rows), date="2026-10-07", ledger=self.path)

    def read(self):
        with open(self.path, newline="") as f:
            return list(csv.DictReader(f))

    def test_appends_todo_and_skips_known_dois(self):
        n = self.route([_row(doi="10.7910/DVN/CDLVDH"), _row(doi="10.7910/DVN/THJYQR")])
        self.assertEqual(n, 1)
        rows = self.read()
        self.assertEqual([r["doi"] for r in rows], ["10.7910/dvn/thjyqr", "10.7910/dvn/cdlvdh"])
        new = rows[1]
        self.assertEqual(new["status"], "todo")
        self.assertEqual(new["lead"], "automated_finding dataverse 2026-10-07")
        self.assertIn("est. respondents: 1249", new["notes"])

    def test_rerun_adds_nothing(self):
        self.route([_row(doi="10.1/a")])
        self.assertEqual(self.route([_row(doi="10.1/a")]), 0)
        self.assertEqual(len(self.read()), 2)

    def test_wrong_header_is_left_alone(self):
        with open(self.path, "w") as f:
            f.write("doi,title\n")
        with redirect_stdout(io.StringIO()):
            n = R.route_conjoints(pd.DataFrame([_row()]), ledger=self.path,
                                  stream=io.StringIO())
        self.assertEqual(n, 0)

    def test_discovery_excludes_ledger_dois(self):
        self.assertIn("10.7910/dvn/thjyqr", D._load_conj_ledger_exclusions(self.path))


if __name__ == "__main__":
    unittest.main()
