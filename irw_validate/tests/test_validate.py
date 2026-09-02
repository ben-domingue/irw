"""Tests for irw_validate. Offline, stdlib unittest, no network, no credentials
-- the pattern red_up/tests/test_red_up.py established.

The first class is the important one. Fifty scripts in `data/` call `run_qc` and
read `.name` / `.status` / `.detail` off the result, and `run_qc` had no test
coverage at all before this file. GOLDEN pins the exact emission order and
status of every check for eight fixtures, so the move out of
`irw_triage_updated.py` is provably behaviour-preserving rather than hopefully
so.
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

#: Captured from `irw_triage_updated.run_qc` on 2026-09-02, BEFORE the move.
GOLDEN = {
    "clean": [("required_columns", "pass"), ("resp_numeric", "pass"),
              ("dup_id_item", "pass")],
    "missing_col": [("required_columns", "fail")],
    "all_na_resp": [("required_columns", "pass"), ("resp_na", "fail"),
                    ("resp_numeric", "fail"), ("dup_id_item", "pass"),
                    ("resp_variation*", "fail"), ("density*", "warn")],
    "dup_id_item": [("required_columns", "pass"), ("resp_numeric", "pass"),
                    ("dup_id_item", "fail")],
    "dup_with_wave": [("required_columns", "pass"), ("resp_numeric", "pass"),
                      ("dup_id_item", "warn")],
    "nonnumeric_resp": [("required_columns", "pass"), ("resp_numeric", "fail"),
                        ("dup_id_item", "pass"), ("resp_variation*", "fail"),
                        ("resp_scale_mixed", "fail")],
    "no_variation": [("required_columns", "pass"), ("resp_numeric", "pass"),
                     ("dup_id_item", "pass"), ("resp_variation*", "fail"),
                     ("imputed_values*", "warn")],
    "unprefixed_cov": [("required_columns", "pass"), ("resp_numeric", "pass"),
                       ("dup_id_item", "pass"), ("cov_prefix", "warn"),
                       ("imputed_values*", "warn")],
}


class GoldenCompatibility(unittest.TestCase):
    """The fifty callers see exactly what they saw before the move."""

    def test_emission_order_and_status_unchanged(self):
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
        # resp_scale_mixed is `fail` in triage; cao_2026_cdss documents a real
        # table that trips it legitimately, so it must not block an upload.
        df = FIXTURES["nonnumeric_resp"]()
        upload = validate_frame(df, profile="upload")
        mixed = [f for f in upload.findings if f.check == "resp_scale_mixed"]
        self.assertEqual([f.severity for f in mixed], ["warn"])

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

    def test_missing_item_text_columns_block(self):
        df = pd.DataFrame({"id": [1], "item": ["a"], "resp": [1]})
        report = validate_frame(df, label="t_2024_scale__items.csv")
        self.assertIn("required_columns", [f.check for f in report.errors])
        self.assertIn("item text", report.errors[0].message)

    def test_the_name_cap_still_applies_to_item_text(self):
        report = validate_frame(self._items(), label=("x" * 41) + "__items.csv")
        self.assertIn("name_length", [f.check for f in report.errors])


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
