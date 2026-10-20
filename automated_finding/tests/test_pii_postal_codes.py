"""Full postal codes are structural PII; truncated ones are a covariate.

Ruled 2026-10-19 alongside the structural/incidental narrowing of the Step 4
PII rule. The Parkins Energy Literacy deposit (10.7939/DVN/10302) answers
"What is your postal code?" in `q37_0` with 2,917 full six-character Canadian
codes over 3,000 rows, beside age, gender, education and income -- block-level
location, the same re-identification surface as the Qualtrics geo-IP
coordinates ruled out the same day. The whole screen returned clean on that
file: there was no postal-code detector at all.

The check has to read VALUES. The label of a full-code column and of a
properly de-identified forward-sortation-area column are the same question,
so only the values separate them.

unittest, not pytest: CI runs `python -m unittest discover` over every test
directory (.github/workflows/tests.yml) and pytest is not installed there.
"""
import unittest

import pandas as pd

from irw_triage_updated import (screen_for_pii, triage_dataset,
                                _holds_full_postal_codes)


def _col(values, dtype="string"):
    return pd.DataFrame({"q37_0": pd.array(values, dtype=dtype),
                         "q1": [1] * len(values)})


class FullCodesAreFound(unittest.TestCase):
    def test_canadian_six_character_codes(self):
        vals = ["K1A 0B1", "M6C 3W2", "T3K3N4", "S4V 3H5", "L1J 2M2",
                "n1e 7c9", "H2X 1Y4", "V6B 2W9"] * 5
        hits = screen_for_pii(_col(vals).columns, _col(vals))
        self.assertTrue(any("q37_0" in h for h in hits), hits)

    def test_uk_and_zip_plus_four(self):
        self.assertTrue(_holds_full_postal_codes(
            pd.Series(["SW1A 1AA", "EC1A 1BB", "M1 1AE", "B33 8TH"] * 5)))
        self.assertTrue(_holds_full_postal_codes(
            pd.Series(["94305-9991", "02139-4307", "10001-2062",
                       "60601-7501", "98101-1234"] * 3)))

    def test_it_beats_a_good_triage_verdict(self):
        """PII must win over `good`, same as every other identifier."""
        n = 40
        df = pd.DataFrame({
            "q37_0": pd.array(["K1A 0B1", "M6C 3W2", "T3K 3N4", "S4V 3H5",
                               "L1J 2M2"] * (n // 5), dtype="string"),
            **{f"q{i}": [1, 2, 3, 4, 5] * (n // 5) for i in range(1, 11)},
        })
        self.assertEqual(triage_dataset(df).flag, "pii_suspected")


class ThingsThatMustNotFire(unittest.TestCase):
    def test_forward_sortation_area_is_a_covariate(self):
        """Three characters is ~20,000 people; that is de-identified."""
        self.assertFalse(_holds_full_postal_codes(
            pd.Series(["K1A", "M6C", "T3K", "S4V", "L1J", "N1E"] * 4)))

    def test_bare_us_five_digit_zip(self):
        self.assertFalse(_holds_full_postal_codes(
            pd.Series(["94305", "02139", "10001", "60601", "98101"] * 3)))

    def test_four_digit_european_code(self):
        self.assertFalse(_holds_full_postal_codes(
            pd.Series(["1011", "3012", "5041", "8003", "2000"] * 3)))

    def test_likert_responses(self):
        self.assertFalse(_holds_full_postal_codes(
            pd.Series(list("12345") * 8)))

    def test_one_code_typed_into_a_comments_box_is_incidental(self):
        """The thresholds carry the structural/incidental seam."""
        self.assertFalse(_holds_full_postal_codes(
            pd.Series(["no comment"] * 100 + ["K1A 0B1"])))


class TheScreenReportsItsDenominator(unittest.TestCase):
    def test_content_tier_count_is_published(self):
        vals = ["K1A 0B1", "M6C 3W2", "T3K 3N4", "S4V 3H5", "L1J 2M2"] * 5
        df = _col(vals)
        screen_for_pii(df.columns, df)
        self.assertEqual(screen_for_pii.content_cols_screened, 1)

    def test_all_numeric_frame_screens_zero_columns(self):
        df = pd.DataFrame({"q1": [1, 2, 3] * 5, "q2": [4, 5, 6] * 5})
        screen_for_pii(df.columns, df)
        self.assertEqual(screen_for_pii.content_cols_screened, 0)


if __name__ == "__main__":
    unittest.main()
