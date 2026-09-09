"""Tests for doi_hygiene.py, the `DOI (for paper)` normaliser (#1690).

THE LINE THAT MATTERS is between normalize() and classify(). Unwrapping
`https://doi.org/10.7910/DVN/ZDNSFJ` leaves a Dataverse deposit DOI, which is
still the wrong object for a column that means "the paper" -- normalisation
must not be mistaken for a fix, and must never rewrite the DOI itself. The
tests below pin both halves of that: the mechanical strip is exhaustive, and a
data DOI comes out of normalize() unchanged and is only ever *reported*.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from doi_hygiene import classify, normalize  # noqa: E402


class NormalizeTest(unittest.TestCase):
    def test_unwraps_resolver_urls(self):
        for raw in ("https://doi.org/10.1136/bmjgh-2019-001724",
                    "http://dx.doi.org/10.1136/bmjgh-2019-001724",
                    "HTTPS://DOI.ORG/10.1136/bmjgh-2019-001724"):
            self.assertEqual(normalize(raw)[0], "10.1136/bmjgh-2019-001724", raw)

    def test_drops_doi_prefixes(self):
        self.assertEqual(normalize("data doi: 10.6084/m9.figshare.26820745.v4")[0],
                         "10.6084/m9.figshare.26820745.v4")
        self.assertEqual(normalize("DOI:10.1371/journal.pone.0146050")[0],
                         "10.1371/journal.pone.0146050")

    def test_drops_supplement_suffix(self):
        ##`.s001` resolves to a supplementary file, not the article.
        self.assertEqual(normalize("10.3389/fpsyg.2022.1014794.s001")[0],
                         "10.3389/fpsyg.2022.1014794")

    def test_composes(self):
        clean, rules = normalize(" data doi: https://doi.org/10.6084/m9.figshare.1.v2 ")
        self.assertEqual(clean, "10.6084/m9.figshare.1.v2")
        self.assertEqual(rules, ["drop-doi-prefix", "unwrap-doi-url"])

    def test_idempotent(self):
        for raw in ("10.1037/a0022874", "10.7910/DVN/ZDNSFJ",
                    "10.17632/826gmw6ypw.1", "10.6084/m9.figshare.26820745.v4"):
            self.assertEqual(normalize(raw), (raw, []), raw)
            self.assertEqual(normalize(normalize(raw)[0])[0], raw)

    def test_leaves_version_and_part_suffixes_alone(self):
        ##Mendeley `.1`, figshare `.v4` and an article DOI ending in digits are
        ##NOT supplement suffixes; only `.s` + exactly three digits is.
        for raw in ("10.17632/826gmw6ypw.1", "10.6084/m9.figshare.26820745.v4",
                    "10.1371/journal.pone.0340806", "10.1787/9789264281820-en"):
            self.assertEqual(normalize(raw)[0], raw, raw)

    def test_never_changes_which_object_a_doi_names(self):
        ##A data DOI survives normalisation untouched: replacing it needs the
        ##linked publication, which is a judgement call, not a strip.
        self.assertEqual(normalize("https://doi.org/10.7910/DVN/ZDNSFJ")[0],
                         "10.7910/DVN/ZDNSFJ")

    def test_blank(self):
        self.assertEqual(normalize(None), ("", []))
        self.assertEqual(normalize("   "), ("", []))


class ClassifyTest(unittest.TestCase):
    def test_labels(self):
        cases = {
            "": "empty",
            "10.1037/a0022874": "article_doi",
            "10.1787/9789264281820-en": "article_doi",
            "10.7910/DVN/ZDNSFJ": "data_doi",
            "10.6084/m9.figshare.26820745.v4": "data_doi",
            "10.17632/826gmw6ypw.1": "data_doi",
            "10.31234/osf.io/abcde": "preprint_doi",
            "10.48550/arXiv.2208.12610": "preprint_doi",
            "not yet published": "free_text",
            "https://osf.io/58xb9/": "free_text",
            "10.7910/DVN/PNGUT5; 10.7910/DVN/7A9YMV": "multiple",
            ##Two DOIs run together with no separator: the cell was written on
            ##two lines and read back through a splitlines() CSV parse. It looks
            ##like one plausible DOI, so it has to be caught by prefix count.
            "10.1016/j.appdev.2017.03.00310.1080/10409289.2025.2578816": "multiple",
        }
        for value, want in cases.items():
            with self.subTest(value=value):
                self.assertEqual(classify(value), want)

    def test_preprints_are_not_a_defect(self):
        ##A preprint IS the paper: it has the authors and the year the column
        ##means. Counting it as a data DOI overstates #1690 by ~75 rows.
        self.assertNotEqual(classify("10.31219/osf.io/xyz12"), "data_doi")


if __name__ == "__main__":
    unittest.main()
