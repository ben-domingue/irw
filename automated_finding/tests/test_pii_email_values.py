"""The PII screen must read values, not only column labels.

10.5281/zenodo.10069489 carried 3,130 real email addresses in a column named
`Nombredeusuario` -- "nombre de usuario" with the spaces stripped. The label
patterns could not fire (no word boundary around "nombre", and the bare-name
pattern wants the label to be exactly "nombre"), and a `dtype == object` guard
skipped the column without reading a value because `pyreadstat` returns
pandas `StringDtype`. The deposit was the richest in its batch and was caught
only by hand.
"""
import pandas as pd
import pytest

from irw_triage_updated import screen_for_pii


def test_emails_found_in_stringdtype_column_with_an_unanticipated_label():
    df = pd.DataFrame({
        "Nombredeusuario": pd.array([f"person{i}@gmail.com" for i in range(40)],
                                    dtype="string"),
        "ryff1": list(range(1, 41)),
    })
    hits = screen_for_pii(df.columns, df)
    assert any("Nombredeusuario" in h for h in hits)


def test_emails_found_in_object_column():
    df = pd.DataFrame({"usuario": [f"a{i}@uni.edu" for i in range(30)],
                       "q1": [1] * 30})
    assert screen_for_pii(df.columns, df)


def test_item_stem_mentioning_email_is_not_pii():
    """A Google Forms export uses the full stem as the label."""
    df = pd.DataFrame({
        "I often check my email before bed": [1, 2, 3, 4, 5] * 8,
        "q2": [3] * 40,
    })
    assert screen_for_pii(df.columns, df) == []


def test_one_institutional_address_in_free_text_is_not_a_roster():
    df = pd.DataFrame({
        "comments": ["no comment"] * 39 + ["contact me at office@uni.edu"],
        "q2": [3] * 40,
    })
    assert screen_for_pii(df.columns, df) == []


def test_numeric_id_column_is_not_pii():
    df = pd.DataFrame({"id": range(200), "resp": [1] * 200})
    assert screen_for_pii(df.columns, df) == []


def test_label_based_screen_still_fires():
    df = pd.DataFrame({"Respondent's Name": ["Ana Lopez"] * 30, "q": [1] * 30})
    assert "Respondent's Name" in screen_for_pii(df.columns, df)


def test_screen_without_a_frame_still_works():
    """`df` is optional; the label tier must not require it."""
    assert screen_for_pii(["date of birth", "q1"]) == ["date of birth"]
