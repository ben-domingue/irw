"""#2314 item 2: numeric parsing and missingness are separate judgments.

Exercise the shared check, its compatibility surface, profile loaders, CLI,
and the real discovery caller. No live corpus, network, or altered gate policy.
"""
from __future__ import annotations

import contextlib
import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from irw_validate import validate_file, validate_frame
from irw_validate._checks import run_qc
from irw_validate.cli import main
from irw_validate.compat import run_qc as compatible_run_qc


def frame(values):
    return pd.DataFrame({"id": range(len(values)), "item": ["q1"] * len(values),
                         "resp": values})


def checks_by_name(checks):
    return {check.name: check for check in checks}


class SharedNumericCheck(unittest.TestCase):
    def test_true_missing_values_do_not_dilute_numeric_fraction(self):
        data = frame(pd.Series([0, "1", "2.5", None, float("nan"), pd.NA], dtype=object))
        original = data.copy(deep=True)
        for check_function in (run_qc, compatible_run_qc):
            with self.subTest(entry=check_function.__module__):
                results = checks_by_name(check_function(data))
                self.assertEqual(results["resp_numeric"].status, "pass")
                self.assertEqual(results["resp_na"].status, "warn")
                pd.testing.assert_frame_equal(data, original)

    def test_nullable_numeric_series_preserve_dtype_and_missingness(self):
        for dtype in ("Int64", "Float64"):
            with self.subTest(dtype=dtype):
                data = frame(pd.Series([0, 1, None, 2], dtype=dtype))
                original = data.copy(deep=True)
                results = checks_by_name(run_qc(data))
                self.assertEqual(results["resp_numeric"].status, "pass")
                self.assertEqual(results["resp_na"].status, "warn")
                pd.testing.assert_frame_equal(data, original)

    def test_empty_and_all_missing_have_no_numeric_failure_but_still_fail_missingness(self):
        for values in ([], [None, None], pd.Series([pd.NA, pd.NA], dtype="Int64")):
            with self.subTest(values=repr(values)):
                results = checks_by_name(run_qc(frame(values)))
                numeric = results["resp_numeric"]
                self.assertEqual(numeric.status, "pass")
                self.assertIn("No non-missing", numeric.detail)
                self.assertIn("resp_na", numeric.detail)
                self.assertEqual(results["resp_na"].status, "fail")

    def test_present_text_is_invalid_and_message_uses_present_denominator(self):
        for token in ("NA", "word", " "):
            with self.subTest(token=repr(token)):
                results = checks_by_name(run_qc(frame([0, 1, token, None, None])))
                numeric = results["resp_numeric"]
                self.assertEqual(numeric.status, "fail")
                self.assertIn("2/3", numeric.detail)
                self.assertIn("non-missing", numeric.detail)
                self.assertIn("67%", numeric.detail)
                self.assertEqual(results["resp_na"].status, "warn")

    def test_exactly_ninety_nine_percent_of_present_values_still_passes(self):
        for missing in (0, 30):
            with self.subTest(missing=missing):
                data = frame([0, 1, 2] * 33 + ["NA"] + [None] * missing)
                self.assertEqual(checks_by_name(run_qc(data))["resp_numeric"].status, "pass")

    def test_below_ninety_nine_percent_of_present_values_still_fails(self):
        data = frame([0, 1, 2] * 33 + ["bad", "NA"] + [None] * 30)
        numeric = checks_by_name(run_qc(data))["resp_numeric"]
        self.assertEqual(numeric.status, "fail")
        self.assertIn("99/101", numeric.detail)


class NumericProfiles(unittest.TestCase):
    def test_core_and_triage_keep_missing_warning_without_numeric_error(self):
        data = frame([0, 1, None, 2])
        for profile in ("core", "triage"):
            with self.subTest(profile=profile):
                report = validate_frame(data, profile=profile)
                self.assertTrue(report.ok, report.findings)
                self.assertIn("resp_numeric", report.checks_run)
                self.assertNotIn("resp_numeric", [f.check for f in report.findings])
                self.assertEqual([(f.check, f.severity) for f in report.findings],
                                 [("resp_na", "warn")])

    def test_no_present_values_do_not_become_a_valid_table(self):
        for profile in ("core", "triage", "upload", "legacy"):
            with self.subTest(profile=profile):
                report = validate_frame(frame([None, None]), profile=profile)
                self.assertFalse(report.ok)
                self.assertIn("resp_na", [f.check for f in report.errors])
                self.assertNotIn("resp_numeric", [f.check for f in report.findings])

    def test_core_and_triage_report_present_text_as_error(self):
        for profile in ("core", "triage"):
            with self.subTest(profile=profile):
                report = validate_frame(frame([0, 1, "NA", None]), profile=profile)
                self.assertIn("resp_numeric", [f.check for f in report.errors])
                self.assertIn("resp_na", [f.check for f in report.warnings])

    def test_gate_profiles_still_reject_one_percent_invalid_present_values(self):
        data = frame([0, 1, 2] * 33 + ["NA"] + [None] * 30)
        original = data.copy(deep=True)
        for profile in ("core", "triage", "upload", "legacy"):
            with self.subTest(profile=profile):
                report = validate_frame(data, profile=profile)
                numeric = [f for f in report.findings if f.check == "resp_numeric"]
                if profile in ("upload", "legacy"):
                    self.assertEqual(len(numeric), 1)
                    self.assertEqual(numeric[0].severity, "error")
                    self.assertIn("1 non-numeric", numeric[0].message)
                    self.assertIn("100 non-missing", numeric[0].message)
                    self.assertIn("'NA'", numeric[0].message)
                else:
                    self.assertEqual(numeric, [])
                pd.testing.assert_frame_equal(data, original)


class NumericFileAndCLI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def write(self, values):
        path = Path(self.temp.name) / "numeric_2026_test.csv"
        with path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["id", "item", "resp"])
            writer.writerows((i, "q1", value) for i, value in enumerate(values))
        return path

    def cli(self, path, profile, strict=False):
        output = io.StringIO()
        arguments = [str(path), "--profile", profile, "--json"]
        if strict:
            arguments.append("--strict")
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
            code = main(arguments)
        return code, json.loads(output.getvalue())[0]

    def test_file_token_parsing_remains_profile_specific(self):
        path = self.write([0, 1, "NA", 2, 0])
        original = path.read_bytes()
        for profile in ("core", "triage", "upload", "legacy"):
            with self.subTest(profile=profile):
                report = validate_file(path, profile=profile)
                if profile in ("core", "triage"):
                    self.assertTrue(report.ok, report.findings)
                    self.assertIn("resp_na", [f.check for f in report.warnings])
                    self.assertNotIn("resp_numeric", [f.check for f in report.findings])
                    self.assertEqual(report.stats["n_responses"], 4)
                else:
                    self.assertIn("resp_numeric", [f.check for f in report.errors])
                    self.assertNotIn("resp_na", [f.check for f in report.findings])
                    self.assertEqual(report.stats["n_responses"], 5)
                self.assertEqual(path.read_bytes(), original)

    def test_cli_preserves_loader_distinction_and_exit_codes(self):
        path = self.write([0, 1, "NA", 2, 0])
        for profile, expected in (("triage", 0), ("core", 0), ("upload", 1), ("legacy", 1)):
            with self.subTest(profile=profile):
                code, report = self.cli(path, profile)
                self.assertEqual(code, expected)
                self.assertEqual(report["ok"], expected == 0)
                numeric = [f for f in report["findings"] if f["check"] == "resp_numeric"]
                self.assertEqual(len(numeric), expected)

    def test_strict_cli_still_blocks_missing_warning(self):
        path = self.write([0, 1, "", 2, 0])
        code, report = self.cli(path, "triage", strict=True)
        self.assertEqual(code, 1)
        self.assertTrue(report["ok"], "Only warnings: strict mode supplies the failure")
        self.assertEqual([(f["check"], f["severity"]) for f in report["findings"]],
                         [("resp_na", "warn")])


class DiscoveryTriageCaller(unittest.TestCase):
    @staticmethod
    def candidate():
        # Balanced ordinal data avoids unrelated concentration/range warnings.
        # Already-long input exercises the real coercion and all routing gates.
        data = pd.DataFrame([(i, f"q{j}", (i + j) % 5)
                             for i in range(100) for j in range(1, 4)],
                            columns=["id", "item", "resp"])
        data["resp"] = data["resp"].astype(object)
        data.loc[data.index[::10], "resp"] = None
        return data

    def test_partial_missing_candidate_routes_good_with_missing_warning(self):
        from automated_finding.irw_triage_updated import triage_dataset

        data = self.candidate()
        original = data.copy(deep=True)
        result = triage_dataset(data)
        self.assertEqual(result.coercion.method, "already-long")
        self.assertEqual(result.flag, "good", result.reasons)
        checks = checks_by_name(result.checks)
        self.assertEqual(checks["resp_numeric"].status, "pass")
        self.assertEqual(checks["resp_na"].status, "warn")
        self.assertEqual(result.metadata["n_participants"], 100)
        self.assertEqual(result.metadata["n_responses"], 270)
        self.assertTrue(any("resp_na" in reason for reason in result.reasons))
        pd.testing.assert_frame_equal(data, original)

    def test_nonnumeric_candidate_still_routes_for_human_assistance(self):
        from automated_finding.irw_triage_updated import triage_dataset

        data = self.candidate()
        data.loc[1:6, "resp"] = "bad"
        original = data.copy(deep=True)
        result = triage_dataset(data)
        self.assertEqual(result.flag, "human_assistance", result.reasons)
        checks = checks_by_name(result.checks)
        self.assertEqual(checks["resp_numeric"].status, "fail")
        self.assertIn("264/270", checks["resp_numeric"].detail)
        self.assertTrue(any("QC failed on: resp_numeric" in reason for reason in result.reasons))
        pd.testing.assert_frame_equal(data, original)

    def test_all_missing_candidate_is_still_rejected_by_existing_sample_floor(self):
        from automated_finding.irw_triage_updated import triage_dataset

        data = self.candidate()
        data["resp"] = None
        original = data.copy(deep=True)
        result = triage_dataset(data)
        # Metadata counts respondents with observed responses. That existing
        # sample-size gate precedes QC routing; no numeric failure is needed.
        self.assertEqual(result.flag, "below_min_n", result.reasons)
        self.assertEqual(result.metadata["n_participants"], 0)
        self.assertEqual(result.metadata["n_responses"], 0)
        checks = checks_by_name(result.checks)
        self.assertEqual(checks["resp_na"].status, "fail")
        self.assertEqual(checks["resp_numeric"].status, "pass")
        pd.testing.assert_frame_equal(data, original)

    def test_retriage_low_confidence_rows_distinguish_missingness_from_numeric_failure(self):
        from automated_finding.irw_triage_updated import triage_dataset

        pipeline = str(Path(__file__).resolve().parents[2] / "automated_finding")
        with patch.object(sys, "path", [pipeline, *sys.path]):
            from irw_retriage_ha import classify

        for invalid, expected in ((False, "worth_retrying"), (True, "human_review")):
            with self.subTest(invalid=invalid):
                data = self.candidate()
                if invalid:
                    data.loc[1:6, "resp"] = "bad"
                result = triage_dataset(data)
                # A synthetic persisted-row seam: the classifier consumes
                # saved reasons. This is not a claim that today's coercer
                # assigns low confidence to this already-long fixture.
                reasons = result.reasons + ["Column mapping was a low-confidence guess."]
                row = pd.Series({"title": "Synthetic response matrix",
                                 "reasons": " | ".join(reasons),
                                 **result.metadata})
                original = row.copy(deep=True)
                self.assertEqual(classify(row)[0], expected)
                pd.testing.assert_series_equal(row, original)


if __name__ == "__main__":
    unittest.main()
