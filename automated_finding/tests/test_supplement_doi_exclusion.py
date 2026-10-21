"""A journal supplementary-file DOI must not re-surface a paper already in IRW.

Frontiers and PLOS mint one DOI per attached file by appending `.s001`,
`.s002`, ... to the article's own DOI, and figshare/DataCite index those as
records in their own right. The exclusion sets hold whatever form the
dictionary recorded -- usually the bare article DOI -- so a verbatim
comparison misses the deposit entirely.

That is not hypothetical: the 2026-10-21 repos sweep surfaced
`10.3389/fpsyt.2022.827519.s001` as a `good` candidate while
`10.3389/fpsyt.2022.827519` was already live as six `wang2022_*` tables. It
was caught by a hand grep before a processing script was written; the SKILL's
own `10.7717/peerj.16295` incident is what the same shape costs when nobody
catches it.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from doi_hygiene import strip_supplement_suffix  # noqa: E402
from irw_discover_updated import (  # noqa: E402
    _with_supplement_bases, is_excluded,
)

ARTICLE = "10.3389/fpsyt.2022.827519"
SUPPLEMENT = ARTICLE + ".s001"


class SupplementSuffixTest(unittest.TestCase):
    def test_strip_is_the_shared_rule(self):
        self.assertEqual(strip_supplement_suffix(SUPPLEMENT), ARTICLE)
        # A version suffix is not a supplement suffix.
        for raw in ("10.17632/826gmw6ypw.1",
                    "10.6084/m9.figshare.26820745.v4",
                    "10.1371/journal.pone.0340806"):
            self.assertEqual(strip_supplement_suffix(raw), raw, raw)


class IsExcludedTest(unittest.TestCase):
    def test_the_bug_the_dictionary_has_the_article_doi(self):
        self.assertEqual(is_excluded(SUPPLEMENT, {ARTICLE}), "supplement")

    def test_an_exact_match_still_reports_exact(self):
        self.assertEqual(is_excluded(ARTICLE, {ARTICLE}), "exact")

    def test_resolver_url_and_case_are_normalised(self):
        self.assertEqual(
            is_excluded("https://doi.org/10.3389/FPSYT.2022.827519.s001",
                        {ARTICLE}), "supplement")

    def test_a_different_paper_is_not_excluded(self):
        self.assertEqual(is_excluded("10.3389/fpsyt.2022.999999.s001",
                                     {ARTICLE}), "")

    def test_a_version_suffix_is_not_stripped_into_a_false_match(self):
        # Stripping `.1` would make every version of one Mendeley deposit
        # match a neighbouring deposit's DOI; it must not happen.
        self.assertEqual(is_excluded("10.17632/826gmw6ypw.1",
                                     {"10.17632/826gmw6ypw"}), "")

    def test_blank_doi_is_never_excluded(self):
        self.assertEqual(is_excluded("", {ARTICLE}), "")
        self.assertEqual(is_excluded(None, {ARTICLE}), "")


class WithSupplementBasesTest(unittest.TestCase):
    def test_the_other_direction_dictionary_has_the_si_doi(self):
        # Some dictionary rows record the SI DOI in `DOI (for paper)`. The
        # article DOI must then be excluded too -- same paper.
        ex = _with_supplement_bases({SUPPLEMENT})
        self.assertIn(ARTICLE, ex)
        self.assertEqual(is_excluded(ARTICLE, ex), "exact")

    def test_leaves_a_set_without_supplement_dois_unchanged(self):
        plain = {"10.5281/zenodo.8057093", "10.17632/mp49tfzx4w"}
        self.assertEqual(_with_supplement_bases(plain), plain)


if __name__ == "__main__":
    unittest.main()
