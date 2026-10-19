"""`_squashed_key` must not collapse non-Latin item codes (#3077).

`_NON_ALNUM` is `[^0-9A-Za-z]`, so it deletes every CJK, Arabic, Persian,
Cyrillic, Greek, Hebrew and Thai character. Two unrelated Chinese codes both
squashed to the empty string and were reported as renderings of one item;
on a table whose codes are ALL non-Latin, every item grouped into one
finding. Found on `yang_2026_appreciative_education`, whose item codes are
the deposit's own Chinese column names.

The function's docstring promised a `None` return for exactly this case from
the start -- the body never returned it.

unittest, not pytest: CI runs `python -m unittest discover` over every test
directory (.github/workflows/tests.yml) and pytest is not installed there.
"""
import os
import sys
import unittest

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from irw_validate.extra import check_item_variants, _squashed_key  # noqa: E402


def frame(items):
    return pd.DataFrame({"id": range(1, len(items) + 1), "item": items,
                         "resp": [1] * len(items)})


class NonLatinItemCodes(unittest.TestCase):
    CASES = {
        "chinese": ["您对赏识教育了解程度", "赏识教育鼓励下，你的学习成绩进步了"],
        "persian": ["جنسیت شما کدام است؟", "سن خود را مشخص کنید"],
        "greek": ["Ποιο είναι το φύλο σας", "Ηλικία"],
        "cyrillic": ["Какой у вас пол", "Возраст"],
    }

    def test_unrelated_non_latin_codes_are_not_variants(self):
        for name, items in self.CASES.items():
            with self.subTest(script=name):
                self.assertEqual(check_item_variants(frame(items)), [])

    def test_squashed_key_is_none_without_latin_alphanumerics(self):
        self.assertIsNone(_squashed_key("您对赏识教育了解程度"))
        self.assertIsNone(_squashed_key("，。！"))

    def test_squashed_key_still_built_for_mixed_codes(self):
        """A code with any Latin alphanumeric is still judged."""
        self.assertIsNotNone(_squashed_key("B3你认为学校的老师对学生十分的关爱"))

    def test_all_non_latin_table_produces_no_finding(self):
        """The worst case: every code non-Latin, so every one squashed alike."""
        items = ["项目一", "项目二", "项目三", "项目四", "项目五"]
        self.assertEqual(check_item_variants(frame(items)), [])


class TheDefectThisCheckExistsFor(unittest.TestCase):
    """#2052's DART cases must be unaffected by the guard."""

    def test_separator_variant_still_fires(self):
        out = check_item_variants(frame(["Agatha Christie", "Agatha_Christie"]))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].check, "item_variants")

    def test_deleted_punctuation_variant_still_fires(self):
        self.assertEqual(
            len(check_item_variants(frame(["J.K. Rowling", "JK Rowling"]))), 1)

    def test_numbered_codes_still_not_merged(self):
        self.assertEqual(check_item_variants(frame(["item_1_2", "item_12"])), [])


if __name__ == "__main__":
    unittest.main()
