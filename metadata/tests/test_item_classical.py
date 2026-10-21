#!/usr/bin/env python3
"""Tests for 19_item_classical.py (#1710, tier 0).

    python3 -m unittest metadata.tests.test_item_classical -v
    python3 metadata/tests/test_item_classical.py

Nothing here touches Redivis. What is tested is the part that decides what gets
computed and what the columns mean -- the SQL itself is checked by running the
stage, and its one real trap (id is FLOAT64 on part of the corpus, which
BigQuery refuses to PARTITION BY) is pinned below as a string assertion because
it cost 28 of the first 400 tables.
"""

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "item_classical", HERE.parent / "19_item_classical.py")
ic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ic)


def item(mean, r=None, lo=0, hi=1):
    return {"mean": str(mean), "item_rest_r": "" if r is None else str(r),
            "min_resp": str(lo), "max_resp": str(hi)}


class TestSummarise(unittest.TestCase):
    def test_no_rows_leaves_every_column_blank(self):
        """A table the rotation has not reached yet must be blank, not zero."""
        self.assertEqual(ic.summarise([]),
                         {"difficulty_spread": "", "mean_item_rest_r": "",
                          "mean_abs_item_rest_r": "", "prop_items_extreme": ""})

    def test_dichotomous_spread_is_the_p_range(self):
        s = ic.summarise([item(0.2), item(0.5), item(0.9)])
        self.assertEqual(s["difficulty_spread"], "0.7")

    def test_spread_is_normalised_by_the_observed_range(self):
        """The same shape on a 1-5 scale gives the same number, which is the
        whole point: the column has to be comparable across the corpus."""
        s = ic.summarise([item(1.8, lo=1, hi=5), item(3.0, lo=1, hi=5),
                          item(4.6, lo=1, hi=5)])
        self.assertEqual(s["difficulty_spread"], "0.7")

    def test_constant_response_table_is_blank_not_zero(self):
        s = ic.summarise([item(1, lo=1, hi=1), item(1, lo=1, hi=1)])
        self.assertEqual(s["difficulty_spread"], "")
        self.assertEqual(s["prop_items_extreme"], "")

    def test_floor_and_ceiling_counted_from_both_ends(self):
        s = ic.summarise([item(0.01), item(0.5), item(0.99), item(0.6)])
        self.assertEqual(s["prop_items_extreme"], "0.5")

    def test_signed_and_absolute_item_rest_r_differ_on_reverse_keying(self):
        """ffm_AGR in miniature: five positive, five reverse-keyed items average
        to about zero, which reads as a scale whose items are unrelated. The
        absolute column is the one a 'do these hang together' filter wants."""
        rs = [item(0.5, r=0.3) for _ in range(5)] + [item(0.5, r=-0.3) for _ in range(5)]
        s = ic.summarise(rs)
        self.assertEqual(s["mean_item_rest_r"], "0")
        self.assertEqual(s["mean_abs_item_rest_r"], "0.3")

    def test_missing_correlations_are_dropped_not_zeroed(self):
        s = ic.summarise([item(0.5, r=0.4), item(0.5, r=None)])
        self.assertEqual(s["mean_item_rest_r"], "0.4")


class TestPlanBatches(unittest.TestCase):
    @staticmethod
    def t(name, resp=0, items=0):
        return {"table": name, "_n_responses": resp, "_n_items": items}

    def test_table_count_cap(self):
        b = ic.plan_batches([self.t(f"t{i}") for i in range(60)])
        self.assertEqual([len(x) for x in b], [25, 25, 10])

    def test_response_cap_splits_heavy_tables(self):
        big = ic.MAX_RESP_PER_BATCH // 2 + 1
        b = ic.plan_batches([self.t("a", big), self.t("b", big), self.t("c", big)])
        self.assertEqual([len(x) for x in b], [1, 1, 1])

    def test_item_cap_splits_sparse_banks(self):
        b = ic.plan_batches([self.t("neurips", items=ic.MAX_ITEMS_PER_BATCH),
                             self.t("small", items=10)])
        self.assertEqual([[x["table"] for x in bb] for bb in b],
                         [["neurips"], ["small"]])

    def test_one_oversized_table_still_gets_its_own_batch(self):
        """A single table over a cap must be attempted, not dropped."""
        b = ic.plan_batches([self.t("huge", ic.MAX_RESP_PER_BATCH * 10)])
        self.assertEqual([len(x) for x in b], [1])

    def test_rotation_order_is_preserved(self):
        names = [f"t{i}" for i in range(30)]
        b = ic.plan_batches([self.t(n) for n in names])
        self.assertEqual([x["table"] for bb in b for x in bb], names)


class TestFmt(unittest.TestCase):
    def test_never_scientific(self):
        """metadata.csv published enem row counts at two significant digits for
        months because R's write.csv picked whichever form was shorter."""
        self.assertEqual(ic.fmt(44986496.0), "44986496")
        self.assertEqual(ic.fmt(0.0000123), "0.000012")

    def test_blank_for_missing(self):
        self.assertEqual(ic.fmt(None), "")
        self.assertEqual(ic.fmt(float("nan")), "")


class TestSql(unittest.TestCase):
    def test_id_is_cast_to_string(self):
        """`id` is FLOAT64 on part of the corpus and BigQuery refuses to
        PARTITION BY a float -- 28 of the first 400 tables failed on it."""
        sql = ic.agg_sql("datapages", "item_response_warehouse", "ffm_AGR")
        self.assertIn("CAST(id AS STRING) AS id", sql)
        self.assertIn("PARTITION BY id", sql)

    def test_non_numeric_responses_are_dropped_not_fatal(self):
        sql = ic.agg_sql("datapages", "item_response_warehouse", "x")
        self.assertIn("SAFE_CAST(resp AS FLOAT64)", sql)

    def test_single_item_respondents_are_excluded_from_the_correlation_only(self):
        """rest = total - resp is a constant 0 for someone who answered one
        item; CORR drops the NULL pairs while the other statistics keep the row."""
        sql = ic.agg_sql("datapages", "item_response_warehouse", "x")
        self.assertIn("IF(COUNT(*) OVER (PARTITION BY id) > 1", sql)
        self.assertNotIn("WHERE k >", sql)


if __name__ == "__main__":
    unittest.main()
