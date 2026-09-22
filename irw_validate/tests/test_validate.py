"""Tests for irw_validate. Offline, stdlib unittest, no network, no credentials
-- the pattern red_up/tests/test_red_up.py established.

The first class is the important one. Fifty scripts in `data/` call `run_qc` and
read `.name` / `.status` / `.detail` off the result, and `run_qc` had no test
coverage at all before this file. GOLDEN pins the exact emission order and
status of every check for eight fixtures. The original move preserved behavior;
PR #1697 explicitly corrects a spurious range finding on text-only responses,
while retaining their numeric failures. #2314 excludes missing responses from
the numeric denominator; all-missing responses still fail the missingness check.
"""
from __future__ import annotations

import csv
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from irw_validate import (CORE_CHECKS, exit_code, validate_file,  # noqa: E402
                          validate_frame)
from irw_validate._checks import run_qc  # noqa: E402
from irw_validate.cli import main  # noqa: E402


def F(**cols):
    return pd.DataFrame(cols)


FIXTURES = {
    "clean": lambda: F(id=[1, 1, 2, 2, 3, 3], item=["a", "b"] * 3, resp=[1, 2, 3, 4, 5, 1]),
    "missing_col": lambda: F(id=[1, 2], item=["a", "b"]),
    "all_na_resp": lambda: F(id=[1, 2], item=["a", "b"], resp=[None, None]),
    "dup_id_item": lambda: F(id=[1, 1], item=["a", "a"], resp=[1, 2]),
    "dup_with_wave": lambda: F(id=[1, 1], item=["a", "a"], resp=[1, 2], wave=[1, 2]),
    "nonnumeric_resp": lambda: F(id=[1, 2, 3], item=["a", "b", "c"], resp=["x", "y", "z"]),
    "no_variation": lambda: F(id=[1, 2, 3], item=["a", "b", "c"], resp=[1, 1, 1]),
    "unprefixed_cov": lambda: F(id=[1, 2], item=["a", "b"], resp=[1, 2], age=[30, 40]),
}

#: Captured before the 2026-09-02 move, with reviewed corrections:
#: all-text responses retain numeric failures, not a spurious numeric-range finding.
#: #2314 excludes missing responses from resp_numeric; all-null still fails resp_na.
GOLDEN = {
    "clean": [("required_columns", "pass"), ("resp_numeric", "pass"),
              ("dup_id_item", "pass")],
    "missing_col": [("required_columns", "fail")],
    "all_na_resp": [("required_columns", "pass"), ("resp_na", "fail"),
                    ("resp_numeric", "pass"), ("dup_id_item", "pass"),
                    ("resp_variation*", "fail"), ("density*", "warn")],
    "dup_id_item": [("required_columns", "pass"), ("resp_numeric", "pass"),
                    ("dup_id_item", "fail")],
    "dup_with_wave": [("required_columns", "pass"), ("resp_numeric", "pass"),
                      ("dup_id_item", "warn")],
    "nonnumeric_resp": [("required_columns", "pass"), ("resp_numeric", "fail"),
                        ("dup_id_item", "pass"), ("resp_variation*", "fail")],
    "no_variation": [("required_columns", "pass"), ("resp_numeric", "pass"),
                     ("dup_id_item", "pass"), ("resp_variation*", "fail"),
                     ("imputed_values*", "warn")],
    "unprefixed_cov": [("required_columns", "pass"), ("resp_numeric", "pass"),
                       ("dup_id_item", "pass"), ("cov_prefix", "warn"),
                       ("imputed_values*", "warn")],
}


class GoldenCompatibility(unittest.TestCase):
    """Existing callers retain the reviewed check contract and emission order."""

    def test_reviewed_emission_order_and_status(self):
        for name, build in FIXTURES.items():
            with self.subTest(fixture=name):
                got = [(c.name, c.status) for c in run_qc(build())]
                self.assertEqual(got, GOLDEN[name])

    def test_check_objects_still_expose_the_three_attributes_callers_use(self):
        for check in run_qc(FIXTURES["unprefixed_cov"]()):
            self.assertIsInstance(check.name, str)
            self.assertIn(check.status, ("pass", "warn", "fail"))
            self.assertIsInstance(check.detail, str)

    def test_the_shim_is_importable_by_its_old_name(self):
        from irw_validate.compat import Check, run_qc as shimmed
        self.assertIs(shimmed, run_qc)
        self.assertTrue(hasattr(Check("x", "pass", "y"), "detail"))


class Profiles(unittest.TestCase):
    """Severity is a property of (check, profile), never of the check alone."""

    def test_heuristics_do_not_block_the_gate(self):
        # Composite-looking names alone remain insufficient to block upload.
        df = F(id=[1, 1, 2, 2, 3, 3], item=["total_a", "total_b"] * 3,
               resp=[1, 2, 3, 4, 5, 1])
        upload = validate_frame(df, profile="upload")
        composite = [f for f in upload.findings if f.check == "composite_items*"]
        self.assertEqual([f.severity for f in composite], ["warn"])
        self.assertFalse(upload.errors)

    def test_gate_errors_still_block(self):
        report = validate_frame(FIXTURES["no_variation"](), profile="upload")
        self.assertIn("resp_variation*", [f.check for f in report.errors])

    def test_core_profile_is_only_the_r_parity_checks(self):
        report = validate_frame(FIXTURES["no_variation"](), profile="core")
        for finding in report.findings:
            self.assertTrue(
                finding.check in CORE_CHECKS or finding.check.endswith("_na"),
                f"{finding.check} is not part of the validate_irw.R subset")

    def test_triage_profile_preserves_today_severities(self):
        report = validate_frame(FIXTURES["dup_id_item"](), profile="triage")
        dup = [f for f in report.findings if f.check == "dup_id_item"]
        self.assertEqual([f.severity for f in dup], ["error"])

    def test_legacy_profile_forgives_the_cov_prefix_rule(self):
        report = validate_frame(FIXTURES["unprefixed_cov"](), profile="legacy")
        self.assertNotIn("cov_prefix", [f.check for f in report.findings])


class ExtraChecks(unittest.TestCase):
    """The prose rules in datastandard.md, now executable."""

    def test_cov_age_sentinel_is_caught(self):
        df = F(id=list(range(1, 5)), item=["a"] * 4, resp=[1, 2, 3, 4],
               cov_age=[34, 41, 999, 28])
        report = validate_frame(df, profile="upload")
        cov = [f for f in report.findings if f.check == "cov_range"]
        self.assertEqual(len(cov), 1)
        self.assertIn("sentinel", cov[0].message)

    def test_cov_age_negative_offset_is_caught(self):
        df = F(id=[1, 2, 3], item=["a"] * 3, resp=[1, 2, 3],
               cov_age=[-18090, 44, 51])
        report = validate_frame(df, profile="upload")
        cov = [f for f in report.findings if f.check == "cov_range"]
        self.assertIn("date or days-since-epoch", cov[0].message)

    def test_cov_age_out_of_range_blocks_the_upload(self):
        """Promoted from warn to error 2026-09-05 (irw#1856)."""
        df = F(id=list(range(1, 5)), item=["a"] * 4, resp=[1, 2, 3, 4],
               cov_age=[34, 41, 999, 28])
        report = validate_frame(df, profile="upload")
        self.assertIn("cov_range", [f.check for f in report.errors])
        self.assertFalse(report.ok, "an out-of-range cov_age must refuse the upload")

    def test_cov_range_severity_can_be_dialled_back(self):
        """The promotion is a test, so it reverses without a deploy."""
        import os
        os.environ["IRW_COV_RANGE_SEVERITY"] = "warn"
        try:
            df = F(id=list(range(1, 5)), item=["a"] * 4, resp=[1, 2, 3, 4],
                   cov_age=[34, 41, 999, 28])
            report = validate_frame(df, profile="upload")
            self.assertIn("cov_range", [f.check for f in report.warnings])
            self.assertTrue(report.ok)
        finally:
            del os.environ["IRW_COV_RANGE_SEVERITY"]

    def test_plausible_ages_pass(self):
        df = F(id=[1, 2, 3], item=["a"] * 3, resp=[1, 2, 3], cov_age=[18, 45, 92])
        report = validate_frame(df, profile="upload")
        self.assertNotIn("cov_range", [f.check for f in report.findings])

    def test_long_table_name_blocks(self):
        df = FIXTURES["clean"]()
        long_name = "a" * 41
        report = validate_frame(df, label=f"{long_name}.csv", profile="upload")
        self.assertIn("name_length", [f.check for f in report.errors])

    def test_name_checks_do_not_run_under_triage(self):
        report = validate_frame(FIXTURES["clean"](), label="A" * 60 + ".csv",
                                profile="triage")
        self.assertNotIn("name_length", [f.check for f in report.findings])

    def test_resp_dtype_catches_numbers_stored_as_text(self):
        df = F(id=[1, 2, 3], item=["a", "b", "c"], resp=["1", "2", "3"])
        report = validate_frame(df, profile="upload")
        self.assertIn("resp_dtype", [f.check for f in report.errors])


class ItemText(unittest.TestCase):
    """An __items.csv has its own schema and must not be judged as response data."""

    def _items(self, n_rep=1):
        rows = {"table": [], "item": [], "item_text": [], "resp": [], "option_text": []}
        for _ in range(n_rep):
            for i in range(1, 4):
                for r in range(4):
                    rows["table"].append("t_2024_scale")
                    rows["item"].append(f"Q{i}")
                    rows["item_text"].append(f"question {i}")
                    rows["resp"].append(r)
                    rows["option_text"].append(f"option {r}")
        return pd.DataFrame(rows)

    def test_item_text_is_not_judged_as_response_data(self):
        report = validate_frame(self._items(), label="t_2024_scale__items.csv")
        self.assertTrue(report.ok, report.findings)
        self.assertNotIn("required_columns",
                         [f.check for f in report.errors])

    def test_a_doubled_item_text_table_is_caught(self):
        # the #1816 defect: an upload appended beside the previous version
        report = validate_frame(self._items(n_rep=2), label="t_2024_scale__items.csv")
        self.assertIn("dup_item_resp", [f.check for f in report.errors])

    def test_two_scale_directions_in_one_table_are_named_as_such(self):
        # afps_vangsness_2019: resp=1 carries both "Strongly agree" and
        # "Strongly disagree". Same repeated (item, resp), completely different
        # fault, and calling it a doubled upload would send someone the wrong way.
        df = self._items()
        flipped = df.copy()
        flipped["option_text"] = flipped["resp"].map(
            {0: "option 3", 1: "option 2", 2: "option 1", 3: "option 0"})
        both = pd.concat([df, flipped], ignore_index=True)
        report = validate_frame(both, label="t_2024_scale__items.csv")
        checks = [f.check for f in report.errors]
        self.assertIn("resp_ambiguous", checks)
        self.assertNotIn("dup_item_resp", checks)

    def test_missing_item_text_columns_block(self):
        df = pd.DataFrame({"id": [1], "item": ["a"], "resp": [1]})
        report = validate_frame(df, label="t_2024_scale__items.csv")
        self.assertIn("required_columns", [f.check for f in report.errors])
        self.assertIn("item text", report.errors[0].message)

    def test_the_name_cap_still_applies_to_item_text(self):
        report = validate_frame(self._items(), label=("x" * 41) + "__items.csv")
        self.assertIn("name_length", [f.check for f in report.errors])


class ScoredTables(unittest.TestCase):
    """A scored table is a different object and needs a different rule."""

    def _mc(self, n_items=20, dup=False):
        rows = {k: [] for k in ("table", "item", "item_text", "correct_response",
                                "option_text", "resp")}
        for i in range(n_items):
            for j, opt in enumerate(("right", "wrong a", "wrong b")):
                rows["table"].append("mc_2024_quiz")
                rows["item"].append(i)
                rows["item_text"].append(f"question {i}")
                rows["correct_response"].append("right")
                rows["option_text"].append(opt)
                rows["resp"].append(1 if j == 0 else 0)
        df = pd.DataFrame(rows)
        return pd.concat([df, df.iloc[[0]]], ignore_index=True) if dup else df

    def test_distractors_sharing_a_resp_are_not_a_defect(self):
        # spanishmegastudy: 1,270 items, three distractors each, all resp=0.
        # Judged by the Likert rule this would flag every one of them.
        report = validate_frame(self._mc(), label="mc_2024_quiz__items.csv")
        self.assertTrue(report.ok, report.findings)

    def test_an_exact_repeat_in_a_scored_table_still_counts(self):
        report = validate_frame(self._mc(dup=True), label="mc_2024_quiz__items.csv")
        self.assertIn("dup_row", [f.check for f in report.errors])

    def test_an_empty_correct_response_does_not_read_as_scored(self):
        # pandas 3 keeps an all-NaN column MISSING through astype(str), so a
        # string-only emptiness test matches nothing and reads it as populated.
        df = self._mc()
        df["correct_response"] = pd.NA
        df.loc[0, "option_text"] = "wrong a"     # now resp=1 has two labels
        report = validate_frame(df, label="likert_2024__items.csv")
        self.assertIn("resp_ambiguous", [f.check for f in report.errors])

class RepeatedMeasures(unittest.TestCase):
    """A rater or a trial explains a repeated id+item; a group does not."""

    def _rated(self, col="rater"):
        return pd.DataFrame({"id": [1, 1, 2, 2], "item": ["a", "a", "a", "a"],
                             "resp": [1, 2, 3, 4], col: [1, 2, 1, 2]})

    def test_a_rater_column_explains_the_repeat(self):
        report = validate_frame(self._rated(), profile="upload")
        self.assertNotIn("dup_id_item", [f.check for f in report.findings])

    def test_so_do_trial_and_period(self):
        for col in ("trialnum", "order", "period", "session", "occasion"):
            with self.subTest(col=col):
                report = validate_frame(self._rated(col), profile="upload")
                self.assertNotIn("dup_id_item", [f.check for f in report.findings])

    def test_a_trial_prefixed_index_explains_the_repeat(self):
        # how the robison_2026_retesting_* and cogcontrol_* tables index trials
        df = F(id=[1, 1, 2, 2], item=["a"] * 4, resp=[0, 1, 1, 0],
               trial_number=[1, 2, 1, 2])
        report = validate_frame(df, label="t_2024_x.csv")
        self.assertNotIn("dup_id_item", [f.check for f in report.findings])
        self.assertIs(report.conforms, True)

    def test_a_group_column_does_not(self):
        # group describes the person, not the occasion -- a person appearing
        # twice under it is a real question, not an explanation
        report = validate_frame(self._rated("group"), profile="upload")
        self.assertIn("dup_id_item", [f.check for f in report.errors])

    def test_a_bare_table_still_fails(self):
        df = pd.DataFrame({"id": [1, 1], "item": ["a", "a"], "resp": [1, 2]})
        self.assertIn("dup_id_item",
                      [f.check for f in validate_frame(df, profile="upload").errors])

    def test_triage_is_unchanged(self):
        # the 50 callers see what they always saw
        report = validate_frame(self._rated(), profile="triage")
        self.assertIn("dup_id_item", [f.check for f in report.findings])


class ResponseTimes(unittest.TestCase):
    """`rt` is the seconds ONE item response took (standard.qmd). Each check
    below tests that sentence from a different side. The shapes come from
    openesm_0018_bailon, an ESM table whose `rt` is the latency from beep to
    response -- one value per beep, copied onto both items, 0 where nobody
    answered -- which the old median>60000 units check passed in silence."""

    def _esm(self, rt_per_wave):
        rows = []
        for pid in range(1, 41):
            for wave, rt in enumerate(rt_per_wave, start=1):
                for item in ("arousal", "valence"):
                    rows.append({"id": pid, "item": item, "resp": 3,
                                 "wave": wave, "rt": rt})
        return pd.DataFrame(rows)

    def test_an_occasion_level_rt_is_named_as_such(self):
        report = validate_frame(self._esm([12, 300, 45]), label="esm_2024.csv")
        finding = next(f for f in report.findings if f.check == "rt_item_level*")
        self.assertIn("100% of 120 person-occasions", finding.message)

    def test_a_genuinely_item_level_rt_is_not_flagged(self):
        df = self._esm([12, 300, 45])
        df["rt"] = [3, 9] * (len(df) // 2)
        names = [f.check for f in validate_frame(df, label="esm_2024.csv").findings]
        self.assertNotIn("rt_item_level*", names)

    def test_zero_response_times_are_flagged_as_a_sentinel(self):
        df = self._esm([0, 300, 45])
        finding = next(f for f in validate_frame(df, label="esm_2024.csv").findings
                       if f.check == "rt_zero*")
        self.assertIn("33%", finding.message)

    def test_a_stray_zero_is_not_worth_a_warning(self):
        df = self._esm([12, 300, 45])
        df.loc[0, "rt"] = 0
        names = [f.check for f in validate_frame(df, label="esm_2024.csv").findings]
        self.assertNotIn("rt_zero*", names)

    def test_millisecond_units_are_caught_well_below_the_old_threshold(self):
        # 1.4 s and 2.6 s recorded as ms: the old check needed a median of
        # 60000 before it said anything.
        df = self._esm([1400, 2600])
        finding = next(f for f in validate_frame(df, label="esm_2024.csv").findings
                       if f.check == "rt_units*")
        self.assertIn("milliseconds", finding.message)

    def test_plausible_seconds_say_nothing_about_units(self):
        names = [f.check for f in
                 validate_frame(self._esm([4, 11, 30]), label="esm_2024.csv").findings]
        self.assertNotIn("rt_units*", names)

    def test_none_of_the_rt_checks_block_an_upload(self):
        report = validate_frame(self._esm([0, 1400, 2600]), label="esm_2024.csv")
        self.assertEqual([], [f.check for f in report.errors
                              if f.check.startswith("rt_")])


class TableNames(unittest.TestCase):
    def test_every_table_suffix_is_stripped(self):
        from irw_validate.core import _table_name
        for label, want in (("a_2024_x.csv", "a_2024_x"),
                            ("a_2024_x.Rdata", "a_2024_x"),
                            ("a_2024_x.rds", "a_2024_x"),
                            ("dir/a_2024_x.tsv", "a_2024_x"),
                            ("a_2024_x", "a_2024_x")):
            self.assertEqual(_table_name(label), want)

    def test_the_extension_does_not_fail_the_lowercase_rule(self):
        # stripping only .csv made all 922 legacy tables fail name_charset on
        # the capital R of ".Rdata"
        df = pd.DataFrame({"id": [1, 2], "item": ["a", "b"], "resp": [1, 2]})
        report = validate_frame(df, label="fine_2019_table.Rdata", profile="legacy")
        self.assertNotIn("name_charset", [f.check for f in report.findings])


class RPythonParity(unittest.TestCase):
    """The fork cannot silently reopen: one list, two languages, checked here."""

    def test_validate_irw_r_declares_the_same_core_checks(self):
        r_file = Path(__file__).resolve().parents[2] / "misc" / "validate_irw.R"
        if not r_file.exists():
            self.skipTest("misc/validate_irw.R not present")
        text = r_file.read_text()
        declared = set(re.findall(r"#\s*@check\s+([a-z_*]+)", text))
        self.assertTrue(
            declared, "validate_irw.R carries no `# @check <name>` markers -- "
                      "add one per check so this parity test can see them")
        self.assertEqual(
            declared, set(CORE_CHECKS),
            "misc/validate_irw.R and irw_validate.model.CORE_CHECKS disagree; "
            "the fork this package closed has reopened")


class Standard(unittest.TestCase):
    """Conformance to the IRW Data Standard is a separate verdict from the gate."""

    def test_every_core_check_names_a_clause(self):
        from irw_validate import CLAUSES
        for check in CORE_CHECKS:
            self.assertIn(check, CLAUSES, f"{check} tests no clause of the standard")

    def test_a_clean_table_conforms(self):
        report = validate_frame(FIXTURES["clean"](), label="x_2024_y.csv")
        self.assertIs(report.conforms, True)
        self.assertEqual(report.to_dict()["standard_version"], "1.0")

    def test_missing_resp_names_clause_c1(self):
        report = validate_frame(FIXTURES["missing_col"](), label="x_2024_y.csv")
        self.assertIs(report.conforms, False)
        self.assertEqual(report.nonconforming, ["C1"])

    def test_text_resp_and_duplicates_name_their_clauses(self):
        self.assertEqual(validate_frame(FIXTURES["nonnumeric_resp"]()).nonconforming, ["C4"])
        self.assertEqual(validate_frame(FIXTURES["dup_id_item"]()).nonconforming, ["C5"])

    def test_intake_policy_does_not_touch_conformance(self):
        # 3 ids is far under the sample floor, and the name breaks the charset
        # rule: IRW would warn about both, and the table still conforms.
        report = validate_frame(FIXTURES["clean"](), label="Not A Good Name.csv")
        self.assertIn("sample_floor", [f.check for f in report.findings])
        self.assertIs(report.conforms, True)

    def test_a_waiver_does_not_make_a_table_conform(self):
        report = validate_frame(FIXTURES["nonnumeric_resp"]())
        report.overridden, report.findings = report.errors, report.warnings
        self.assertTrue(report.ok)
        self.assertIs(report.conforms, False)

    def test_no_verdict_where_the_profile_reads_the_clauses_differently(self):
        for profile in ("core", "triage"):
            self.assertIsNone(validate_frame(FIXTURES["clean"](), profile=profile).conforms)

    def test_no_verdict_for_item_text(self):
        df = F(table=["t"] * 2, item=["a", "b"], item_text=["one", "two"])
        self.assertIsNone(validate_frame(df, label="t__items.csv").conforms)

    def test_the_report_leads_with_both_verdicts(self):
        from irw_validate import format_report
        text = format_report(validate_frame(FIXTURES["dup_id_item"](), label="x.csv"))
        self.assertIn("IRW Data Standard 1.0: does not conform (C5)", text)
        self.assertIn("IRW upload gate: blocked", text)
        self.assertIn("[C5]", text)


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        # never append to the repository's real waiver ledger from a test run
        os.environ["IRW_VALIDATE_LEDGER"] = os.path.join(self.tmp.name, "ledger.csv")
        self.addCleanup(os.environ.pop, "IRW_VALIDATE_LEDGER", None)

    def test_override_is_recorded_in_the_ledger(self):
        rows = [(1, "a", "x"), (2, "b", "y")]
        path = self._write("bad_2024_scale.csv", rows)
        reason = "resp is a documented free-text probe, confirmed with the author"
        main([path, "--override", reason])
        ledger = Path(os.environ["IRW_VALIDATE_LEDGER"])
        self.assertTrue(ledger.exists(), "a waiver must leave a trail")
        body = ledger.read_text()
        self.assertIn(reason, body)
        self.assertIn("resp_numeric", body)

    def _write(self, name, rows, header=("id", "item", "resp")):
        path = os.path.join(self.tmp.name, name)
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)
        return path

    def test_clean_table_exits_zero(self):
        rows = [(i, f"q{j}", (i + j) % 5 + 1) for i in range(1, 40) for j in range(1, 5)]
        self.assertEqual(main([self._write("ok_2024_scale.csv", rows)]), 0)

    def test_blocking_table_exits_one(self):
        rows = [(1, "a", "x"), (2, "b", "y"), (3, "c", "z")]
        self.assertEqual(main([self._write("bad_2024_scale.csv", rows)]), 1)

    def test_missing_file_exits_two(self):
        self.assertEqual(main([os.path.join(self.tmp.name, "nope.csv")]), 2)

    def test_strict_promotes_warnings(self):
        rows = [(i, "a", 1 + i % 3) for i in range(1, 20)]
        path = self._write("small_2024_scale.csv", rows)
        self.assertEqual(main([path]), 0)          # sample_floor is a warning
        self.assertEqual(main([path, "--strict"]), 1)

    def test_override_without_a_reason_is_rejected(self):
        rows = [(1, "a", "x"), (2, "b", "y")]
        path = self._write("bad_2024_scale.csv", rows)
        self.assertEqual(main([path, "--override", "nope"]), 2)
        self.assertEqual(main([path, "--override-check", "resp_numeric"]), 2)

    def test_override_waives_and_still_reports(self):
        rows = [(1, "a", "x"), (2, "b", "y")]
        path = self._write("bad_2024_scale.csv", rows)
        reason = "resp is a documented free-text probe, confirmed with the author"
        self.assertEqual(main([path, "--override", reason]), 0)

    def test_scoped_override_leaves_other_errors_blocking(self):
        rows = [(1, "a", "x"), (2, "b", "y")]
        path = self._write("bad_2024_scale.csv", rows)
        reason = "resp is a documented free-text probe, confirmed with the author"
        self.assertEqual(
            main([path, "--override-check", "resp_numeric", "--override", reason]),
            1, "resp_variation* should still block")


class RewordedMessages(unittest.TestCase):
    """#2314: six checks said things the data does not support. The claims are
    gone; the gate decisions they rode on are unchanged."""

    def _detail(self, df, check, profile="triage"):
        report = validate_frame(df, profile=profile)
        hits = [f.message for f in report.findings if f.check == check]
        self.assertTrue(hits, f"{check} did not fire")
        return hits[0]

    # item 1 -- imputed_values* reports concentration, not a cause
    def test_concentration_no_longer_names_mean_imputation(self):
        detail = self._detail(FIXTURES["no_variation"](), "imputed_values*")
        self.assertNotIn("possible mean imputation", detail)
        self.assertIn("does not establish a cause", detail)
        self.assertIn("reports response concentration only", detail)

    def test_every_concentrated_item_is_counted_not_just_the_first(self):
        # three items, all fully concentrated: the old check broke after the
        # first and named it alone, reading as though it were the only one
        df = F(id=[1, 2, 3] * 3, item=["a"] * 3 + ["b"] * 3 + ["c"] * 3,
               resp=[7] * 9)
        self.assertIn("3 of 3 item(s)",
                      self._detail(df, "imputed_values*"))

    # item 3 -- dup_id_item reports the tested keys and the residual
    def test_a_present_occasion_column_is_tested_not_assumed(self):
        # wave is present, and keying on it changes nothing: id 1 / item a
        # repeats within wave 1. The old message called this "likely ok".
        df = F(id=[1, 1, 1, 2], item=["a"] * 4, resp=[1, 2, 3, 4],
               wave=[1, 1, 2, 1])
        detail = self._detail(df, "dup_id_item")
        self.assertNotIn("likely ok", detail)
        self.assertIn("excess row(s) remain", detail)
        self.assertIn("wave", detail)

    def test_the_residual_counts_the_full_key_combination(self):
        # trial restarts inside each wave, so neither column keys a row alone;
        # one genuine excess row survives both together
        df = F(id=[1, 1, 1], item=["a"] * 3, resp=[1, 2, 3],
               wave=[1, 1, 1], trial_number=[1, 1, 2])
        detail = self._detail(df, "dup_id_item")
        self.assertIn("1 excess row(s) remain", detail)
        self.assertIn("trial_number", detail)

    def test_a_key_that_does_resolve_is_reported_as_such(self):
        detail = self._detail(FIXTURES["dup_with_wave"](), "dup_id_item")
        self.assertIn("made unique by wave", detail)

    def test_the_gate_rescue_still_uses_the_same_keys(self):
        # the hoisted helper must not change which repeats the gate forgives
        df = F(id=[1, 1], item=["a", "a"], resp=[1, 2], trial_number=[1, 2])
        report = validate_frame(df, profile="upload")
        self.assertNotIn("dup_id_item", [f.check for f in report.findings])
        self.assertIn("dup_id_item:resolved_by_trial_number", report.checks_run)

    # item 4 -- id_na / resp_na distinguish typed nulls from parsed tokens
    def test_missing_value_wording_is_profile_aware(self):
        df = F(id=[1, 2, 3], item=["a", "b", "c"], resp=[1, None, 3])
        triage = self._detail(df, "resp_na", profile="triage")
        upload = self._detail(df, "resp_na", profile="upload")
        self.assertIn("may be empty cells or literal 'NA'-style text", triage)
        self.assertIn("read as a response on this profile", upload)
        self.assertNotEqual(triage, upload)

    # item 6 -- zero numeric categories is not one response value
    def test_stored_text_reports_zero_categories_not_one(self):
        detail = self._detail(FIXTURES["nonnumeric_resp"](), "resp_variation*")
        self.assertIn("3 distinct value(s) are stored as text", detail)
        self.assertIn("not one response value", detail)

    def test_a_genuinely_constant_response_still_says_one(self):
        self.assertIn("1 unique numeric value",
                      self._detail(FIXTURES["no_variation"](), "resp_variation*"))

    def test_resp_variation_still_blocks_the_gate_either_way(self):
        for fixture in ("nonnumeric_resp", "no_variation"):
            with self.subTest(fixture=fixture):
                report = validate_frame(FIXTURES[fixture](), profile="upload")
                self.assertIn("resp_variation*",
                              [f.check for f in report.errors])

    # item 7 -- a trailing space is not a second construct
    def test_prefix_grouping_trims_whitespace(self):
        # F246's shape: "question " and "question" are one 35-label group
        items = [f"question {i}" for i in range(1, 6)] + \
                [f"question{i}" for i in range(6, 11)] + \
                [f"scale_{i}" for i in range(1, 4)]
        df = F(id=list(range(1, len(items) + 1)), item=items,
               resp=list(range(1, len(items) + 1)))
        detail = self._detail(df, "multi_scale*")
        self.assertIn("2 repeated prefixes", detail)
        self.assertNotIn("'question '", detail)


class ExitCodes(unittest.TestCase):
    def test_exit_code_contract(self):
        clean = validate_frame(FIXTURES["clean"](), profile="upload")
        broken = validate_frame(FIXTURES["no_variation"](), profile="upload")
        self.assertEqual(exit_code([clean]), 0)
        self.assertEqual(exit_code([clean, broken]), 1)

    def test_size_downgrade_is_recorded_not_silent(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "big_2024_scale.csv"
            path.write_text("id,item,resp\n1,a,1\n")
            report = validate_file(path, max_bytes=1)
            self.assertIn("size_downgrade", [f.check for f in report.findings])


if __name__ == "__main__":
    unittest.main()
