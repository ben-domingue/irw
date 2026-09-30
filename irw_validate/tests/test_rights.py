"""The rights-register hold on the write path (#2154).

Three rules from sweep_instrument_rights.py's header are what these pin: a hit
warns and never errors; a clean table produces no finding at all (a miss is not
a clearance); and the check runs on `upload` only. Against a small fixture
register, so the tests do not move when the real one gains a row.
"""
import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from irw_validate import validate_frame  # noqa: E402
from irw_validate import rights  # noqa: E402

FIELDS = ["instrument", "family", "verdict", "rule", "clause", "source_url",
          "source_sha256", "fetched", "match_item_text", "match_item_code", "notes"]


class Rights(unittest.TestCase):
    def setUp(self):
        tmp = self.enterContext(tempfile.TemporaryDirectory())
        self.reg = Path(tmp) / "register.csv"
        with self.reg.open("w", newline="") as fh:
            w = csv.DictWriter(fh, FIELDS)
            w.writeheader()
            w.writerow({"instrument": "Perceived Stress Scale (PSS-10)", "family": "PSS",
                        "verdict": "block", "rule": "2026-09-06 irw#1955",
                        "match_item_text": "unable to control the important things|on top of things",
                        "match_item_code": "^pss[_ ]?[0-9]"})
            w.writerow({"instrument": "Life Orientation Test-Revised", "family": "LOT-R",
                        "verdict": "ship_with_note", "match_item_code": "^lot"})
            w.writerow({"instrument": "Rosenberg", "family": "RSES", "verdict": "ship",
                        "match_item_text": "i feel that i have a number of good qualities",
                        "match_item_code": "^rses"})
            w.writerow({"instrument": "Prose cell", "family": "GHQ", "verdict": "block",
                        "match_item_code": "ghq1..ghq28 (a note, not a pattern"})
        os.environ[rights.REGISTER_ENV] = str(self.reg)
        self.addCleanup(os.environ.pop, rights.REGISTER_ENV, None)

    def items(self, texts):
        return pd.DataFrame({"table": "x_2026_scale", "item": [f"q{i}" for i in range(len(texts))],
                             "item_text": texts, "resp": 1})

    def responses(self, codes):
        return pd.DataFrame([(i, c, 1 + (i + j) % 5) for i in range(1, 120)
                             for j, c in enumerate(codes)], columns=["id", "item", "resp"])

    def rights_findings(self, report):
        return [f for f in report.findings if f.check == "rights_register"]

    def test_item_text_hit_warns_and_quotes_the_row(self):
        df = self.items(["In the last month, how often have you felt that you were "
                         "UNABLE to control the important things in your life?",
                         "Something unrelated"])
        report = validate_frame(df, label="x_2026_scale__items", profile="upload")
        (f,) = self.rights_findings(report)
        self.assertEqual(f.severity, "warn")
        self.assertIn("PSS", f.message)
        self.assertIn("verdict block", f.message)
        self.assertIn("'q0'", f.message)
        self.assertIn("not a verdict", f.message)
        self.assertTrue(report.ok, "a rights hit must never block the gate")

    def test_translated_column_hit_warns(self):
        """2026-09-29 (irw#2401): a block row covers *_translated. beck_2021_iesr's
        German item_text matched nothing; its English twin matched every stem."""
        df = self.items(["Wie oft hatten Sie das Gefuehl ...", "Etwas anderes"])
        df["language"] = "German"
        df["item_text_translated"] = ["How often have you felt that you were unable "
                                      "to control the important things in your life?",
                                      "NA"]
        report = validate_frame(df, label="x_2026_scale__items", profile="upload")
        (f,) = self.rights_findings(report)
        self.assertEqual(f.severity, "warn")
        self.assertIn("item_text_translated", f.message)
        self.assertIn("'q0'", f.message)
        self.assertTrue(report.ok)

    def test_clean_table_says_nothing(self):
        report = validate_frame(self.items(["How tall are you?"]),
                                label="x_2026_scale__items", profile="upload")
        self.assertEqual(self.rights_findings(report), [])
        self.assertIn("rights_register", report.checks_run)
        self.assertFalse(any("rights" in f.message.lower() and f.severity == "info"
                             for f in report.findings),
                         "a miss must not be reported as a clearance")

    def test_ship_verdict_is_not_a_hold(self):
        report = validate_frame(self.items(["I feel that I have a number of good qualities"]),
                                label="x_2026_scale__items", profile="upload")
        self.assertEqual(self.rights_findings(report), [])

    def test_response_item_codes(self):
        report = validate_frame(self.responses(["pss_1", "pss_2", "pss_3", "lot3",
                                                "lot4", "lot5", "other"]),
                                label="x_2026_scale", profile="upload")
        found = {f.message.split("register's ")[1].split(" row")[0]: f
                 for f in self.rights_findings(report)}
        self.assertEqual(set(found), {"PSS", "LOT-R"})
        self.assertIn("3 item code(s)", found["PSS"].message)
        self.assertIn("wording cannot", found["PSS"].message)
        self.assertTrue(all(f.severity == "warn" for f in found.values()))

    def test_one_stray_code_among_many_is_not_a_lead(self):
        """A word-list table matched unanchored patterns through one word in
        thousands; 'pss_1' alone among 40 codes is the same shape."""
        codes = ["pss_1"] + [f"w{i}" for i in range(40)]
        report = validate_frame(self.responses(codes), label="x_2026_scale",
                                profile="upload")
        self.assertEqual(self.rights_findings(report), [])

    def test_upload_profile_only(self):
        for profile in ("legacy", "triage", "core"):
            with self.subTest(profile=profile):
                report = validate_frame(self.responses(["pss_1", "pss_2", "pss_3"]),
                                        label="x_2026_scale", profile=profile)
                self.assertEqual(self.rights_findings(report), [])

    def test_missing_register_is_recorded_not_silent(self):
        os.environ[rights.REGISTER_ENV] = str(self.reg.parent / "nope.csv")
        report = validate_frame(self.responses(["pss_1", "pss_2"]),
                                label="x_2026_scale", profile="upload")
        self.assertIn("rights_register:unavailable", report.checks_run)
        self.assertEqual(self.rights_findings(report), [])

    def test_the_real_register_loads(self):
        os.environ.pop(rights.REGISTER_ENV)
        reg = rights.load_register()
        self.assertIsNotNone(reg, "itemtext/instrument_rights_register.csv not found")
        self.assertTrue(any(r["verdict"] == "block" for r in reg))


if __name__ == "__main__":
    unittest.main()
