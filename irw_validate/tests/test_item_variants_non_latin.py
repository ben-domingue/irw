"""`_squashed_key` must not collapse non-Latin item codes (#3077).

`_NON_ALNUM` is `[^0-9A-Za-z]`, so it deletes every CJK, Arabic, Persian,
Cyrillic, Greek, Hebrew and Thai character. Two unrelated Chinese codes both
squashed to the empty string and were reported as renderings of one item;
on a table whose codes are ALL non-Latin, every item grouped into one
finding. Found on `yang_2026_appreciative_education`, whose item codes are
the deposit's own Chinese column names.

The function's docstring promised a `None` return for exactly this case from
the start -- the body never returned it.
"""
import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from irw_validate.extra import check_item_variants, _squashed_key  # noqa: E402


def frame(items):
    return pd.DataFrame({"id": range(1, len(items) + 1), "item": items,
                         "resp": [1] * len(items)})


NON_LATIN = [
    pytest.param(["您对赏识教育了解程度", "赏识教育鼓励下，你的学习成绩进步了"],
                 id="chinese"),
    pytest.param(["جنسیت شما کدام است؟", "سن خود را مشخص کنید"], id="persian"),
    pytest.param(["Ποιο είναι το φύλο σας", "Ηλικία"], id="greek"),
    pytest.param(["Какой у вас пол", "Возраст"], id="cyrillic"),
]


@pytest.mark.parametrize("items", NON_LATIN)
def test_unrelated_non_latin_codes_are_not_variants(items):
    assert check_item_variants(frame(items)) == []


def test_squashed_key_is_none_without_latin_alphanumerics():
    assert _squashed_key("您对赏识教育了解程度") is None
    assert _squashed_key("，。！") is None


def test_squashed_key_still_built_for_mixed_codes():
    """A code with any Latin alphanumeric is still judged."""
    assert _squashed_key("B3你认为学校的老师对学生十分的关爱") is not None


def test_all_non_latin_table_produces_no_finding():
    """The worst case: every code non-Latin, so every one squashed alike."""
    items = ["项目一", "项目二", "项目三", "项目四", "项目五"]
    assert check_item_variants(frame(items)) == []


def test_the_defect_this_check_exists_for_still_fires():
    """#2052's DART case must be unaffected by the guard."""
    out = check_item_variants(frame(["Agatha Christie", "Agatha_Christie"]))
    assert len(out) == 1 and out[0].check == "item_variants"
    out = check_item_variants(frame(["J.K. Rowling", "JK Rowling"]))
    assert len(out) == 1


def test_numbered_codes_still_not_merged():
    assert check_item_variants(frame(["item_1_2", "item_12"])) == []
