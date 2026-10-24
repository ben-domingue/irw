"""A postal code served as an INTEGER (review R-41, issue irw#3227).

The content tier is string-only by design: digits cannot be told from a
legitimate numeric covariate without a locale, which is right for a raw
candidate. It is not right for a column whose NAME says postal code --
`friedman_2018_risks_*` published a full 5-digit US ZIP as an integer, which
`_holds_full_postal_codes` could not see, and 72.0% of its 3,110 respondents
were unique on that column alone.

So the tier is name-scoped, and these tests pin both halves: it fires on a
5-digit numeric column called `cov_zip`, and it does not fire on the coarsened
`cov_zip3` the 2026-10-19 ruling asks for, nor on an ordinary numeric covariate
holding the same magnitudes.

unittest, not pytest: CI runs `python -m unittest discover` over every test
directory and pytest is not installed there.
"""
import unittest

import pandas as pd

from irw_triage_updated import _holds_numeric_postal_codes, screen_for_pii

N = 200


def frame(**cols):
    base = {"id": range(N), "item": ["q1"] * N, "resp": [1] * N}
    base.update(cols)
    return pd.DataFrame(base)


class TheDetector(unittest.TestCase):
    def test_five_digit_codes(self):
        self.assertTrue(_holds_numeric_postal_codes(
            pd.Series([94305 + i for i in range(N)])))

    def test_three_digit_prefix_is_the_coarsening(self):
        self.assertFalse(_holds_numeric_postal_codes(
            pd.Series([943 + i % 50 for i in range(N)])))

    def test_a_repeated_code_is_a_category(self):
        # A 5-digit school or district id repeated across thousands of rows is
        # not a respondent's location.
        self.assertFalse(_holds_numeric_postal_codes(
            pd.Series([10001, 20002, 30003] * 60)))

    def test_strings_are_the_other_tier(self):
        self.assertFalse(_holds_numeric_postal_codes(
            pd.Series([str(94305 + i) for i in range(N)])))

    def test_too_few_values(self):
        self.assertFalse(_holds_numeric_postal_codes(pd.Series([94305, 94306])))


class TheScreen(unittest.TestCase):
    def test_numeric_zip_is_a_hit_and_counts_as_geographic(self):
        df = frame(cov_zip=[94305 + i for i in range(N)])
        hits = screen_for_pii(df.columns, df)
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("numeric", hits[0])
        # Geographic, so the 2026-10-20 ruling says drop the column and ship
        # the rest rather than skip the candidate.
        self.assertEqual(screen_for_pii.geographic_hits, hits)
        self.assertIn(hits[0], screen_for_pii.value_hits)

    def test_truncated_zip_is_clean(self):
        df = frame(cov_zip3=[943 + i % 50 for i in range(N)])
        self.assertEqual(screen_for_pii(df.columns, df), [])

    def test_ordinary_numeric_covariate_is_clean(self):
        df = frame(cov_income=[45000 + 100 * i for i in range(N)])
        self.assertEqual(screen_for_pii(df.columns, df), [])

    def test_value_hits_separates_the_tiers(self):
        # A name-tier hit is not a value-tier hit: irw_validate blocks on the
        # second and warns on the first.
        df = frame(respondent_name=["x"] * N)
        hits = screen_for_pii(df.columns, df)
        self.assertEqual(len(hits), 1, hits)
        self.assertEqual(screen_for_pii.value_hits, [])


if __name__ == "__main__":
    unittest.main()
