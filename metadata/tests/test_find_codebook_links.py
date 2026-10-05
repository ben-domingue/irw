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


class DeepRepositoryTest(unittest.TestCase):
    """#2787 follow-up: documents in repository deposits, past their names."""

    def test_analysis_output_is_not_documentation(self):
        ega = ("library(EGAnet); data <- read_excel('x.xlsx') ... Variable pairs with wTO > 0.25 "
               "node_i node_j wto ... loadings ... items_1 items_2 items_3")
        efa = "Table SM2. EFAs of the full Spanish BFI-2. Loadings of BFI1 ... BFI60"
        self.assertTrue(fcl.looks_like_output(ega))
        self.assertTrue(fcl.looks_like_output(efa))

    def test_questionnaires_and_codebooks_pass(self):
        q = ("TABLE I: Full questionnaire ID German Question English Translation F01r Der Besuch einer "
             "Kunstausstellung ... P12_1. Skup zakona ... 1 - Uopste nije vazno 5 - Vrlo vazno")
        cb = "Variable: nfc_xxx_01_x  Label: I get a kick when ...  Values: 1 = Strongly disagree ... 7 = Strongly agree"
        self.assertFalse(fcl.looks_like_output(q))
        self.assertFalse(fcl.looks_like_output(cb))

    def test_text_files_in_deposits_are_not_read(self):
        # a deposit's .txt/.dat is usually the data, whose header names every column
        self.assertNotIn("txt", fcl.REPO_TEXT_EXT)
        self.assertNotIn("csv", fcl.REPO_TEXT_EXT)


class ReviewLinksTest(unittest.TestCase):
    """#2787 step 3: codebook_by_review.csv, found by hand, never by a crawler."""

    def _run(self, rows, live):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "codebook_by_review.csv"
            with open(p, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fcl.REVIEW_FIELDS)
                w.writeheader()
                for r in rows:
                    w.writerow({k: r.get(k, "") for k in fcl.REVIEW_FIELDS})
            old = fcl.REVIEW_CODEBOOKS
            fcl.REVIEW_CODEBOOKS = p
            try:
                return fcl.review_links(live)
            finally:
                fcl.REVIEW_CODEBOOKS = old

    def test_codebook_and_questionnaire_rows(self):
        md = "https://www.cis.es/documents/20117/1555121/MD2913.zip"
        rows = self._run([
            {"table": "spain_2011_immigrant_family", "url": md, "file_name": "codigo2913.pdf (inside MD2913.zip)",
             "doc_type": "codebook", "series": "CIS", "wave": "2913", "evidence": "study 2913", "reviewed_at": "2026-10-04"},
            {"table": "spain_2011_immigrant_family", "url": "https://www.cis.es/documents/20117/1555121/cues2913.pdf.zip",
             "doc_type": "questionnaire", "series": "CIS", "wave": "2913", "reviewed_at": "2026-10-04"},
            {"table": "retired_2011", "url": md, "doc_type": "codebook"},
        ], {"spain_2011_immigrant_family"})
        self.assertEqual([(r["how_found"], r["file_name"], r["host"], r["n_same_kind_in_deposit"]) for r in rows],
                         [("recorded_by_review", "codigo2913.pdf (inside MD2913.zip)", "cis.es", 1),
                          ("questionnaire", "cues2913.pdf.zip", "cis.es", 1)])
        self.assertEqual(rows[0]["evidence"], "study 2913")
        self.assertEqual(rows[0]["checked_at"], "2026-10-04")

    def test_a_bad_row_stops_the_run(self):
        for bad in ({"table": "t", "url": "https://x.org/a.pdf", "doc_type": "guess"},
                    {"table": "t", "url": "", "doc_type": "codebook"}):
            with self.assertRaises(SystemExit):
                self._run([bad], {"t"})


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
