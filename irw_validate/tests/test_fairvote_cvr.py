"""fairvote_cvr.py strips leading and trailing whitespace from cov_ values and from nothing else (#3024)."""
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "fairvote_cvr", Path(__file__).resolve().parents[2] / "data" / "rankings" / "fairvote_cvr.py")
fv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fv)

META = {"table": "rcv_town_20221108_council", "collection": "10.7910/DVN/AMK8PJ", "method": "irv",
        "file_id": "0", "dataset_version": "1"}


class CovWhitespace(unittest.TestCase):
    def test_cov_values_are_stripped(self):
        rows = [["ballotID", "rank1", "rank2", "precinct", "precinctPortion"],
                ["1", "Alpha", "Beta", "P1", "P1 - Early - 1 "],
                ["2", "Beta", "skipped", "P1", "P1 - Early - 1"],
                ["3", "skipped", "skipped", "P1 ", " P1 - Early - 1"]]
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "Town_20221108_CityCouncil.tab"
            with open(src, "w", newline="", encoding="utf-8") as f:
                csv.writer(f, delimiter="\t", lineterminator="\n").writerows(rows)
            out, design, warn = fv.convert(src, META)
        self.assertEqual({r["cov_precinct_portion"] for r in out}, {"P1 - Early - 1"})
        # id, item and resp are untouched: same rows as before the change.
        self.assertEqual([(r["id"], r["item"], r["resp"]) for r in out], [(1, "c01", 1), (1, "c02", 2), (2, "c02", 1)])
        # The unmarked ballot 3 sits in precinct "P1 ", the same precinct as the marked ballots once stripped.
        self.assertEqual(design["n_ballots_eligible_est"], 3)
        self.assertEqual(warn, [])


if __name__ == "__main__":
    unittest.main()
