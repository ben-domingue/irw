"""The rankings dictionary's release claim (automated_finding/dictionary_auto_rank.csv).

Rankings has no dictionary sheet: `stage_dict_row.py --source rank` writes that
file and `metadata/02_biblio.R` reads it alone. Nothing rewrites it afterwards,
so a sentence staged before the upload stays in the file forever -- which is how
"Not on Redivis yet." came to sit on 109 live tables, `rcv_alaska_20221108_hd10`
and the whole of `mpls_2017`/`mpls_2021` among them. The release state itself is
recorded in three places that are maintained (the ledger's `status`,
`coverage_matrix.csv` and `rank_metadata.csv`), so the sentence is not the record
of anything; it is a courtesy to a reader of the dictionary, and a false one once
the table ships.

`Notes` is not published for this family -- `rank_biblio` has no Notes column --
so this never reached a table page. It is a repo-hygiene check, not a data defect.

The failure mode worth guarding is the one every cross-file check has: passing
because it compared nothing. A renamed `Notes` column, a dictionary that failed
to parse or an empty liveness list all produce zero hits, and none of those is
good news -- hence `test_both_files_are_whole` and `test_the_sentence_matcher_matches`.

Offline. Add a step for this file to .github/workflows/tests.yml if you move it.

Run: python metadata/tests/test_rank_dictionary.py -v
"""
import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DICT = ROOT / "automated_finding" / "dictionary_auto_rank.csv"
META = ROOT / "metadata" / "rank_metadata.csv"

#: The sentence stage_dict_row.py's callers write while a table is still local.
#: Matched as a substring, because it sits mid-cell ahead of the verification
#: prose in the Minneapolis rows.
CLAIM = "Not on Redivis yet"


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def claims_unreleased(notes):
    return CLAIM in (notes or "")


class RankDictionary(unittest.TestCase):
    def setUp(self):
        self.cols, self.rows = read(DICT)
        _, live = read(META)
        self.live = {r["table"] for r in live}

    def test_both_files_are_whole(self):
        """Neither side may be empty or missing the column the check reads."""
        self.assertIn("Notes", self.cols)
        self.assertIn("table", self.cols)
        self.assertGreater(len(self.rows), 400)
        self.assertGreater(len(self.live), 400)

    def test_the_sentence_matcher_matches(self):
        """So a reworded sentence is a test failure rather than a silent pass."""
        self.assertTrue(claims_unreleased(
            "Script data/rankings/fairvote_cvr.py (source file X.tab). "
            "Design record data/rankings/design_tables.csv. Not on Redivis yet."))
        self.assertFalse(claims_unreleased(
            "Script data/rankings/fairvote_cvr.py (source file X.tab)."))
        self.assertFalse(claims_unreleased(""))
        self.assertFalse(claims_unreleased(None))

    def test_no_live_table_says_it_is_not_on_redivis(self):
        """A table in rank_metadata is live, so the sentence is false of it.

        Clear it in the PR that flips the ledger row to `uploaded` -- that is the
        companion edit this test exists to catch.
        """
        stale = sorted(r["table"] for r in self.rows
                       if r["table"] in self.live and claims_unreleased(r["Notes"]))
        self.assertFalse(stale, f"{len(stale)} live tables still claim "
                                f"'{CLAIM}': {stale[:8]}")


if __name__ == "__main__":
    unittest.main()
