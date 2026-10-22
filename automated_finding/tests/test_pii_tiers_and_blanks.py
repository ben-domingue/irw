"""Two PII-screen defects from the 2026-10-21 repos sweep, both found by hand.

Both of the sweep's two `pii_suspected` rows were false positives, and each
for a different reason:

1. **An empty column.** 10.7910/DVN/F9D6TH, a CC0 replication file of 6,132
   respondents, was closed on `RecipientLastName` and `RecipientFirstName`.
   Every Qualtrics export carries those columns plus `RecipientEmail` whether
   or not the distribution used an email list, and on an anonymous-link study
   all three are empty in every row -- 0 non-blank values of 6,132. The name
   tier matched the NAME and never looked at the values.

2. **The wrong action for the tier.** Since Ben's 2026-10-20 ruling a postal
   or other geographic code means DROP THE COLUMN and ship the rest, while a
   name or an email still skips the whole candidate. The triage reason said
   "whole-candidate skip" for both, which is the sentence a reader acts on --
   it is what closed 10.7910/DVN/QIEEJU (2,862 respondents x 5 waves) and
   10.5061/dryad.6vs80 before the ruling reopened them by hand.

Also pinned here: the Royal Mail letter constraints added to
`_RE_POSTAL_FULL`, after it matched a column of self-generated pseudonymous
participant codes ("J27SE", "M17MN": a letter, a two-digit day of birth and
two initials) in zenodo.22208333. The constraints are real -- the first
position never uses Q, V or X, and J and Z are not area letters; the final two
never use C, I, K, M, O or V -- and they must not cost a real postcode.

Offline, synthetic.
"""
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from irw_triage_updated import (  # noqa: E402
    _RE_POSTAL_FULL, screen_for_pii, triage_dataset)


def _responses(n=200, items=6, seed=0):
    rng = np.random.default_rng(seed)
    return {f"Q{k}": rng.integers(1, 6, n) for k in range(1, items + 1)}


class EmptyQualtricsPlaceholders(unittest.TestCase):
    def frame(self, n=200):
        df = pd.DataFrame(_responses(n))
        df["ResponseId"] = [f"R_{i:05d}" for i in range(n)]
        df["RecipientLastName"] = [""] * n
        df["RecipientFirstName"] = [np.nan] * n
        df["RecipientEmail"] = [""] * n
        return df

    def test_empty_placeholders_are_not_flagged(self):
        df = self.frame()
        self.assertEqual(screen_for_pii(df.columns, df), [])

    def test_the_skip_is_reported_not_silent(self):
        df = self.frame()
        screen_for_pii(df.columns, df)
        self.assertEqual(sorted(screen_for_pii.blank_columns_skipped),
                         ["RecipientEmail", "RecipientFirstName",
                          "RecipientLastName"])

    def test_a_populated_one_is_still_flagged(self):
        df = self.frame()
        df.loc[:, "RecipientLastName"] = ["Nowak"] * len(df)
        self.assertTrue(screen_for_pii(df.columns, df))

    def test_triage_no_longer_closes_the_candidate(self):
        self.assertNotEqual(triage_dataset(self.frame()).flag,
                            "pii_suspected")


class GeographicTierNamesItsOwnAction(unittest.TestCase):
    def frame(self, n=200):
        df = pd.DataFrame(_responses(n))
        # Canadian full postal codes, the shape the detector was built for.
        df["postcode"] = [f"K{i % 10}A {i % 10}B{i % 10}" for i in range(n)]
        return df

    def test_it_is_still_flagged(self):
        df = self.frame()
        hits = screen_for_pii(df.columns, df)
        self.assertTrue(hits)
        self.assertEqual(screen_for_pii.geographic_hits, hits)

    def test_the_reason_says_drop_the_column_not_skip(self):
        reasons = " ".join(triage_dataset(self.frame()).reasons)
        self.assertIn("DROP THE COLUMN", reasons)
        # The phrase appears, but negated -- what must not appear is the
        # directive the name tier gives.
        self.assertIn("NOT a whole-candidate skip", reasons)
        self.assertNotIn("this is a whole-candidate skip", reasons)

    def test_a_name_still_says_whole_candidate_skip(self):
        df = self.frame()
        df["Respondent's Name"] = ["Dorothy Cassidy"] * len(df)
        reasons = " ".join(triage_dataset(df).reasons)
        self.assertIn("whole-candidate skip", reasons)

    def test_a_name_beside_a_postcode_is_not_downgraded(self):
        df = self.frame()
        df["participant name"] = ["Dorothy Cassidy"] * len(df)
        reasons = " ".join(triage_dataset(df).reasons)
        self.assertIn("whole-candidate skip", reasons)
        self.assertNotIn("DROP THE COLUMN", reasons)


class RoyalMailLetterConstraints(unittest.TestCase):
    REAL = ["SW1A 1AA", "M1 1AE", "B33 8TH", "CR2 6XH", "DN55 1PT",
            "EC1A 1BB", "W1A 0AX", "K1A 0B1", "K1A0B1", "12345-6789"]
    # Self-generated participant codes the old pattern accepted.
    CODES = ["J27SE", "M17MN", "O15OS", "A10JM", "S10ME", "J13OV"]

    def test_real_codes_still_match(self):
        for s in self.REAL:
            self.assertTrue(_RE_POSTAL_FULL.match(s), s)

    def test_the_impossible_letters_no_longer_match(self):
        for s in self.CODES:
            self.assertFalse(_RE_POSTAL_FULL.match(s), s)

    def test_a_column_of_participant_codes_is_not_flagged(self):
        # 130 codes, every one of them using a letter the real format forbids.
        df = pd.DataFrame(_responses(130))
        df["Code"] = [f"J{i % 28 + 1:02d}S{chr(65 + i % 26)}"
                      for i in range(130)]
        self.assertEqual(screen_for_pii(df.columns, df), [])


if __name__ == "__main__":
    unittest.main()
