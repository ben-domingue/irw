"""A deposit this pipeline has already staged must not resurface as a candidate.

`_load_existing_irw_dois()` reads the live dictionary SHEET, and a row staged by
`stage_dict_row.py` only reaches that sheet when `metadata/02_biblio.R` next
runs. In between, the deposit is still discoverable. Three of the 106 leads in
the 2026-10-28 re-triage were already-shipped deposits for exactly that reason,
and one of them (10.7910/DVN/EL4KPR -> gries_2011_moral_foundations) nearly got
a second processing script.
"""
import csv
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import irw_discover_updated as d  # noqa: E402

HEADER = ["table", "table.lower", "Description", "URL (for data)", "Reference",
          "DOI (for paper)", "DOI (for data)", "Original License",
          "Custom License", "Public Reshare?", "Derived License",
          "Custom License2", "Notes", "Contributor", "Date"]


def _write(tmp, name, rows):
    path = os.path.join(tmp, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        for r in rows:
            w.writerow(r)
    return path


class TestStagedDictExclusion(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._here = d._HERE
        d._HERE = self.tmp

    def tearDown(self):
        d._HERE = self._here

    def test_reads_both_doi_columns_and_the_url(self):
        _write(self.tmp, "dictionary_auto.csv", [
            # a data DOI in its own column
            ["a", "a", "desc", "https://doi.org/10.7910/DVN/EL4KPR", "ref",
             "", "10.7910/DVN/EL4KPR", "CC0 1.0", "", "Public", "CC0 1.0",
             "", "", "automated", ""],
            # a paper DOI, with the deposit only in the URL
            ["b", "b", "desc", "https://zenodo.org/records/17802433", "ref",
             "10.1234/paper.1", "", "CC BY 4.0", "", "Public", "CC BY 4.0",
             "", "", "automated", ""],
        ])
        got = d._load_staged_dict_exclusions(("dictionary_auto.csv",))
        self.assertIn("10.7910/dvn/el4kpr", {x.lower() for x in got})
        self.assertIn("10.1234/paper.1", {x.lower() for x in got})

    def test_reads_every_source_file(self):
        for name in ("dictionary_auto.csv", "dictionary_auto_comps.csv",
                     "dictionary_auto_nom.csv", "dictionary_auto_sim.csv",
                     "dictionary_auto_conj.csv"):
            stem = name.replace(".csv", "")
            _write(self.tmp, name, [
                [stem, stem, "desc", "", "ref", f"10.5555/{stem}", "",
                 "CC0 1.0", "", "Public", "CC0 1.0", "", "", "automated", ""]])
        got = {x.lower() for x in d._load_staged_dict_exclusions()}
        for name in d.STAGED_DICT_FILES:
            self.assertIn(f"10.5555/{name.replace('.csv','')}", got, name)

    def test_missing_files_are_not_an_error(self):
        self.assertEqual(d._load_staged_dict_exclusions(("nope.csv",)), set())

    def test_live_file_covers_the_three_leads_that_slipped_through(self):
        # Against the repo's real dictionary_auto.csv, not a fixture.
        d._HERE = self._here
        got = {x.lower() for x in d._load_staged_dict_exclusions()}
        for doi in ("10.7910/dvn/el4kpr", "10.7910/dvn/zxqbc7",
                    "10.5281/zenodo.17802433"):
            self.assertIn(doi, got, doi)


if __name__ == "__main__":
    unittest.main()
