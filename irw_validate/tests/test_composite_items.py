"""Agreed #2314 item-5 contract: label matches are observations, not scores.

The #2369 policy makes all-match and subset findings warnings. Strict mode
still blocks warnings, and error-only overrides cannot waive them. Matching,
messages and independent blocking conditions retain their existing contracts.
"""
from __future__ import annotations

import contextlib
import csv
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from irw_validate import exit_code, validate_file, validate_frame
from irw_validate._checks import _looks_composite, run_qc
from irw_validate.cli import main
from irw_validate.compat import run_qc as compatible_run_qc


CHECK = "composite_items*"


def frame(labels):
    # 100 observed respondents, balanced ordinal responses, unique id/item
    # pairs for distinct labels. Avoid unrelated sample-size/scale failures.
    return pd.DataFrame([(person, label, (person + index) % 5)
                         for person in range(100)
                         for index, label in enumerate(labels)],
                        columns=["id", "item", "resp"])


def composite(checks):
    return [check for check in checks if check.name == CHECK]


class CompositeLabelContract(unittest.TestCase):
    def test_bare_markers_are_whole_stripped_case_insensitive_matches(self):
        for label in ("pre", "POST", "baseline", "followup", "follow-up",
                      "follow_up", "follow up", "  PrE  ", "\tFollow-Up\n"):
            with self.subTest(label=repr(label)):
                self.assertTrue(_looks_composite(label))

    def test_exactly_one_separator_and_one_or_two_letter_digit_suffixes(self):
        for label in ("pre-A", "post_F", "baseline-A1", "follow-up_F",
                      "pre_1", "post-12", "follow up a", "PRE_9z",
                      "pre-İ", "post_ı", "baseline-ſ", "pre_K"):
            with self.subTest(label=label):
                self.assertTrue(_looks_composite(label))

    def test_ordinary_words_item_numbers_and_malformed_suffixes_do_not_match(self):
        for label in ("poster", "preen", "preto", "Pre63", "PRE1",
                      "pre-", "post_", "pre_anxiety_3", "pre_ABC", "post-123",
                      "pre--A", "post__F", "pre-_A", "pre  A", "pre- A",
                      "pre/A", "pre.A", "pre\tA", "pre-α", "prefix pre-A",
                      "pre-A extra", "q_pre_A", "pre-A\nq1", "", "   "):
            with self.subTest(label=repr(label)):
                self.assertFalse(_looks_composite(label))

    def test_score_word_tokens_remain_lexical_matches_including_sentences(self):
        for label in ("total_a", "SCORE_1", "subscales", "overall_rating",
                      "What does that mean?__ça", "Calculate the sum of these.",
                      "pre_mean", "pre_anxiety_score"):
            with self.subTest(label=label):
                self.assertTrue(_looks_composite(label))
        for label in ("meaning_1", "scoreboard_2", "summary", "preschool", "q1"):
            with self.subTest(label=label):
                self.assertFalse(_looks_composite(label))


class CompositeRawChecks(unittest.TestCase):
    def assert_observation_only(self, message, count):
        self.assertIn(count, message)
        self.assertIn("item labels", message)
        self.assertIn("naming pattern", message.replace("naming-pattern", "naming pattern"))
        self.assertIn("alone do not establish", message)
        self.assertIn("computed scores", message)
        self.assertNotIn("name computed scores", message)
        self.assertNotIn("names a computed score", message)
        self.assertNotIn("summary/aggregate table", message)
        self.assertNotIn("drop", message.lower())

    def test_all_subset_and_no_match_statuses_across_raw_compatibility_entrypoints(self):
        cases = ((["pre-A", "post_F"], "warn"),
                 (["PRE1", "pre-A"], "warn"),
                 (["PRE1", "poster"], None),
                 (["q1", "q2"], None),
                 (["pre-A"], "warn"))
        for check_function in (run_qc, compatible_run_qc):
            for labels, status in cases:
                with self.subTest(entry=check_function.__module__, labels=labels):
                    findings = composite(check_function(frame(labels)))
                    self.assertEqual([finding.status for finding in findings],
                                     [] if status is None else [status])

    def test_both_messages_describe_matches_without_claiming_computed_scores(self):
        for labels, count in ((["pre-A", "post_F"], "2/2"),
                              (["What does that mean?__ça", "q1"], "1/2")):
            with self.subTest(labels=labels):
                finding, = composite(run_qc(frame(labels)))
                self.assert_observation_only(finding.detail, count)
                self.assertIn(labels[0], finding.detail)

    def test_counts_use_distinct_original_labels_not_rows_or_stripped_labels(self):
        data = frame([" pre-A ", "pre-A", "q1"])
        # Repeated response rows do not change the count of label names.
        data = pd.concat([data, data.iloc[[0, 1]]], ignore_index=True)
        finding, = composite(run_qc(data))
        self.assert_observation_only(finding.detail, "2/3")
        self.assertIn(repr(" pre-A "), finding.detail)
        self.assertIn(repr("pre-A"), finding.detail)

    def test_examples_preserve_first_four_matching_labels_and_order(self):
        labels = ["q1", "post_F", "total_a", "pre-A", "mean_b", "baseline-5"]
        finding, = composite(run_qc(frame(labels)))
        self.assert_observation_only(finding.detail, "5/6")
        positions = [finding.detail.index(repr(label)) for label in labels[1:5]]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn(repr(labels[5]), finding.detail)

    def test_blank_labels_excluded_but_null_label_counting_is_unchanged(self):
        # The existing selector filters by str(label).strip(), not dropna().
        # This preserves its denominator; item_na separately reports the null.
        data = frame([None, "", "   ", "pre-A"])
        findings = run_qc(data)
        finding, = composite(findings)
        self.assert_observation_only(finding.detail, "1/2")
        self.assertIn("item_na", [check.name for check in findings])
        self.assertEqual(composite(run_qc(frame(["", "   "]))), [])
        self.assertEqual(composite(run_qc(frame([]))), [])

    def test_checks_and_profiles_do_not_mutate_original_labels_or_input(self):
        data = frame([" PRE-A ", "poster", "What does that mean?__ça"])
        data.index = [index // 2 for index in range(len(data))]
        original = data.copy(deep=True)
        run_qc(data)
        for profile in ("core", "triage", "upload", "legacy"):
            validate_frame(data, profile=profile)
            pd.testing.assert_frame_equal(data, original)

    def test_raw_failure_assertions_keep_independent_failures(self):
        clean = frame(["pre-A", "post_F"])
        duplicate = pd.concat([clean, clean.iloc[[0]]], ignore_index=True)
        constant = clean.assign(resp=1)
        for data, expected_failure in ((clean, None),
                                       (duplicate, "dup_id_item"),
                                       (constant, "resp_variation*")):
            for check_function in (run_qc, compatible_run_qc):
                with self.subTest(failure=expected_failure, entry=check_function.__module__):
                    checks = check_function(data)
                    self.assertEqual([c.status for c in composite(checks)], ["warn"])
                    # The aggregate condition used by conversion scripts must
                    # relax only the composite finding, not another failure.
                    failures = [c.name for c in checks if c.status == "fail"]
                    if expected_failure is None:
                        self.assertEqual(failures, [])
                    else:
                        self.assertIn(expected_failure, failures)
                    self.assertNotIn(CHECK, failures)


class CompositeProfilesAndFiles(unittest.TestCase):
    def test_all_match_warns_in_triage_and_gate_profiles_but_still_blocks_strict(self):
        for profile, severity, normal_code, strict_code in (
                ("core", None, 0, 0), ("triage", "warn", 0, 1),
                ("upload", "warn", 0, 1), ("legacy", "warn", 0, 1)):
            with self.subTest(profile=profile):
                report = validate_frame(frame(["pre-A", "post_F"]), profile=profile)
                findings = [finding for finding in report.findings if finding.check == CHECK]
                self.assertEqual([finding.severity for finding in findings],
                                 [] if severity is None else [severity])
                self.assertEqual(exit_code([report]), normal_code)
                self.assertEqual(exit_code([report], strict=True), strict_code)

    def test_narrowing_retains_subset_warning_or_removes_finding(self):
        for labels, has_match in ((["PRE1", "pre-A"], True),
                                  (["PRE1", "poster"], False)):
            for profile in ("core", "triage", "upload", "legacy"):
                with self.subTest(labels=labels, profile=profile):
                    report = validate_frame(frame(labels), profile=profile)
                    expected = ["warn"] if has_match and profile != "core" else []
                    self.assertEqual([finding.severity for finding in report.findings
                                      if finding.check == CHECK], expected)
                    self.assertTrue(report.ok, report.findings)

    def test_file_api_and_cli_retain_profile_policy_and_source_bytes(self):
        cases = ((["pre-A", "post_F"], "all"),
                 (["PRE1", "pre-A"], "subset"),
                 (["PRE1", "poster"], "none"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "naming_2026_scale.csv"
            for labels, kind in cases:
                with path.open("w", newline="") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(["id", "item", "resp"])
                    writer.writerows(frame(labels).itertuples(index=False, name=None))
                original = path.read_bytes()
                for profile in ("core", "triage", "upload", "legacy"):
                    expected_severity = (
                        None if profile == "core" or kind == "none" else
                        "warn")
                    with self.subTest(kind=kind, profile=profile):
                        report = validate_file(path, profile=profile)
                        self.assertEqual([finding.severity for finding in report.findings
                                          if finding.check == CHECK],
                                         [] if expected_severity is None else [expected_severity])
                    for strict in (False, True):
                        with self.subTest(kind=kind, profile=profile, strict=strict):
                            arguments = [str(path), "--profile", profile, "--json"]
                            if strict:
                                arguments.append("--strict")
                            output = io.StringIO()
                            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                                code = main(arguments)
                            expected_code = int(expected_severity == "error" or
                                                (strict and expected_severity == "warn"))
                            self.assertEqual(code, expected_code)
                            returned, = json.loads(output.getvalue())
                            findings = [finding for finding in returned["findings"]
                                        if finding["check"] == CHECK]
                            self.assertEqual([finding["severity"] for finding in findings],
                                             [] if expected_severity is None else [expected_severity])
                            self.assertEqual(path.read_bytes(), original)

    def test_scoped_override_cannot_waive_the_all_match_warning_in_strict_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "naming_2026_scale.csv"
            ledger = Path(directory) / "ledger.csv"
            frame(["pre-A", "post_F"]).to_csv(path, index=False)
            original = path.read_bytes()
            reason = "Synthetic naming evidence only; no data provenance claim."
            for strict in (False, True):
                with self.subTest(strict=strict):
                    arguments = [str(path), "--profile", "triage", "--json",
                                 "--override-check", CHECK, "--override", reason]
                    if strict:
                        arguments.append("--strict")
                    output = io.StringIO()
                    with patch.dict(os.environ, {"IRW_VALIDATE_LEDGER": str(ledger)}), \
                            contextlib.redirect_stdout(output), \
                            contextlib.redirect_stderr(io.StringIO()):
                        code = main(arguments)
                    report, = json.loads(output.getvalue())
                    self.assertEqual(code, int(strict))
                    self.assertTrue(report["ok"])
                    self.assertEqual([(f["check"], f["severity"])
                                      for f in report["findings"]], [(CHECK, "warn")])
                    self.assertEqual(report["overridden"], [])
                    self.assertIsNone(report["override_reason"])
                    self.assertFalse(ledger.exists(), "A warning must not create a waiver row")
                    self.assertEqual(path.read_bytes(), original)

    def test_scoped_override_preserves_other_errors_and_only_records_actual_error_waivers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "naming_2026_scale.csv"
            data = frame(["pre-A", "post_F"])
            data["resp"] = data["resp"].astype(object)
            data.loc[0:5, "resp"] = "invalid"
            data.to_csv(path, index=False)
            original = path.read_bytes()
            reason = "Synthetic caller test: explicitly waive only this numeric error."
            for target in (CHECK, "resp_numeric"):
                for strict in (False, True):
                    with self.subTest(target=target, strict=strict):
                        ledger = Path(directory) / f"ledger_{int(target == CHECK)}_{int(strict)}.csv"
                        arguments = [str(path), "--profile", "triage", "--json",
                                     "--override-check", target, "--override", reason]
                        if strict:
                            arguments.append("--strict")
                        output = io.StringIO()
                        with patch.dict(os.environ, {"IRW_VALIDATE_LEDGER": str(ledger)}), \
                                contextlib.redirect_stdout(output), \
                                contextlib.redirect_stderr(io.StringIO()):
                            code = main(arguments)
                        report, = json.loads(output.getvalue())
                        self.assertEqual(code, int(target == CHECK or strict))
                        self.assertIn((CHECK, "warn"),
                                      [(f["check"], f["severity"]) for f in report["findings"]])
                        if target == CHECK:
                            self.assertFalse(report["ok"])
                            self.assertIn("resp_numeric", [f["check"] for f in report["findings"]
                                                            if f["severity"] == "error"])
                            self.assertEqual(report["overridden"], [])
                            self.assertFalse(ledger.exists())
                        else:
                            self.assertTrue(report["ok"])
                            self.assertEqual([(f["check"], f["severity"])
                                              for f in report["overridden"]],
                                             [("resp_numeric", "error")])
                            with ledger.open(newline="") as handle:
                                rows = list(csv.DictReader(handle))
                            self.assertEqual(len(rows), 1)
                            self.assertEqual(rows[0]["checks"], "resp_numeric")
                            self.assertEqual(rows[0]["reason"], reason)
                        self.assertEqual(path.read_bytes(), original)

    def test_csv_blank_item_parsing_retains_loader_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "naming_2026_scale.csv"
            frame(["pre-A", ""]).to_csv(path, index=False)
            original = path.read_bytes()
            for profile in ("triage", "upload", "legacy"):
                with self.subTest(profile=profile):
                    report = validate_file(path, profile=profile)
                    finding, = [finding for finding in report.findings if finding.check == CHECK]
                    self.assertEqual(finding.severity, "warn")
                    self.assertIn("1/2", finding.message)
                    self.assertIn("item_na", [finding.check for finding in report.warnings])
                    self.assertEqual(path.read_bytes(), original)


class CompositeDiscoveryRoutes(unittest.TestCase):
    def triage(self, labels, invalid=False):
        from automated_finding.irw_triage_updated import triage_dataset

        data = frame(labels)
        if invalid:
            data["resp"] = data["resp"].astype(object)
            data.loc[0:5, "resp"] = "invalid"
        original = data.copy(deep=True)
        result = triage_dataset(data)
        self.assertEqual(result.coercion.method, "already-long")
        self.assertEqual(result.metadata["n_participants"], 100)
        pd.testing.assert_frame_equal(data, original)
        return result

    def test_all_match_routes_good_with_warning_when_no_other_condition_blocks(self):
        result = self.triage(["pre-A", "post_F"])
        self.assertEqual(result.flag, "good", result.reasons)
        self.assertEqual([finding.status for finding in composite(result.checks)], ["warn"])
        self.assertTrue(any(CHECK in reason for reason in result.reasons))

    def test_all_match_warning_does_not_hide_independent_numeric_failure(self):
        result = self.triage(["pre-A", "post_F"], invalid=True)
        self.assertEqual(result.flag, "human_assistance", result.reasons)
        self.assertEqual([finding.status for finding in composite(result.checks)], ["warn"])
        self.assertIn("resp_numeric", [c.name for c in result.checks if c.status == "fail"])
        self.assertTrue(any("QC failed on: resp_numeric" in reason for reason in result.reasons))

    def test_real_low_confidence_coercion_retriages_only_warning_cases_as_worth_retrying(self):
        from automated_finding.irw_triage_updated import triage_dataset

        pipeline = str(Path(__file__).resolve().parents[2] / "automated_finding")
        with patch.object(sys, "path", [pipeline, *sys.path]):
            from irw_retriage_ha import classify

        for constant, expected in ((False, "worth_retrying"), (True, "human_review")):
            with self.subTest(constant=constant):
                # No identifier column and <50% unique responses: the real
                # coercer must synthesize row ids and mark the mapping low.
                data = pd.DataFrame({
                    "pre-A": [1 if constant else person % 5 for person in range(100)],
                    "post_F": [1 if constant else (person + 1) % 5 for person in range(100)],
                })
                original = data.copy(deep=True)
                result = triage_dataset(data)
                self.assertEqual(result.coercion.method, "wide-to-long")
                self.assertEqual(result.coercion.confidence, "low")
                self.assertEqual(result.metadata["n_participants"], 100)
                self.assertEqual(result.flag, "human_assistance", result.reasons)
                self.assertEqual([c.status for c in composite(result.checks)], ["warn"])
                failures = [c.name for c in result.checks if c.status == "fail"]
                if constant:
                    self.assertIn("resp_variation*", failures)
                else:
                    self.assertEqual(failures, [])
                row = pd.Series({"title": "Synthetic response matrix",
                                 "reasons": " | ".join(result.reasons), **result.metadata})
                saved_row = row.copy(deep=True)
                self.assertEqual(classify(row)[0], expected)
                pd.testing.assert_series_equal(row, saved_row)
                pd.testing.assert_frame_equal(data, original)

    def test_numbered_label_with_retained_marker_routes_good_with_subset_warning(self):
        result = self.triage(["PRE1", "pre-A"])
        self.assertEqual(result.flag, "good", result.reasons)
        self.assertEqual([finding.status for finding in composite(result.checks)], ["warn"])
        self.assertTrue(any(CHECK in reason for reason in result.reasons))

    def test_only_former_overmatches_route_good_without_composite_finding(self):
        result = self.triage(["PRE1", "poster"])
        self.assertEqual(result.flag, "good", result.reasons)
        self.assertEqual(composite(result.checks), [])
        self.assertFalse(any(CHECK in reason for reason in result.reasons))

    def test_removed_composite_finding_does_not_hide_independent_numeric_failure(self):
        result = self.triage(["PRE1", "poster"], invalid=True)
        self.assertEqual(result.flag, "human_assistance", result.reasons)
        self.assertEqual(composite(result.checks), [])
        self.assertIn("resp_numeric", [check.name for check in result.checks if check.status == "fail"])
        self.assertTrue(any("resp_numeric" in reason for reason in result.reasons))


if __name__ == "__main__":
    unittest.main()
