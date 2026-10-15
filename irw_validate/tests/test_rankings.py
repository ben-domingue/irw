"""Rankings-table checks (irw_validate.rankings, the draft standard's R1-R8)."""
import unittest

import pandas as pd

from irw_validate.rankings import validate_rankings_frame


def table():
    """Three ballots: a full ranking, a ranking with a gap, a duplicate mark + an overvote."""
    rows = [
        {"id": 1, "task": 1, "item": "c01", "resp": 1}, {"id": 1, "task": 1, "item": "c02", "resp": 2},
        {"id": 1, "task": 1, "item": "c03", "resp": 3},
        {"id": 2, "task": 1, "item": "c03", "resp": 1}, {"id": 2, "task": 1, "item": "c01", "resp": 3},
        {"id": 3, "task": 1, "item": "c02", "resp": 1}, {"id": 3, "task": 1, "item": "c02", "resp": 2},
        {"id": 3, "task": 1, "item": "(overvote)", "resp": 3},
    ]
    df = pd.DataFrame(rows)
    df["cov_precinct"] = df["id"].map({1: "A", 2: "A", 3: "B"})
    return df


DESIGN = {"n_positions": "3", "n_candidates": "3", "n_ballots_with_marks": "3"}


def checks(df, severity, design=None):
    r = validate_rankings_frame(df, label="rcv_town_20211102_council.csv", design=design)
    return {f.check for f in r.findings if f.severity == severity}


class RankingsTest(unittest.TestCase):
    def test_valid_table_has_no_errors(self):
        self.assertEqual(checks(table(), "error", DESIGN), set())

    def test_duplicate_marks_are_allowed_and_counted(self):
        r = validate_rankings_frame(table(), label="rcv_town_20211102_council.csv")
        self.assertEqual(r.stats["n_duplicate_marks"], 1)
        self.assertEqual(r.stats["n_ballots_with_gap"], 1)

    def test_repeated_position_is_an_error(self):
        df = table()
        df.loc[1, "resp"] = 1
        self.assertIn("rank_positions", checks(df, "error"))

    def test_personal_name_is_an_error(self):
        df = table()
        df.loc[0, "item"] = "Hale Robison"
        self.assertIn("rank_items", checks(df, "error"))

    def test_unreserved_parenthesis_is_an_error(self):
        df = table()
        df.loc[7, "item"] = "(skipped)"
        self.assertIn("rank_items", checks(df, "error"))

    def test_zero_position_is_an_error(self):
        df = table()
        df.loc[0, "resp"] = 0
        self.assertIn("rank_types", checks(df, "error"))

    def test_undefined_column_is_an_error(self):
        self.assertIn("rank_columns", checks(table().assign(precinct="A"), "error"))

    def test_cov_varying_within_ballot_is_an_error(self):
        df = table()
        df.loc[0, "cov_precinct"] = "Z"
        self.assertIn("rank_columns", checks(df, "error"))

    def test_design_mismatch_is_an_error(self):
        self.assertIn("rank_design", checks(table(), "error", {**DESIGN, "n_positions": "2"}))
        self.assertIn("rank_design", checks(table(), "error", {**DESIGN, "n_candidates": "4"}))

    def test_small_table_warns_on_floor(self):
        self.assertIn("sample_floor", checks(table(), "warn"))


if __name__ == "__main__":
    unittest.main()
