"""Cov-table checks (irw_validate.cov, the draft standard's V1-V8)."""
import unittest

import pandas as pd

import tempfile
from pathlib import Path

from irw_validate.cov import validate_cov_file, validate_cov_frame

LABEL = "smith_1990_abilities.csv"


def table(r12=0.5, r13=0.3, r23=0.4, n=200, stat="cor"):
    rows = [("a", "a", 1.0), ("b", "a", r12), ("b", "b", 1.0),
            ("c", "a", r13), ("c", "b", r23), ("c", "c", 1.0)]
    df = pd.DataFrame([{"stat": stat, "var1": a, "var2": b, "value": v, "n": n} for a, b, v in rows])
    sd = pd.DataFrame([{"stat": "sd", "var1": v, "var2": None, "value": s, "n": n}
                       for v, s in zip("abc", (1.5, 2.0, 0.8))])
    return pd.concat([df, sd], ignore_index=True)


def checks(df, severity):
    r = validate_cov_frame(df, label=LABEL)
    return {f.check for f in r.findings if f.severity == severity}


class CovTest(unittest.TestCase):
    def test_valid_table_has_no_findings(self):
        r = validate_cov_frame(table(), label=LABEL)
        self.assertEqual(r.findings, [])
        self.assertEqual(r.stats["n_vars"], {"": 3})
        self.assertTrue(r.stats["has_sd"][""])

    def test_moment_rows_survive_a_csv_round_trip(self):
        ## Read from CSV under pandas 3 a blank var2 is string-dtype NaN, which was
        ## stringified to "nan" and failed V3 on every sd/mean row.
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / LABEL
            table().to_csv(path, index=False)
            r = validate_cov_file(path)
        self.assertEqual([f.check for f in r.findings if f.severity == "error"], [])

    def test_blank_group_is_refused(self):
        ## groupby dropped blank-group rows, so a table whose groups were all
        ## blank passed without a single matrix being checked.
        df = table().assign(group="g1")
        df.loc[df.index[:3], "group"] = None
        self.assertIn("cov_group", checks(df, "error"))

    def test_non_pd_is_a_warning_not_an_error(self):
        df = table(r12=0.9, r13=0.9, r23=-0.9)
        self.assertEqual(checks(df, "error"), set())
        self.assertIn("cov_pd", checks(df, "warn"))

    def test_duplicate_cell_either_orientation(self):
        df = pd.concat([table(), pd.DataFrame([{"stat": "cor", "var1": "a", "var2": "b", "value": 0.5, "n": 200}])])
        self.assertIn("cov_cells", checks(df, "error"))

    def test_missing_cell(self):
        df = table()
        df = df[~((df.var1 == "c") & (df.var2 == "b"))]
        self.assertIn("cov_cells", checks(df, "error"))

    def test_blank_cell_is_info_and_pd_uses_the_complete_part(self):
        ## Ben, 2026-11-18: a cell the source did not report is a row with an
        ## empty value. It passes, is reported, and V8 is judged on the
        ## complete part.
        df = table()
        df.loc[(df.var1 == "c") & (df.var2 == "b"), "value"] = float("nan")
        r = validate_cov_frame(df, label=LABEL)
        self.assertEqual(r.errors, [])
        self.assertIn("cov_cells", {f.check for f in r.findings if f.severity == "info"})
        self.assertEqual(r.stats["n_missing_cells"], {"": 1})
        self.assertGreater(r.stats["min_eigenvalue"][""], 0)

    def test_blank_diagonal_or_moment_is_still_refused(self):
        df = table()
        df.loc[0, "value"] = float("nan")
        self.assertIn("cov_required_columns", checks(df, "error"))
        df = table()
        df.loc[df.stat == "sd", "value"] = float("nan")
        self.assertIn("cov_required_columns", checks(df, "error"))

    def test_parse_variables(self):
        from irw_validate.cov import parse_variables
        self.assertEqual(parse_variables(""), [])
        self.assertEqual(parse_variables(None), [])
        self.assertEqual(parse_variables("x1 = father's education | x2"),
                         [("x1", "father's education"), ("x2", "")])

    def test_complete_drop_is_smallest_and_keeps_earlier_variables(self):
        from irw_validate.cov import complete_drop
        order = list("abcde")
        self.assertEqual(complete_drop(order, [frozenset("ab")]), ["b"])
        # c touches both blanks, so dropping c alone beats dropping a and e
        self.assertEqual(complete_drop(order, [frozenset("ac"), frozenset("ce")]), ["c"])
        self.assertEqual(complete_drop(order, [frozenset("ab"), frozenset("de")]), ["b", "e"])
        self.assertEqual(complete_drop(order, []), [])

    def test_cor_out_of_range_and_bad_diagonal(self):
        self.assertIn("cov_values", checks(table(r12=1.2), "error"))
        df = table()
        df.loc[0, "value"] = 0.9
        self.assertIn("cov_values", checks(df, "error"))

    def test_rounding_tolerated(self):
        df = table()
        df.loc[0, "value"] = 0.9996
        self.assertEqual(checks(df, "error"), set())

    def test_cov_implying_r_above_one(self):
        df = table(stat="cov")
        df.loc[df.var1.eq("a") & df.var2.eq("a"), "value"] = 1.0
        df.loc[df.var1.eq("b") & df.var2.eq("b"), "value"] = 1.0
        df.loc[df.var1.eq("b") & df.var2.eq("a"), "value"] = 1.5
        self.assertIn("cov_values", checks(df, "error"))

    def test_n_must_be_positive_integer(self):
        df = table().astype({"n": float})
        df.loc[1, "n"] = 10.5
        self.assertIn("cov_n", checks(df, "error"))

    def test_stat_vocabulary_and_columns(self):
        df = table()
        df.loc[0, "stat"] = "polychoric"
        self.assertIn("cov_stat", checks(df, "error"))
        self.assertIn("cov_columns", checks(table().assign(note="x"), "error"))

    def test_moment_for_unknown_variable(self):
        df = pd.concat([table(), pd.DataFrame([{"stat": "mean", "var1": "z", "var2": None, "value": 3, "n": 200}])])
        self.assertIn("cov_moments", checks(df, "error"))

    def test_groups_checked_separately(self):
        g1, g2 = table().assign(group="boys"), table(r12=0.6, n=150).assign(group="girls")
        r = validate_cov_frame(pd.concat([g1, g2]), label=LABEL)
        self.assertEqual([f for f in r.findings if f.severity == "error"], [])
        self.assertEqual(r.stats["n_obs"], {"boys": 200, "girls": 150})
        bad = pd.concat([g1, g2[~((g2.var1 == "c") & (g2.var2 == "a"))]])
        self.assertIn("cov_cells", checks(bad, "error"))

    def test_mixed_cor_and_cov_in_one_group(self):
        df = table()
        df.loc[1, "stat"] = "cov"
        self.assertIn("cov_stat", checks(df, "error"))


if __name__ == "__main__":
    unittest.main()
