"""The write-path PII screen (review R-41, issue #3227).

What these pin is the shape of the check rather than the detectors' thresholds
(those are tested in automated_finding/tests/test_pii_*.py, against the screen
itself):

  * a VALUE-level match fails, for every family -- main, item text, conjoint
    and rankings;
  * a NAME-level match warns and never blocks, because 28 of the 29 live
    tables whose column name suggests an identifier hold coded yes/no flags;
  * a clean table produces no finding at all -- a miss is not a clearance;
  * the coarsened form of the one real hit in the corpus (`cov_zip3`) passes,
    so the check cannot flag the fix;
  * a screen that read nothing says so.

unittest, not pytest: CI runs `python -m unittest discover` and pytest is not
installed there.
"""
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from irw_validate import validate_frame                      # noqa: E402
from irw_validate.conjoint import validate_conjoint_frame     # noqa: E402
from irw_validate.rankings import validate_rankings_frame     # noqa: E402

N = 120
FIRST = ["Alice", "Bob", "Carol", "Dan", "Eve", "Frank", "Grace", "Hank",
         "Ivy", "Jack", "Kim", "Liam", "Mia", "Nina", "Omar", "Pia",
         "Quinn", "Rosa", "Sam", "Tess", "Uma", "Vic", "Wes", "Xia"]
LAST = ["Smith", "Jones", "Wu", "Lee", "Hall", "Ng", "Diaz", "Pires", "Chen",
        "Roy", "Osei", "Park", "Hoff", "Said", "Vega", "Rossi"]
#: Distinct enough to clear the screen's roster thresholds (15+ distinct
#: values, over 30% of the column), which are the triage screen's own and are
#: not re-tuned here.
NAMES = [f"{f} {l}" for l in LAST for f in FIRST]


def emails(n=N):
    return [f"person{i}@example.org" for i in range(n)]


def names(n=N):
    return [NAMES[i % len(NAMES)] for i in range(n)]


def zips(n=N):
    return [94305 + i for i in range(n)]


def responses(n=N):
    return pd.DataFrame({"id": [f"p{i}" for i in range(n)],
                         "item": [f"q{i % 4}" for i in range(n)],
                         "resp": [i % 3 for i in range(n)]})


def findings(report, check):
    return [f for f in report.findings if f.check == check]


class ValueMatchesFail(unittest.TestCase):
    def test_email_name_and_numeric_zip_all_fail(self):
        df = responses()
        df["cov_email"] = emails()
        df["cov_name"] = names()
        df["cov_zip"] = zips()
        report = validate_frame(df, label="fixture.csv", profile="upload")
        hit = findings(report, "pii_values")
        self.assertEqual(len(hit), 1, [f.check for f in report.findings])
        self.assertEqual(hit[0].severity, "error")
        self.assertFalse(report.ok)
        joined = " ".join(hit[0].details)
        for col in ("cov_email", "cov_name", "cov_zip"):
            self.assertIn(col, joined)

    def test_legacy_profile_screens_too(self):
        # The one real identifier in the corpus had been live for 516 releases,
        # so a screen that only looks at new tables cannot find it.
        df = responses()
        df["cov_email"] = emails()
        report = validate_frame(df, label="fixture.csv", profile="legacy")
        self.assertTrue(findings(report, "pii_values"))

    def test_conjoint_family(self):
        n = 60
        df = pd.DataFrame({"id": [f"p{i // 2}" for i in range(n)],
                           "task": [1] * n,
                           "profile": [1, 2] * (n // 2),
                           "choice": [1, 0] * (n // 2),
                           "attr_colour": ["red", "blue"] * (n // 2)})
        df["cov_email"] = emails(n)
        report = validate_conjoint_frame(df, label="fixture.csv")
        self.assertTrue(findings(report, "pii_values"))
        self.assertFalse(report.ok)

    def test_rankings_family(self):
        n = 60
        df = pd.DataFrame({"id": [f"p{i // 3}" for i in range(n)],
                           "task": [1] * n,
                           "item": ["c01", "c02", "c03"] * (n // 3),
                           "resp": [1, 2, 3] * (n // 3)})
        df["cov_email"] = emails(n)
        report = validate_rankings_frame(df, label="fixture.csv")
        self.assertTrue(findings(report, "pii_values"))

    def test_item_text_family(self):
        n = 40
        df = pd.DataFrame({"table": ["t"] * n,
                           "item": [f"q{i}" for i in range(n)],
                           "item_text": [f"How often do you feel {i}?" for i in range(n)],
                           "cov_email": emails(n)})
        report = validate_frame(df, label="t__items.csv", profile="upload")
        self.assertTrue(findings(report, "pii_values"))


class NameMatchesWarn(unittest.TestCase):
    def test_coded_flag_warns_and_does_not_block(self):
        # `cov_left_email` in the live corpus is a yes/no flag, not an address.
        df = responses()
        df["cov_left_email"] = [i % 2 for i in range(N)]
        report = validate_frame(df, label="fixture.csv", profile="upload")
        hit = findings(report, "pii_name")
        self.assertEqual(len(hit), 1)
        self.assertEqual(hit[0].severity, "warn")
        self.assertFalse(findings(report, "pii_values"))
        self.assertTrue(report.ok)


class CleanTablesAreSilent(unittest.TestCase):
    def test_no_finding_at_all(self):
        df = responses()
        df["cov_age"] = [20 + i % 40 for i in range(N)]
        report = validate_frame(df, label="fixture.csv", profile="upload")
        self.assertEqual(findings(report, "pii_values"), [])
        self.assertEqual(findings(report, "pii_name"), [])

    def test_truncated_zip_passes(self):
        # cov_zip3 is the coarsening the 2026-10-19 ruling asks for (irw#3231).
        # A check that flagged it would flag the fix.
        df = responses()
        df["cov_zip3"] = [943 + i % 50 for i in range(N)]
        report = validate_frame(df, label="fixture.csv", profile="upload")
        self.assertEqual(findings(report, "pii_values"), [])

    def test_item_name_column_is_not_a_roster(self):
        df = responses()
        df["cov_item_name"] = [f"Anxiety Item {i % 9}" for i in range(N)]
        report = validate_frame(df, label="fixture.csv", profile="upload")
        self.assertEqual(findings(report, "pii_values"), [])


class TheDenominatorIsAsserted(unittest.TestCase):
    def test_content_column_count_is_recorded(self):
        df = responses()
        df["cov_note"] = ["fine"] * N
        report = validate_frame(df, label="fixture.csv", profile="upload")
        recorded = [c for c in report.checks_run if c.startswith("pii_screen:")]
        self.assertEqual(recorded, ["pii_screen:content_cols=1"])

    def test_a_screen_that_read_nothing_says_so(self):
        # The failure this guards against is a dtype bug: the screen selects no
        # column, finds nothing, and reports clean. On 2026-10-19 that shape
        # read 0 of a deposit's 11 string columns.
        from irw_validate import pii

        def blind(columns, df=None, labels=None):
            blind.content_cols_screened = 0
            blind.value_hits = []
            return []

        df = responses()
        df["cov_note"] = ["fine"] * N
        real = pii._screen
        unreadable = pii._unreadable
        try:
            pii._screen = lambda: blind
            pii._unreadable = lambda frame, cols: ["cov_note"]
            found, checks = pii.check_pii(df, "fixture")
        finally:
            pii._screen = real
            pii._unreadable = unreadable
        self.assertEqual([f.check for f in found], ["pii_screen_blind"])
        self.assertEqual(found[0].severity, "warn")
        self.assertEqual(checks, ["pii_screen:content_cols=0"])

    def test_no_screen_is_reported_not_passed(self):
        from irw_validate import pii
        real = pii._screen
        try:
            pii._screen = lambda: None
            found, checks = pii.check_pii(responses(), "fixture")
        finally:
            pii._screen = real
        self.assertEqual([f.check for f in found], ["pii_screen_unavailable"])
        self.assertEqual(checks, ["pii_screen:unavailable"])


if __name__ == "__main__":
    unittest.main()
