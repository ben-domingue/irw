"""The PII screen's third surface: the SPSS/Stata variable label.

zenodo.13913289 carries 1,472 real dates of birth in a column named `Q009`,
beside municipality of residence. The name tier sees `Q009`. The value tier
sees dates, which look like any other date. The words that any pattern could
match live only in the variable label, "Date of birth? (dd/mm/yyyy)", which
`load_table` discarded on purpose. Every opaque-coded SPSS deposit (`Q001`,
`v_12`, `CT1_SQ003`) was invisible to the label tier for the same reason.

Three surfaces now, because each has caught what the others could not:
  name    -- a `Nama` column of real names
  values  -- 3,130 emails under `Nombredeusuario` (no word boundary, StringDtype)
  label   -- this
and a column *labelled* "Name of the Senior Citizen" holding `1..500` serials
is why no single surface may be trusted alone.

unittest, not pytest: CI runs `python -m unittest discover` over every test
directory (.github/workflows/tests.yml) and pytest is not installed there.
"""
import unittest

import pandas as pd

from irw_triage_updated import screen_for_pii

COLS = ["Q001", "Q009", "Q010"]
LABELS = {"Q001": "Gender",
          "Q009": "Date of birth? (dd/mm/yyyy)",
          "Q010": "Municipality of residence"}


def frame():
    return pd.DataFrame({"Q001": [1] * 30,
                         "Q009": ["01/02/1990"] * 30,
                         "Q010": ["Roma"] * 30})


class LabelTierFires(unittest.TestCase):
    def test_dob_in_a_variable_label_under_an_opaque_code(self):
        hits = screen_for_pii(COLS, frame(), LABELS)
        self.assertTrue(hits)
        self.assertIn("Q009", hits[0])

    def test_the_hit_names_the_column_not_just_the_label(self):
        """The uploader has to act on a column, so report one."""
        hits = screen_for_pii(["ID1"], None, {"ID1": "Passport number"})
        self.assertTrue(hits and hits[0].startswith("ID1"))

    def test_without_labels_the_same_frame_screens_clean(self):
        """Pins the gap itself: this is what the screen did before."""
        self.assertEqual(screen_for_pii(COLS, frame()), [])


class NonEnglishDatesOfBirth(unittest.TestCase):
    FIRE = ["Data di nascita", "Fecha de nacimiento", "Geburtsdatum",
            "Date de naissance", "Geboortedatum", "Doğum tarihi",
            "Data de nascimento", "出生日期", "生年月日"]

    def test_full_dates_of_birth_fire(self):
        for lab in self.FIRE:
            with self.subTest(label=lab):
                self.assertTrue(screen_for_pii(["Q1"], None, {"Q1": lab}), lab)

    def test_a_birth_YEAR_is_a_legitimate_covariate(self):
        for lab in ("Año de nacimiento", "Anno di nascita", "Geburtsjahr",
                    "birth year", "birthyr", "Year of birth"):
            with self.subTest(label=lab):
                self.assertEqual(screen_for_pii(["Q1"], None, {"Q1": lab}), [],
                                 lab)


class ThingsThatMustNotFire(unittest.TestCase):
    def test_an_item_stem_as_a_variable_label(self):
        labels = {"v1": "I often check my email before bed",
                  "v2": "I feel calm"}
        self.assertEqual(screen_for_pii(["v1", "v2"], None, labels), [])

    def test_a_column_is_reported_once_when_name_and_label_both_hit(self):
        hits = screen_for_pii(["date of birth"], None,
                              {"date of birth": "Date of birth"})
        self.assertEqual(len(hits), 1)


class OtherSurfacesStillWork(unittest.TestCase):
    def test_value_tier_intact(self):
        df = pd.DataFrame({
            "Nombredeusuario": pd.array([f"a{i}@x.com" for i in range(40)],
                                        dtype="string"),
            "q": [1] * 40})
        self.assertTrue(screen_for_pii(df.columns, df))

    def test_name_tier_intact(self):
        df = pd.DataFrame({"Respondent's Name": ["Ana Lopez"] * 30,
                           "q": [1] * 30})
        self.assertIn("Respondent's Name", screen_for_pii(df.columns, df))

    def test_labels_argument_is_optional(self):
        self.assertEqual(screen_for_pii(["date of birth", "q1"]),
                         ["date of birth"])


if __name__ == "__main__":
    unittest.main()
