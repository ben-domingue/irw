"""Tests for find_codebook_links.py (#2766, #2770): the rules that decide what
counts as a source codebook. No network: only the pure functions are tested.

THE RULE THESE GUARD: never guess a codebook. A file counts by its NAME
(codebook, data dictionary, ...), a README by its TEXT naming the table's own
columns, and an ingest record because a person read it. Everything else stays
out of the page.
"""
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fcl", HERE / "find_codebook_links.py")
fcl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fcl)


class NameMatchTest(unittest.TestCase):
    def test_codebook_names(self):
        for n in ["Codebook.pdf", "Data key for the instrument.pdf", "my_dictionary.csv",
                  "Variable_labels.xlsx", "variables.xlsx", "diccionario_datos.xlsx",
                  "COACH_Code Book_Final_version.xlsx"]:
            self.assertEqual(fcl.match(n), "name_codebook", n)

    def test_readme_names(self):
        for n in ["README.txt", "Read me.docx", "LÉAME.docx", "_README.rtf"]:
            self.assertEqual(fcl.match(n), "name_readme", n)

    def test_code_and_data_files_never_count(self):
        ##a data file named variables_* (caught in the 10-02 sweep), the code
        ##that writes a codebook, and R data files
        for n in ["variables_BG_excloutliers.csv", "codebook.R", "make_codebook.py",
                  "variables_NA.Rdata", "codebook.rds", "data.csv", "S1_File.pdf"]:
            self.assertIsNone(fcl.match(n), n)


class RouteTest(unittest.TestCase):
    def test_hosts(self):
        self.assertEqual(fcl.route("https://osf.io/8jtn9/overview"), ("osf", "8jtn9"))
        self.assertEqual(fcl.route("https://zenodo.org/records/5156068"), ("zenodo", "5156068"))
        self.assertEqual(fcl.route("https://doi.org/10.7910/DVN/ZNGS1K"),
                         ("dataverse", "dataverse.harvard.edu|doi:10.7910/DVN/ZNGS1K"))
        self.assertEqual(fcl.route("https://doi.org/10.1371/journal.pone.0278165.s004"),
                         ("skip", "plos_supplementary"))

    def test_a_dataverse_file_pid_routes_to_its_dataset(self):
        h, k = fcl.route("https://dataverse.harvard.edu/file.xhtml?persistentId="
                         "doi:10.7910/DVN/1KDJTZ/QTQOC4&version=1.0")
        self.assertEqual((h, k), ("dataverse", "dataverse.harvard.edu|doi:10.7910/DVN/1KDJTZ"))

    def test_figshare_private_links_are_not_crawled(self):
        self.assertEqual(fcl.route("https://figshare.com/s/59a2c9e849bc019da6e4?file=1")[0], "skip")


class ReadmeNamesTest(unittest.TestCase):
    def test_whole_word_matching(self):
        text = "RMEQ1 to RMEQ5: items. Sexo: Gender (1=Male, 2=Female). Edad: age."
        self.assertEqual(fcl.names_in_text(["RMEQ1", "RMEQ5", "sexo", "edad", "RMEQ"], text),
                         ["RMEQ1", "RMEQ5", "sexo", "edad"])

    def test_word_items_of_a_stimulus_set_do_not_count(self):
        ##a lexical task's items are English words and match any README
        items = ["choice", "that", "this", "card"] + [f"w{i}" for i in range(200)]
        names = fcl.table_names("lex", None, {"lex": items}, {}, offline=True)
        self.assertNotIn("that", names)
        self.assertIn("w17", names)   # identifier-shaped items still count

    def test_plain_words_in_a_script_do_not_count(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.R"
            p.write_text('df$subid <- x[["SubID"]]; read.csv("data.csv"); m <- "files"\n'
                         'y <- df[c("BC_10", "university")]')
            lits = fcl.script_literals([str(p)])
        self.assertEqual(lits, {"SubID", "BC_10"})


class IngestLinksTest(unittest.TestCase):
    def test_recorded_urls_become_rows_and_none_does_not(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "codebook_at_ingest.csv"
            with open(p, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["table", "source", "codebook_url", "recorded_at"])
                w.writerow(["foo_2026", "core", "https://osf.io/abcde/files/osfstorage/1a/Codebook%20v2.pdf", "2026-10-02"])
                w.writerow(["bar_2026", "core", "none", "2026-10-02"])
                w.writerow(["retired_2019", "core", "https://x.org/cb.pdf", "2026-01-01"])
            old = fcl.INGEST_CODEBOOKS
            fcl.INGEST_CODEBOOKS = p
            try:
                rows = fcl.ingest_links({"foo_2026", "bar_2026"})
            finally:
                fcl.INGEST_CODEBOOKS = old
        self.assertEqual([(r["table"], r["how_found"], r["file_name"], r["host"]) for r in rows],
                         [("foo_2026", "recorded_at_ingest", "Codebook v2.pdf", "osf.io")])


if __name__ == "__main__":
    unittest.main()
