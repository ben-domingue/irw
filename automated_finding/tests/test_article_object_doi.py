"""An article's own table/figure DOI is never a deposit, and .sNNN still is.

Eleven `.tNNN` hits reached `worth_retrying` in the 2026-10-28 leads re-triage,
every one a published results table. The filter that drops them must not touch
`.sNNN`, which is a supplementary FILE and is frequently the dataset itself.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doi_hygiene import is_article_object, strip_supplement_suffix  # noqa: E402

TABLES = [
    "10.1371/journal.pone.0331247.t006",
    "10.1371/journal.pone.0289454.t001",
    "10.1371/journal.pgph.0002978.t004",
    "10.1371/journal.pone.0010457.t002",
    "10.3389/fpsyg.2019.02591.g001",
]
NOT_TABLES = [
    "10.3389/fpsyg.2022.845355.s001",   # a real 1,297-respondent dataset
    "10.1371/journal.pone.0211929",
    "10.17632/yxpj8h384j.1",            # a Mendeley version, not an object
    "10.6084/m9.figshare.23964495.v1",  # a figshare version
    "10.5281/zenodo.17520820",
    "10.7910/DVN/HUYYQZ",
    "",
    None,
]


class TestArticleObjectDoi(unittest.TestCase):
    def test_tables_and_figures_are_article_objects(self):
        for doi in TABLES:
            self.assertTrue(is_article_object(doi), doi)

    def test_supplements_versions_and_deposits_are_not(self):
        for doi in NOT_TABLES:
            self.assertFalse(is_article_object(doi), doi)

    def test_supplement_stripping_is_untouched(self):
        # The two rules are siblings and must not interfere.
        self.assertEqual(
            strip_supplement_suffix("10.3389/fpsyt.2022.827519.s001"),
            "10.3389/fpsyt.2022.827519")
        self.assertEqual(
            strip_supplement_suffix("10.1371/journal.pone.0331247.t006"),
            "10.1371/journal.pone.0331247.t006")

    def test_discovery_imports_and_uses_it(self):
        import irw_discover_updated as d
        self.assertIs(d.is_article_object, is_article_object)


if __name__ == "__main__":
    unittest.main()
