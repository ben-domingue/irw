"""The figshare fallthrough guard must accept a versioned portal URL.

`_figshare_files` gained a trailing-version group on 2026-09-16. The guard in
`_resolve_data_files_any_order` that decides whether to CALL it did not, so
every institutional figshare portal -- which serves
/articles/dataset/<title>/<id>/<version> -- failed the guard and the row came
back "no resolvable tabular file on landing page". The one URL the 2026-10-18b
fallthrough was tested against carries no version segment, which is why the
gap survived its own test; these cases pin both shapes.

unittest, not pytest: CI runs `python -m unittest discover` over every test
directory (.github/workflows/tests.yml) and pytest is not installed there.
"""
import inspect
import re
import unittest

import irw_batch_updated as b

VERSIONED = [
    "https://figshare.manchester.ac.uk/articles/dataset/Questionnaire_Data_-_Religion_Theology_and_Climate_Change/30234109/1",
    "https://orda.shef.ac.uk/articles/dataset/Datasets_for_exploring_the_link/33121544/1",
    "https://drum.um.edu.mt/articles/dataset/_b_Wellbeing_lifestyle_b_/30920516/1",
    "https://figshare.com/articles/survey3a/7357034/1",
]
UNVERSIONED = [
    "https://repository.uj.ac.za/articles/dataset/foo/33093377",
    "https://figshare.com/articles/dataset/bar/12345678",
]

# The guard as it appears in _resolve_data_files_any_order's last resort.
GUARD = re.compile(r"articles/(?:[^/?#]+/)*?\d{4,}(?:/\d+)?/?(?:[?#]|$)")
EXTRACT = re.compile(r"articles/(?:[^/?#]+/)*?(\d{4,})(?:/(\d+))?/?(?:[?#]|$)")


class GuardAcceptsPortalUrls(unittest.TestCase):
    def test_guard_accepts_portal_article_urls(self):
        for url in VERSIONED + UNVERSIONED:
            with self.subTest(url=url):
                self.assertTrue(GUARD.search(url), url)

    def test_guard_and_extractor_agree(self):
        """Whatever the guard admits, the extractor must find an id in."""
        for url in VERSIONED + UNVERSIONED:
            with self.subTest(url=url):
                self.assertTrue(GUARD.search(url))
                m = EXTRACT.search(url)
                self.assertIsNotNone(m, url)
                self.assertGreaterEqual(len(m.group(1)), 4, url)

    def test_extractor_reads_the_id_not_the_version(self):
        m = EXTRACT.search("https://figshare.manchester.ac.uk/articles/"
                           "dataset/x/30234109/1")
        self.assertEqual(m.group(1), "30234109")
        self.assertEqual(m.group(2), "1")

    def test_non_article_url_is_not_admitted(self):
        self.assertIsNone(
            GUARD.search("https://example.org/datasets/collection/overview"))


class GuardAndExtractorStayIdentical(unittest.TestCase):
    """Their drifting apart IS the bug this file exists for."""

    def test_guard_in_source_matches_the_pattern_under_test(self):
        src = inspect.getsource(b._resolve_data_files_any_order)
        self.assertIn(r"articles/(?:[^/?#]+/)*?\d{4,}(?:/\d+)?/?(?:[?#]|$)",
                      src)


if __name__ == "__main__":
    unittest.main()
