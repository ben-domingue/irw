"""The rights-register hold on the write path (#2154).

Three rules from sweep_instrument_rights.py's header are what these pin: a hit
warns and never errors; a clean table produces no finding at all (a miss is not
a clearance); and the check runs on `upload` only. Against a small fixture
register, so the tests do not move when the real one gains a row.
"""
import contextlib
import csv
import io
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

    def test_anchored_stem_matches_only_a_whole_item(self):
        """irw#2544: the STAI-6 stem 'I am worried' flagged a study-written
        sentence (c19prc_uk_mcbride_2021_childimpact). `^stem$` is whole-item."""
        hit = rights.stem_hit
        for text in ("I am worried", "  I am worried. ", "I AM WORRIED!", "I am worried\u2026"):
            with self.subTest(text=text):
                self.assertTrue(hit("^I am worried$", text))
        for text in ("I am worried that I am not able to provide good home schooling",
                     "Sometimes I am worried", "I am worried something might go wrong."):
            with self.subTest(text=text):
                self.assertFalse(hit("^I am worried$", text))
        self.assertTrue(hit("i am worried", "Sometimes I am worried"),
                        "an unanchored stem is still a substring")
        self.assertEqual(rights.stem_core(" ^I am tense$ "), "I am tense")

    def test_anchored_stem_through_the_validator(self):
        with self.reg.open("a", newline="") as fh:
            csv.DictWriter(fh, FIELDS).writerow(
                {"instrument": "STAI-6", "family": "STAI", "verdict": "block",
                 "match_item_text": "^I am tense$|^I am worried$"})
        df = self.items(["I am worried that I am not able to provide good home schooling",
                         "I am tense."])
        (f,) = self.rights_findings(validate_frame(df, label="x_2026_scale__items",
                                                   profile="upload"))
        self.assertIn("STAI", f.message)
        self.assertIn("1 item(s)' text", f.message)
        self.assertIn("'q1'", f.message)

    def test_a_ship_ruling_is_readable_even_though_it_never_warns(self):
        """The 2026-10-18 defect: load_register() kept only hold/note verdicts,
        so a permission was invisible to everything built on it. The gate can
        discover a prohibition and never a permission."""
        reg = rights.load_register()
        ships = [r for r in reg if r["verdict"] in rights.PERMIT]
        self.assertTrue(ships, "a `ship` row must survive loading")
        self.assertIn("Rosenberg", [r["instrument"] for r in ships])
        # and it still warns about nothing, on either surface
        self.assertEqual(rights.check_item_text(
            self.items(["I feel that I have a number of good qualities"]),
            "x_2026_scale", reg), [])
        self.assertEqual(rights.check_item_codes(
            self.responses(["rses1", "rses2", "rses3"]), "x_2026_scale", reg), [])

    def test_lookup_finds_a_ruling_by_name(self):
        (row, where), = rights.lookup("rosenberg")
        self.assertEqual(row["verdict"], "ship")
        self.assertIn("instrument", where)
        self.assertIn("SHIPS", rights.verdict_meaning(row["verdict"]))
        self.assertIn("DOES NOT SHIP",
                      rights.verdict_meaning("block"))
        self.assertIn("note", rights.verdict_meaning("ship_with_note"))

    def test_lookup_reads_the_rule_text_too(self):
        """An adaptation is often ruled on inside another row's rule rather than
        getting a row of its own, which is where the MSLQ's 'adaptations ship
        too' lives."""
        with self.reg.open("a", newline="") as fh:
            csv.DictWriter(fh, FIELDS).writerow(
                {"instrument": "Parent instrument", "family": "PI",
                 "verdict": "ship", "rule": "adaptations such as the Widget "
                                            "Scale ship under this row"})
        hits = rights.lookup("widget scale")
        self.assertEqual([w for _, w in hits], [["rule"]])

    def test_lookup_on_an_unregistered_name_is_silence_not_nothing(self):
        self.assertEqual(rights.lookup("Zarquon Anxiety Index"), [])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = rights._cli(["Zarquon", "Anxiety", "Index"])
        self.assertEqual(code, 1, "an unregistered name is not a success")
        self.assertIn("SILENCE, not permission", out.getvalue())

    def test_cli_prints_the_verdict_and_says_which_surfaces_can_fire(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = rights._cli(["Rosenberg"])
        text = out.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("verdict  ship", text)
        self.assertIn("not an identification", text)
        self.assertIn("stems    1", text)

    def test_the_real_register_loads(self):
        os.environ.pop(rights.REGISTER_ENV)
        reg = rights.load_register()
        self.assertIsNotNone(reg, "itemtext/instrument_rights_register.csv not found")
        self.assertTrue(any(r["verdict"] == "block" for r in reg))
        self.assertTrue(any(r["verdict"] in rights.PERMIT for r in reg),
                        "the real register's permissions must load too")

    def test_the_mslq_permission_is_findable_in_the_real_register(self):
        """The case this exists for: a verbatim MSLQ subscale was held because
        nothing could surface a `ship` ruling whose row carries no stems and
        whose code pattern cannot match the table's codes."""
        os.environ.pop(rights.REGISTER_ENV)
        hits = rights.lookup("MSLQ")
        mslq = [r for r, _ in hits if r["family"] == "MSLQ"]
        self.assertTrue(mslq, "the MSLQ row must be findable by name")
        self.assertEqual(mslq[0]["verdict"], "ship")
        self.assertEqual(mslq[0]["stems"], [],
                         "if this row gains stems, the comment above is stale")


if __name__ == "__main__":
    unittest.main()
