"""The dictionary readers read the published record, not the sheet (#2067).

What matters: a table in the export answers from the export, even when the
sheet disagrees (that is the whole point -- the export carries the
Description/licence overrides the sheet never gets); a table the export has
not reached yet falls back to dictionary_auto.csv, then the sheet, and never
comes back `no_data` merely for being new; and the network is not touched when
a local record answers. Offline throughout.
"""
import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import published_dictionary as pdict  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "lookup_dictionary",
    HERE.parent / "tags" / ".claude" / "skills" / "irw-auto-tag" / "scripts"
    / "lookup_dictionary.py")
lookup_dictionary = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lookup_dictionary)

BIBLIO_COLS = ["table", "DOI__for_paper_", "DOI__for_data_", "Reference_x",
               "URL__for_data_", "Original_License", "Derived_License",
               "Custom_License_Terms", "Description", "BibTex"]
AUTO_COLS = ["table", "table.lower", "Description", "URL (for data)", "Reference",
             "DOI (for paper)", "DOI (for data)", "Original License",
             "Custom License (source)", "Public Reshare?", "Derived License",
             "Custom License (derived)", "Notes", "Contributor", "Date",
             "Source via"]


def _write(path, cols, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, cols, lineterminator="\r\n")   # the exports are CRLF
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


class Published(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        _write(self.root / "metadata" / "biblio.csv", BIBLIO_COLS, [
            {"table": "Chronic_2024", "Description": "Chronic-diagnosis checklist",
             "DOI__for_paper_": "10.1000/paper", "Reference_x": "Ref A",
             "Original_License": "CC BY 4.0"},
            {"table": "deposit_2023", "DOI__for_data_": "10.7910/DVN/ABC",
             "Description": "NA"},
        ])
        _write(self.root / "metadata" / "nominal_biblio.csv", BIBLIO_COLS, [
            {"table": "votes_nom", "Description": "Roll calls"},
        ])
        _write(self.root / "automated_finding" / "dictionary_auto.csv", AUTO_COLS, [
            {"table": "New_2026", "table.lower": "new_2026", "Description": "Fresh",
             "DOI (for paper)": "10.1000/fresh", "Contributor": "automated"},
        ])
        self.pub = pdict.load_published(self.root)
        self.auto = pdict.load_auto_rows(self.root)

    def test_keys_lowercased_across_every_export(self):
        self.assertEqual(set(self.pub), {"chronic_2024", "deposit_2023", "votes_nom"})
        self.assertEqual(self.pub["votes_nom"]["file"], "metadata/nominal_biblio.csv")
        self.assertEqual(self.pub["deposit_2023"]["description"], "",
                         "a literal NA is blank, not a Description")

    def test_export_wins_over_the_sheet(self):
        sheet = {"chronic_2024": {"Description": "PROMIS fatigue",
                                  "DOI (for paper)": "10.1000/paper"}}
        out = lookup_dictionary.lookup("CHRONIC_2024", self.pub, self.auto, sheet)
        self.assertEqual(out["description"], "Chronic-diagnosis checklist")
        self.assertEqual(out["source"], "metadata/biblio.csv")

    def test_data_doi_never_returned_as_the_paper_doi(self):
        out = lookup_dictionary.lookup("deposit_2023", self.pub, self.auto, {})
        self.assertEqual(out["doi"], "")
        self.assertEqual(out["data_doi"], "10.7910/DVN/ABC")

    def test_new_table_falls_back_without_the_network(self):
        def sheet():
            raise AssertionError("the sheet must not be fetched for a local hit")
        out = lookup_dictionary.lookup("new_2026", self.pub, self.auto, sheet)
        self.assertTrue(out["matched"])
        self.assertFalse(out["no_data"])
        self.assertEqual(out["doi"], "10.1000/fresh")
        self.assertEqual(out["source"], "automated_finding/dictionary_auto.csv")

    def test_sheet_is_the_last_resort(self):
        out = lookup_dictionary.lookup(
            "only_on_sheet", self.pub, self.auto,
            lambda: {"only_on_sheet": {"Description": "Hand entry"}})
        self.assertEqual((out["description"], out["source"]), ("Hand entry", "sheet"))
        miss = lookup_dictionary.lookup("nowhere", self.pub, self.auto, lambda: {})
        self.assertEqual((miss["matched"], miss["no_data"]), (False, True))

    def test_the_real_exports_load(self):
        real = pdict.load_published()
        self.assertGreater(len(real), 4000)


if __name__ == "__main__":
    unittest.main()
