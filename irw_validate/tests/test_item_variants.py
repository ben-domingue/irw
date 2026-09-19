"""`check_item_variants` -- two codes that are renderings of one item (#2052).

The false-positive guards are the point of this file. The check exists to catch
a workbook that spells one author two ways, and the way it could go wrong is
merging two items a table numbers apart ("item_1_2" and "item_12"), which would
be a far worse defect than the one it fixes.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from irw_validate.extra import check_item_variants  # noqa: E402


def _flag(items) -> bool:
    df = pd.DataFrame({"id": range(len(items)), "item": list(items),
                       "resp": [1] * len(items)})
    return bool(check_item_variants(df, "t"))


class ItemVariants(unittest.TestCase):

    def test_flags_separator_style(self):
        # The DART case: same name, space vs underscore.
        self.assertTrue(_flag(["Agatha Christie", "Agatha_Christie"]))

    def test_flags_case_only(self):
        self.assertTrue(_flag(["Q1", "q1"]))

    def test_flags_deleted_separator(self):
        # Study 5 does not swap the period for a space, it deletes it.
        self.assertTrue(_flag(["J.K. Rowling", "JK Rowling"]))

    def test_flags_collapsed_double_space(self):
        self.assertTrue(_flag(["Jorge  Remache", "Jorge Remache"]))

    def test_keeps_numbered_items_apart(self):
        # The guard that matters: these are two items, not one rendering.
        self.assertFalse(_flag(["item_1_2", "item_12"]))

    def test_keeps_regrouped_digits_apart(self):
        self.assertFalse(_flag(["a1b2", "a12b"]))

    def test_keeps_near_miss_names_apart(self):
        # The DART's foils are deliberate near-misses of real authors; merging
        # them would invert an item. "Susan Smith" is a typo for "Susan Smit"
        # per the paper, but that is a ruling, not something a key may assume.
        self.assertFalse(_flag(["Susan Smit", "Susan Smith"]))

    def test_clean_table_is_silent(self):
        self.assertFalse(_flag(["sbq1", "sbq2", "sbq3", "sbq4"]))

    def test_no_item_column(self):
        self.assertEqual(check_item_variants(pd.DataFrame({"id": [1]}), "t"), [])

    def test_empty_frame(self):
        self.assertEqual(
            check_item_variants(pd.DataFrame({"id": [], "item": []}), "t"), [])

    def test_counts_are_reported(self):
        items = ["A B", "A_B", "C D", "C_D", "E"]
        df = pd.DataFrame({"id": range(5), "item": items, "resp": [1] * 5})
        msg = check_item_variants(df, "t")[0].message
        self.assertIn("2 item(s)", msg)
        self.assertIn("5 codes describe 3 items", msg)


if __name__ == "__main__":
    unittest.main()
