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
                  "variables_NA.Rdata", "codebook.rds", "data.csv", "S1_File.pdf",
                  "CODEBOOK_TEMPLATE.docx"]:
            self.assertIsNone(fcl.match(n), n)


class RouteTest(unittest.TestCase):
    def test_hosts(self):
        self.assertEqual(fcl.route("https://osf.io/8jtn9/overview"), ("osf", "8jtn9"))
        self.assertEqual(fcl.route("https://zenodo.org/records/5156068"), ("zenodo", "5156068"))
        self.assertEqual(fcl.route("https://doi.org/10.7910/DVN/ZNGS1K"),
                         ("dataverse", "dataverse.harvard.edu|doi:10.7910/DVN/ZNGS1K"))
        self.assertEqual(fcl.route("https://doi.org/10.1371/journal.pone.0278165.s004"),
                         ("plos", "10.1371/journal.pone.0278165"))

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


class JournalSupplementTest(unittest.TestCase):
    """#2792: PLOS / Europe PMC supplementary files, judged by caption, sheet
    names and (text documents only) content, never by guessing."""

    def test_routes(self):
        self.assertEqual(fcl.route("https://journals.plos.org/plosone/article/file?type=supplementary"
                                   "&id=10.1371/journal.pone.0310665.s001"),
                         ("plos", "10.1371/journal.pone.0310665"))
        self.assertEqual(fcl.route("https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0201007"),
                         ("plos", "10.1371/journal.pone.0201007"))
        self.assertEqual(fcl.route("https://europepmc.org/article/PMC/PMC9472413"), ("epmc", "PMC9472413"))
        self.assertEqual(fcl.route("https://europepmc.org/article/MED/123")[0], "skip")

    def test_captions(self):
        self.assertEqual(fcl.caption_kind("S2 File", "Codebook for the survey. (PDF)"), "name_codebook")
        self.assertEqual(fcl.caption_kind("S1 Table", "Description of the variables. (DOCX)"), "name_codebook")
        self.assertEqual(fcl.caption_kind("S1 Questionnaire", "(DOCX)"), "questionnaire")
        self.assertEqual(fcl.caption_kind("S2 File", "Research instruments. (DOCX)"), "questionnaire")
        ##pilot false positives, 10-02
        self.assertEqual(fcl.caption_kind("S2 Table", "Pearson's correlation coefficients (r) between PHQ-9 "
                                          "items and with other questionnaires. (DOCX)"), "data_or_results")
        self.assertEqual(fcl.caption_kind("S3 Data", "Data processing output. (DOCX)"), "data_or_results")
        self.assertEqual(fcl.caption_kind("S1 File", "Questionnaire responses. (XLSX)"), "data_or_results")
        self.assertIsNone(fcl.caption_kind("S1 File", "(PDF)"))

    def test_jats_supplements(self):
        xml = ('<supplementary-material id="a" mimetype="application/pdf" xlink:href="info:doi/x.s001">'
               '<label>S1 File</label><caption><p>Codebook. (PDF)</p></caption></supplementary-material>'
               '<supplementary-material id="b"><media xlink:href="f.xlsx" mimetype="application" '
               'mime-subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet"><caption><p>'
               '<bold>Additional file 1.</bold></p></caption></media></supplementary-material>'
               '<supplementary-material id="c"><media xlink:href="f.xlsx"/></supplementary-material>')
        s = fcl.jats_supplements(xml)
        self.assertEqual([x["href"] for x in s], ["info:doi/x.s001", "f.xlsx"])   ##deduplicated
        self.assertEqual(s[0]["label"], "S1 File")
        self.assertEqual(fcl._ext_of(s[0]), "pdf")
        self.assertEqual(fcl._ext_of(s[1]), "xlsx")

    def _res(self, files):
        return {"status": "ok", "landing": "L", "files": files}

    def test_sheet_names_and_data_files(self):
        fcl._TEXTS = {"u/doc": "text", "u/own": "text"}
        res = self._res([
            {"name": "S1_Data.xlsx", "url": "u/x", "label": "S1 Data", "caption": "(XLSX)",
             "sheets": ["Data", "Codebook"]},
            {"name": "S2_Data.xlsx", "url": "u/y", "label": "S2 Data", "caption": "(XLSX)",
             "sheets": ["Sheet1", "Variables"]},
            {"name": "S3_File.xlsx", "url": "u/z", "label": "S3 File", "caption": "(XLSX)",
             "sheets": ["Sheet1"]},
            {"name": "S1_File.docx", "url": "u/doc", "label": "S1 File", "caption": "(DOCX)", "supp_id": "s004"},
            {"name": "S2_File.pdf", "url": "u/own", "label": "S2 File", "caption": "(PDF)", "supp_id": "s005"},
        ])
        hits = fcl.supp_hits("t", "plos", res, {"s005"}, "2026-10-02")
        got = [(x["how_found"], x["file_name"]) for x in hits]
        self.assertIn(("name_codebook", "Codebook (sheet in S1_Data.xlsx)"), got)
        self.assertIn(("name_codebook", "Variables (sheet in S2_Data.xlsx)"), got)
        self.assertIn(("doc_candidate", "S1_File.docx"), got)
        self.assertNotIn(("doc_candidate", "S2_File.pdf"), got)      ##the table's own data file
        self.assertEqual(len(got), 3)
        fcl._TEXTS = None

    def test_caption_naming_a_sibling_table_belongs_to_it(self):
        sib = {"jeon_2019_cbi", "jeon_2019_cesd10"}
        self.assertEqual(fcl.caption_owners("Questionnaire of Korean version of Copenhagen Burnout "
                                            "Inventory(CBI-K). (GIF)", sib), {"jeon_2019_cbi"})
        sib = {"horiuchi_2024_rsmsm", "horiuchi_2024_attachment"}
        self.assertEqual(fcl.caption_owners("The rating scale (RS-MSM) Questionnaire items. (DOCX)", sib),
                         {"horiuchi_2024_rsmsm"})
        ##an acronym that names no table of the article: the file is everyone's
        self.assertEqual(fcl.caption_owners("The Dietarian Identity Questionnaire (DIQ). (PDF)",
                                            {"gumus_2025_dietarian_identity"}), set())

    def test_qualitative_codebooks_and_factor_tables_do_not_count(self):
        self.assertIsNone(fcl.caption_kind("S1 Table", "Interview codebook. (PDF)"))
        self.assertEqual(fcl.caption_kind("S4 Table", "Rotated factor matrix for scale items. (DOCX)"),
                         "data_or_results")
        self.assertEqual(fcl.caption_kind("S1 File", "Survey questions. (PDF)"), "questionnaire")

    def test_names_count_once_whatever_their_case(self):
        self.assertEqual(fcl.names_in_text(["Education", "education", "Place"], "education and place"),
                         ["Education", "Place"])

    def test_full_run_exclusions(self):
        self.assertIsNone(fcl.caption_kind("S5 File", "Dutch guidelines for questionnaire research. (PDF)"))
        self.assertIsNone(fcl.caption_kind("S6 Table", "List of controls and instruments used. (DOCX)"))
        ##the dataset, whatever its labels
        self.assertEqual(fcl.caption_kind("S2 File", "Dataset. Anonymized SPSS dataset with English "
                                          "variable labels. (SAV)"), "data_or_results")
        self.assertEqual(fcl.caption_kind("S1 File", "Empirical dataset and the corresponding codebook. (XLSX)"),
                         "name_codebook")
        self.assertIsNone(fcl.caption_kind("S10 File", "Translation Codebook"))
