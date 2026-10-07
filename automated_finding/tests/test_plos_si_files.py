"""extract_si_files() pairs each SI item's URL with its own label and format.

The old single regex required a one-word label ("S1 Dataset."). A multi-word
label ("S1 CONSORT Checklist.") made the match run on into the next block, so
pone.0147763 fetched its CONSORT .doc under the name S1_Dataset.sav and never
saw the real .sav. HTML below is the shape of a live PLOS article. No network.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from irw_discover_plos import extract_si_files  # noqa: E402

DOI = "10.1371/journal.pone.0147763"


def _block(n, label, caption, fmt):
    sid = f"pone.0147763.s{n:03d}"
    return (
        f'<div class="supplementary-material"><a name="{sid}" id="{sid}" class="link-target"></a>'
        f'<h3 class="siTitle title-small"><a href="article/file?type=supplementary&amp;id=10.1371/journal.{sid}">'
        f'{label}. </a>{caption}</h3><p class="siDoi"><a href="https://doi.org/10.1371/journal.{sid}">'
        f'https://doi.org/10.1371/journal.{sid}</a></p><p class="postSiDOI">({fmt})</p>\n</div>')


HTML = "<h2>Supporting Information</h2>" + "".join([
    _block(1, "S1 Appendix", "Overviews.", "PDF"),
    _block(2, "S1 CONSORT Checklist", "CONSORT Checklist.", "DOC"),
    _block(3, "S1 Dataset", "Relevant dataset excluding personal information.", "SAV"),
    _block(4, "S1 Protocol", "Trial Protocol.", "PDF"),
    _block(5, "S2 Raw Data", "Item responses, wave 2.", "XLSX"),
])


class SiFiles(unittest.TestCase):
    def test_each_url_keeps_its_own_label_and_format(self):
        got = {name: url.rsplit(".", 1)[-1] for url, name, _ in extract_si_files(HTML, DOI)}
        self.assertEqual(got, {
            "journal.pone.0147763_S1_Dataset.sav": "s003",
            "journal.pone.0147763_S2_Raw_Data.xlsx": "s005",
        })

    def test_caption_is_this_blocks(self):
        caps = {name: cap for _, name, cap in extract_si_files(HTML, DOI)}
        self.assertIn("Relevant dataset", caps["journal.pone.0147763_S1_Dataset.sav"])
        self.assertIn("wave 2", caps["journal.pone.0147763_S2_Raw_Data.xlsx"])


if __name__ == "__main__":
    unittest.main()
