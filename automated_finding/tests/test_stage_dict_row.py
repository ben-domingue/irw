"""Tests for stage_dict_row.py, the dictionary staging writer (#1732).

THE TEST THAT MATTERS is test_leading_dash_is_not_escaped. The first version of
this script prefixed an apostrophe to any value starting with "=", "+", "-" or
"@", carried over from the paste path where Sheets reads those as a formula.
Nothing is pasted any more -- 02_biblio.R reads this file directly -- so the
apostrophe corrupted the value instead of protecting it. Replaying the
7/13/2026 batch caught it: two Notes cells legitimately begin "-1 sentinel
values ..." and came back with a leading quote. Three such cells exist in the
live sheet today.
"""
import csv
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "stage_dict_row.py"


class StageDictRowTest(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        os.unlink(self.path)

    def tearDown(self):
        for p in (self.path, self.path + ".codebook.csv"):
            if os.path.exists(p):
                os.unlink(p)

    def stage(self, payload):
        env = dict(os.environ, IRW_DICT_AUTO_PATH=self.path,
                   IRW_CODEBOOK_INGEST_PATH=self.path + ".codebook.csv")
        return subprocess.run([sys.executable, str(SCRIPT)], input=payload,
                              text=True, capture_output=True, env=env)

    def rows(self):
        with open(self.path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    ##A minimal row that passes every refusal, so each test varies one thing.
    def ok_payload(self, **kw):
        base = {"table": "a_2026", "public_reshare": "Public",
                "derived_license": "CC BY 4.0"}
        base.update(kw)
        import json
        return json.dumps(base)

    def test_leading_dash_is_not_escaped(self):
        note = "-1 sentinel values (unfinished ESM sessions) excluded before upload"
        r = self.stage(self.ok_payload(notes=note))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.rows()[0]["Notes"], note)

    def test_other_formula_prefixes_are_not_escaped(self):
        for value in ("=2 or more", "+1 wave", "@home administration"):
            with self.subTest(value=value):
                if os.path.exists(self.path):
                    os.unlink(self.path)
                self.stage(self.ok_payload(notes=value))
                self.assertEqual(self.rows()[0]["Notes"], value)

    def test_comma_quote_newline_round_trip(self):
        desc = 'A comma, a "quote", and\na newline'
        self.stage(self.ok_payload(description=desc))
        self.assertEqual(self.rows()[0]["Description"], desc)

    def test_contributor_is_forced(self):
        self.stage(self.ok_payload())
        self.assertEqual(self.rows()[0]["Contributor"], "automated")

    def test_table_lower_is_derived_not_supplied(self):
        self.stage(self.ok_payload(table="Su_2024_PHQ"))
        row = self.rows()[0]
        self.assertEqual(row["table"], "Su_2024_PHQ")
        self.assertEqual(row["table.lower"], "su_2024_phq")

    def test_blank_public_reshare_is_refused(self):
        r = self.stage('{"table": "a_2026", "derived_license": "CC BY 4.0"}')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("public_reshare", r.stderr)

    def test_public_row_without_licence_is_refused(self):
        r = self.stage('{"table": "a_2026", "public_reshare": "Public"}')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("derived_license", r.stderr)

    def test_unknown_field_is_refused(self):
        r = self.stage(self.ok_payload(bogus="x"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("unknown field", r.stderr)

    def test_duplicate_table_is_refused_case_insensitively(self):
        self.stage(self.ok_payload(table="A_2026"))
        r = self.stage(self.ok_payload(table="a_2026"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("already in", r.stderr)
        r = self.stage(self.ok_payload(table="a_2026") )
        self.assertNotEqual(r.returncode, 0)

    def test_header_mismatch_is_refused(self):
        ##Appending a wider row under a narrower header shifts every value
        ##silently. Refuse instead.
        with open(self.path, "w", newline="", encoding="utf-8") as f:
            f.write("table,Description\n")
        r = self.stage(self.ok_payload())
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("header", r.stderr)


class DataDoiRoutingTest(StageDictRowTest):
    """#1690: a deposit DOI must not land in `DOI (for paper)`."""

    def test_data_doi_is_routed_to_its_own_column(self):
        r = self.stage(self.ok_payload(
            table="feng2026_x", doi="https://doi.org/10.7910/DVN/ZDNSFJ"))
        self.assertEqual(r.returncode, 0, r.stderr)
        row = self.rows()[0]
        self.assertEqual(row["DOI (for data)"], "10.7910/DVN/ZDNSFJ")
        self.assertEqual(row["DOI (for paper)"], "")

    def test_an_article_doi_stays_put(self):
        r = self.stage(self.ok_payload(
            table="a_2020", doi="10.1371/journal.pone.0146050"))
        self.assertEqual(r.returncode, 0, r.stderr)
        row = self.rows()[0]
        self.assertEqual(row["DOI (for paper)"], "10.1371/journal.pone.0146050")
        self.assertEqual(row["DOI (for data)"], "")

    def test_a_caller_that_knows_better_is_not_overridden(self):
        ##Both supplied: the paper DOI is a paper DOI, so nothing is routed.
        r = self.stage(self.ok_payload(
            table="b_2021", doi="10.1371/journal.pone.0146050",
            doi_data="https://doi.org/10.7910/DVN/ZDNSFJ"))
        self.assertEqual(r.returncode, 0, r.stderr)
        row = self.rows()[0]
        self.assertEqual(row["DOI (for paper)"], "10.1371/journal.pone.0146050")
        self.assertEqual(row["DOI (for data)"], "10.7910/DVN/ZDNSFJ")

    def test_free_text_is_refused(self):
        r = self.stage(self.ok_payload(
            table="c_2022", doi="not yet published"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not a DOI", r.stderr + r.stdout)

    def test_several_dois_in_one_cell_are_refused(self):
        r = self.stage(self.ok_payload(
            table="d_2023", doi="10.7910/DVN/PNGUT5; 10.7910/DVN/7A9YMV"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("more than one DOI", r.stderr + r.stdout)


    ##--source (#2628): one automated file per dictionary sheet.
    def test_source_flag_stages_a_row(self):
        env = dict(os.environ, IRW_DICT_AUTO_PATH=self.path)
        r = subprocess.run([sys.executable, str(SCRIPT), "--source", "nom"],
                           input=self.ok_payload(), text=True,
                           capture_output=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.rows()[0]["table"], "a_2026")

    def test_unknown_source_is_refused(self):
        env = dict(os.environ, IRW_DICT_AUTO_PATH=self.path)
        r = subprocess.run([sys.executable, str(SCRIPT), "--source=nominal"],
                           input=self.ok_payload(), text=True,
                           capture_output=True, env=env)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("unknown --source", r.stderr + r.stdout)
        self.assertFalse(os.path.exists(self.path))

    def test_source_picks_the_matching_file(self):
        sys.path.insert(0, str(SCRIPT.parent))
        import stage_dict_row
        old = os.environ.pop("IRW_DICT_AUTO_PATH", None)
        try:
            for src, name in [("core", "dictionary_auto.csv"),
                              ("comps", "dictionary_auto_comps.csv"),
                              ("nom", "dictionary_auto_nom.csv"),
                              ("sim", "dictionary_auto_sim.csv"),
                              ("conj", "dictionary_auto_conj.csv")]:
                with self.subTest(source=src):
                    self.assertEqual(stage_dict_row.staging_path(src),
                                     SCRIPT.parent / name)
        finally:
            if old is not None:
                os.environ["IRW_DICT_AUTO_PATH"] = old

    def test_committed_source_files_have_the_stager_header(self):
        sys.path.insert(0, str(SCRIPT.parent))
        import stage_dict_row
        for name in stage_dict_row.SOURCE_FILES.values():
            with self.subTest(file=name):
                with open(SCRIPT.parent / name, newline="", encoding="utf-8") as f:
                    self.assertEqual(next(csv.reader(f)), stage_dict_row.COLUMNS)

class CodebookAtIngestTest(StageDictRowTest):
    """codebook_url (#2770): recorded beside the dictionary, not in it."""

    BASE = ('{"table": "%s", "description": "d", "public_reshare": "Public", '
            '"derived_license": "CC BY 4.0", "codebook_url": "%s"}')

    def codebook_rows(self):
        with open(self.path + ".codebook.csv", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_url_is_recorded_and_not_a_dictionary_column(self):
        r = self.stage(self.BASE % ("foo_2026", "https://osf.io/abcde/files/osfstorage/1"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("codebook_url", self.rows()[0])
        cb = self.codebook_rows()
        self.assertEqual([(c["table"], c["source"], c["codebook_url"]) for c in cb],
                         [("foo_2026", "core", "https://osf.io/abcde/files/osfstorage/1")])

    def test_none_is_accepted_and_restaging_replaces(self):
        self.assertEqual(self.stage(self.BASE % ("foo_2026", "None")).returncode, 0)
        self.assertEqual([c["codebook_url"] for c in self.codebook_rows()], ["none"])
        env = dict(os.environ, IRW_DICT_AUTO_PATH=self.path,
                   IRW_CODEBOOK_INGEST_PATH=self.path + ".codebook.csv")
        r = subprocess.run([sys.executable, str(SCRIPT), "--force"],
                           input=self.BASE % ("foo_2026", "https://x.org/cb.pdf"),
                           text=True, capture_output=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([c["codebook_url"] for c in self.codebook_rows()], ["https://x.org/cb.pdf"])

    def test_a_guess_that_is_not_a_url_is_refused_before_anything_is_written(self):
        r = self.stage(self.BASE % ("foo_2026", "probably the PDF on OSF"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("codebook_url", r.stderr)
        self.assertFalse(os.path.exists(self.path))


if __name__ == "__main__":
    unittest.main()
