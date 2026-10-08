"""Conjoint-table checks (irw_validate.conjoint, the draft standard's J1-J7)."""
import unittest

import pandas as pd

from irw_validate.conjoint import validate_conjoint_frame


def table(**over):
    """Two respondents x 2 tasks x 2 profiles, valid: forced choice + rating."""
    rows = []
    for i in (1, 2):
        for t in (1, 2):
            for p in (1, 2):
                rows.append({"id": i, "task": t, "profile": p, "choice": int(p == 1), "rating": 3 + p,
                             "attr_party": ["Democrat", "Republican"][p - 1],
                             "attr_age": ["45", "60"][(p + t) % 2], "cov_age": 30 + i})
    df = pd.DataFrame(rows)
    for k, v in over.items():
        df[k] = v
    return df


def checks(df, severity):
    r = validate_conjoint_frame(df, label="smith_2024_candidates.csv")
    return {f.check for f in r.findings if f.severity == severity}


class ConjointTest(unittest.TestCase):
    def test_valid_table_has_no_errors(self):
        self.assertEqual(checks(table(), "error"), set())

    def test_missing_profile_is_an_error(self):
        self.assertIn("conj_required_columns", checks(table().drop(columns="profile"), "error"))

    def test_duplicate_rows_are_an_error(self):
        df = table()
        self.assertIn("conj_duplicates", checks(pd.concat([df, df.head(1)]), "error"))

    def test_two_chosen_profiles_in_a_task_is_an_error(self):
        self.assertIn("conj_choice", checks(table(choice=1), "error"))

    def test_an_opt_out_task_is_a_warning(self):
        df = table()
        df.loc[(df.id == 1) & (df.task == 1), "choice"] = 0
        self.assertIn("conj_choice", checks(df, "warn"))
        self.assertNotIn("conj_choice", checks(df, "error"))

    def test_named_extra_outcomes_are_allowed(self):
        df = table()
        df["choice_effective"] = df["choice"]
        df["rating_trust"] = df["rating"]
        self.assertEqual(checks(df, "error"), set())

    def test_no_outcome_is_an_error(self):
        self.assertIn("conj_outcomes", checks(table().drop(columns=["choice", "rating"]), "error"))

    def test_an_undefined_column_is_an_error(self):
        self.assertIn("conj_columns", checks(table(age=40), "error"))

    def test_numeric_attribute_codes_warn(self):
        df = table()
        df["attr_party"] = [1, 2] * (len(df) // 2)
        self.assertIn("conj_attributes", checks(df, "warn"))

    def test_not_shown_text_is_valid(self):
        df = table()
        df.loc[df.profile == 2, "attr_age"] = "(not shown)"
        self.assertEqual(checks(df, "error"), set())
        self.assertNotIn("conj_attributes", checks(df, "warn"))

    def test_a_blank_attribute_cell_is_an_error(self):
        df = table()
        df.loc[0, "attr_age"] = None
        self.assertIn("conj_attributes", checks(df, "error"))

    def test_a_displayed_none_level_is_not_blank(self):
        import tempfile, os
        from irw_validate.conjoint import validate_conjoint_file
        df = table()
        df["attr_age"] = ["None", "45"] * (len(df) // 2)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "smith_2024_candidates.csv")
            df.to_csv(p, index=False)
            r = validate_conjoint_file(p)
        self.assertEqual({f.check for f in r.findings if f.severity == "error"}, set())

    def test_a_not_shown_variant_warns(self):
        df = table()
        df.loc[df.profile == 2, "attr_age"] = "Not shown"
        self.assertIn("conj_attributes", checks(df, "warn"))

    def test_identifier_column_names_warn(self):
        self.assertIn("conj_pii_hint", checks(table(cov_ip_address="1.2.3.4"), "warn"))

    def test_small_sample_warns(self):
        self.assertIn("sample_floor", checks(table(), "warn"))


if __name__ == "__main__":
    unittest.main()
