"""A deposit recorded under its paper's DOI must not re-surface in discovery (#3573).

The dictionary often holds the PAPER DOI plus a repository landing page, not
the deposit's own DOI: mellat_2022_* carries 10.1080/19349637.2022.2121239 and
data.mendeley.com/datasets/nr9388gbzf; sanchezgarcia_2025_* carries
10.1371/journal.pone.0346573 and zenodo.org/records/14870714. Discovery finds
the deposit by its own DOI, so unless the exclusion turns those URLs (and the
build scripts' download URLs) back into deposit DOIs, the deposit comes back as
a fresh candidate. In the 2026-11-06 claude-assist eval 35 such deposits sat in
human_review/ although a data/ script had already built them.
"""
import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from irw_discover_updated import (  # noqa: E402
    _extract_doi_from_url, _load_biblio_exclusions,
    _load_build_script_exclusions, _with_supplement_bases, is_excluded,
)


class UrlToDepositDoiTest(unittest.TestCase):
    def test_repository_url_forms(self):
        cases = {
            # Mendeley landing page, versioned page, and the script download forms
            "https://data.mendeley.com/datasets/nr9388gbzf": "10.17632/nr9388gbzf",
            "https://data.mendeley.com/datasets/58my34fsg3/1": "10.17632/58my34fsg3",
            "https://data.mendeley.com/public-files/datasets/nr9388gbzf/files/x":
                "10.17632/nr9388gbzf",
            "https://data.mendeley.com/public-api/datasets/csgs546vxy":
                "10.17632/csgs546vxy",
            # Zenodo: current /records/, old /record/, API
            "https://zenodo.org/records/14870714": "10.5281/zenodo.14870714",
            "https://zenodo.org/record/14870714": "10.5281/zenodo.14870714",
            "https://zenodo.org/api/records/4536002/files/": "10.5281/zenodo.4536002",
            # OSF sub-pages and API
            "https://osf.io/2hcw3/files/osfstorage": "10.17605/osf.io/2hcw3",
            "https://osf.io/37ycj/overview": "10.17605/osf.io/37ycj",
            "https://osf.io/2xbe5/?view_only=": "10.17605/osf.io/2xbe5",
            "https://osf.io/abcde": "10.17605/osf.io/abcde",
            "https://api.osf.io/v2/nodes/abcde/files/": "10.17605/osf.io/abcde",
            # A DOI anywhere in the URL
            "https://datadryad.org/stash/dataset/doi:10.5061/dryad.kh189326b":
                "10.5061/dryad.kh189326b",
            "https://journals.plos.org/plosone/article/file?id=10.1371/"
            "journal.pone.0289553.s001&type=supplementary":
                "10.1371/journal.pone.0289553.s001",
        }
        for url, want in cases.items():
            self.assertEqual(_extract_doi_from_url(url), want, url)

    def test_non_repository_urls(self):
        for url in ("", "http://openpsychometrics.org/_rawdata/",
                    "https://cran.r-project.org/package=psych"):
            self.assertIsNone(_extract_doi_from_url(url), url)


class VersionedDepositTest(unittest.TestCase):
    def test_versioned_candidate_matches_bare_exclusion(self):
        self.assertEqual(is_excluded("10.17632/nr9388gbzf.2",
                                     {"10.17632/nr9388gbzf"}), "exact")
        self.assertEqual(is_excluded("10.6084/m9.figshare.31078552.v1",
                                     {"10.6084/m9.figshare.31078552"}), "exact")

    def test_bare_candidate_matches_versioned_exclusion(self):
        ex = _with_supplement_bases({"10.17632/csgs546vxy.2"})
        self.assertEqual(is_excluded("10.17632/csgs546vxy", ex), "exact")

    def test_ordinary_dotted_doi_untouched(self):
        # canonical_doi only strips repository version suffixes
        self.assertEqual(is_excluded("10.1371/journal.pone.0235154",
                                     {"10.1371/journal.pone"}), "")


class SourceLoadersTest(unittest.TestCase):
    def test_biblio_reads_paper_data_and_url(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "biblio.csv")
            with open(p, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["table", "DOI__for_paper_", "DOI__for_data_",
                            "URL__for_data_"])
                w.writerow(["mellat_2022_x", "10.1080/19349637.2022.2121239", "NA",
                            "https://data.mendeley.com/datasets/nr9388gbzf"])
                w.writerow(["andreu_sanchez_2023_x", "NA", "10.5281/zenodo.8057093",
                            "https://zenodo.org/records/8057093"])
            got = _load_biblio_exclusions(p)
        self.assertEqual(got, {"10.1080/19349637.2022.2121239",
                               "10.17632/nr9388gbzf", "10.5281/zenodo.8057093"})

    def test_build_scripts_cite_the_deposit(self):
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "conjoint"))
            Path(td, "sanchezgarcia_2025_x.py").write_text(
                '# DOI: 10.1371/journal.pone.0346573\n'
                'URL = ("https://zenodo.org/api/records/14870714/files/"\n'
                '       "data.xlsx/content")\n')
            Path(td, "conjoint", "treger_2026.R").write_text(
                '# https://doi.org/10.7910/DVN/AEZ83R\n')
            got = _load_build_script_exclusions(td)
        self.assertIn("10.1371/journal.pone.0346573", got)
        self.assertIn("10.5281/zenodo.14870714", got)
        self.assertIn("10.7910/dvn/aez83r", got)
        self.assertEqual(is_excluded("10.5281/zenodo.14870714",
                                     _with_supplement_bases(got)), "exact")


if __name__ == "__main__":
    unittest.main()
