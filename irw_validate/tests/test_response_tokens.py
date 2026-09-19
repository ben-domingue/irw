"""File-boundary regressions for #2029; no live data or credentials."""
import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from irw_validate import validate_file, validate_frame
from irw_validate.cli import main
from irw_validate._checks import run_qc


class ResponseTokens(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, values, suffix=".csv", delimiter=",", extra=False):
        path = Path(self.tmp.name) / ("responses_2026_test" + suffix)
        with path.open("w", newline="") as fh:
            writer = csv.writer(fh, delimiter=delimiter)
            writer.writerow(["id", "item", "resp"] + (["cov_age"] if extra else []))
            for i, value in enumerate(values):
                writer.writerow([i, "q1", value] + (["NA"] if extra else []))
        return path

    def numeric_errors(self, report):
        return [f for f in report.errors if f.check == "resp_numeric"]

    def test_literal_missing_tokens_survive_csv_read(self):
        for profile in ("upload", "legacy"):
            for token in ("NA", "N/A", "NULL", "NaN", "nan", "None", "<NA>", " NA "):
                with self.subTest(profile=profile, token=token):
                    report = validate_file(self.write([0, 1, token, 0, 1]), profile=profile)
                    findings = self.numeric_errors(report)
                    self.assertEqual(len(findings), 1)
                    self.assertIn(repr(token), findings[0].message)
                    self.assertNotIn("resp_na", [f.check for f in report.findings])

    def test_one_bad_value_below_one_percent_still_blocks(self):
        for token in ("NA", "Quase nunca"):
            with self.subTest(token=token):
                report = validate_file(self.write([0, 1] * 100 + [token]))
                self.assertEqual(len(self.numeric_errors(report)), 1)
                self.assertIn("1 non-numeric", self.numeric_errors(report)[0].message)

    def test_empty_cells_remain_missing_not_invalid(self):
        report = validate_file(self.write([0, 1, "", None, 0, 1]))
        self.assertFalse(self.numeric_errors(report))
        self.assertTrue(report.ok)
        self.assertIn("resp_na", [f.check for f in report.warnings])
        self.assertEqual(report.stats["n_responses"], 4)

    def test_whitespace_is_literal_text_not_an_empty_cell(self):
        report = validate_file(self.write([0, 1, "   "]))
        self.assertEqual(len(self.numeric_errors(report)), 1)
        self.assertIn(repr("   "), self.numeric_errors(report)[0].message)

    def test_all_empty_still_fails_missing_response_check(self):
        report = validate_file(self.write(["", ""]))
        self.assertIn("resp_na", [f.check for f in report.errors])
        self.assertFalse(self.numeric_errors(report))

    def test_delimited_inputs_and_no_file_mutation(self):
        for suffix, delimiter in ((".csv", ","), (".tsv", "\t"), (".txt", ";")):
            with self.subTest(suffix=suffix):
                path = self.write([0, 1, "NA"], suffix, delimiter)
                before = path.read_bytes()
                self.assertTrue(self.numeric_errors(validate_file(path)))
                self.assertEqual(path.read_bytes(), before)

    def test_numeric_notation_is_inferred_without_false_dtype_error(self):
        report = validate_file(self.write(["0", "1", "-2", "0.5", "1e2", " 3 ", ""]))
        self.assertTrue(report.ok, report.findings)
        self.assertNotIn("resp_dtype", [f.check for f in report.findings])

    def test_other_columns_keep_existing_missing_value_semantics(self):
        path = self.write([0, 1, "NA"], extra=True)
        with patch("irw_validate.core.validate_frame") as validate:
            validate_file(path)
            frame = validate.call_args.args[0]
        self.assertTrue(frame["cov_age"].isna().all())
        self.assertEqual(frame["resp"].iloc[2], "NA")

    def test_in_memory_tokens_are_rejected_without_mutation(self):
        frame = pd.DataFrame({"id": range(202), "item": ["q1"] * 202,
                              "resp": [0, 1] * 100 + [None, "NA"]})
        original = frame.copy(deep=True)
        for profile in ("upload", "legacy"):
            self.assertEqual(len(self.numeric_errors(validate_frame(frame, profile=profile))), 1)
        pd.testing.assert_frame_equal(frame, original)

    def test_nullable_numeric_frame_and_typed_strings_keep_their_meaning(self):
        frame = pd.DataFrame({"id": [1, 2, 3], "item": ["a"] * 3,
                              "resp": pd.Series([0, 1, None], dtype="Int64")})
        self.assertFalse(self.numeric_errors(validate_frame(frame)))
        frame["resp"] = ["0", "1", "2"]
        self.assertIn("resp_dtype", [f.check for f in validate_frame(frame).errors])

    def test_invalid_text_on_a_separate_item_does_not_crash_range_check(self):
        frame = pd.DataFrame({"id": [1, 2, 3, 4], "item": ["a", "b", "c", "d"],
                              "resp": [0, 1, 2, "NA"]})
        self.assertEqual(len(self.numeric_errors(validate_frame(frame))), 1)

    def test_triage_and_core_keep_compatibility(self):
        path = self.write([0, 1, "NA", 0, 1])
        for profile in ("triage", "core"):
            expected = validate_frame(pd.read_csv(path), label=str(path), profile=profile)
            self.assertEqual(validate_file(path, profile=profile).to_dict(), expected.to_dict())
        frame = pd.DataFrame({"id": range(201), "item": ["q1"] * 201,
                              "resp": [0, 1] * 100 + ["NA"]})
        self.assertEqual(next(c.status for c in run_qc(frame) if c.name == "resp_numeric"), "pass")

    def test_item_text_option_keys_are_not_response_data(self):
        path = Path(self.tmp.name) / "responses_2026_test__items.csv"
        path.write_text("table,item,item_text,resp,option_text\n"
                        "responses_2026_test,q1,An item,NA,Not applicable\n")
        report = validate_file(path)
        self.assertTrue(report.ok, report.findings)
        self.assertNotIn("resp_numeric", report.checks_run)

    def test_cli_json_blocks_literal_token_and_accepts_empty_cell(self):
        for value, expected_code in (("NA", 1), ("", 0)):
            with self.subTest(value=value):
                path = self.write([0, 1, value, 0, 1])
                output = io.StringIO()
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                    code = main([str(path), "--json"])
                self.assertEqual(code, expected_code)
                reports = json.loads(output.getvalue())
                self.assertEqual(reports[0]["ok"], expected_code == 0)

    def test_uploader_validation_seam_receives_blocking_finding(self):
        # Call only the local validation seam, never the uploader/network.
        from red_up.checks import run_validator
        errors, _ = run_validator(self.write([0, 1, "NA"]))
        self.assertTrue(any("resp_numeric" in e and "'NA'" in e for e in errors))
        errors, _ = run_validator(self.write([0, 1, ""]))
        self.assertFalse(errors)


if __name__ == "__main__":
    unittest.main()
