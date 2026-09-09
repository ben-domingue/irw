"""Response coding is not construct identity (PR #1697).

Offline synthetic fixtures make the evidence explicit: observed supports are
not codebooks, item prefixes are not construct declarations, and valid mixed
formats remain one table regardless of which format is more common.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from irw_validate import CORE_CHECKS, validate_file, validate_frame  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402
from irw_validate.compat import run_qc as compatible_run_qc  # noqa: E402


WIDTH_CHECKS = {
    "resp_scale_nested_support", "resp_scale_mixed", "item_scale_outlier",
}
EVIDENCE_CHECKS = {
    "permitted_values_unusable", "resp_outside_permitted",
    "item_constructs_unusable", "resp_scale_constructs",
}


def response_table(supports, *, disjoint=False, respondents=120):
    """Every declared synthetic category is observed; no inferred codebook."""
    rows = []
    for index, (item, values) in enumerate(supports.items()):
        values = list(values)
        for person in range(respondents):
            ident = index * respondents + person if disjoint else person
            rows.append((ident, item, values[person % len(values)]))
    return pd.DataFrame(rows, columns=["id", "item", "resp"])


def raw_findings(checks, names=WIDTH_CHECKS | EVIDENCE_CHECKS):
    return {check.name: check.status for check in checks
            if check.name in names and check.status != "pass"}


def report_findings(report, names=WIDTH_CHECKS | EVIDENCE_CHECKS):
    return {finding.check: finding.severity for finding in report.findings
            if finding.check in names}


def mixed_math(n_mc, n_cr):
    return {**{f"MC_{i:02d}": (0, 1) for i in range(n_mc)},
            **{f"CR_{i:02d}": (0, 1, 2, 3) for i in range(n_cr)}}


class WidthEvidence(unittest.TestCase):
    def test_majority_ties_and_order_do_not_fail_a_mixed_format_test(self):
        for n_mc, n_cr in ((20, 5), (5, 20), (5, 5)):
            supports = mixed_math(n_mc, n_cr)
            for reversed_items in (False, True):
                ordered = dict(reversed(list(supports.items()))) if reversed_items else supports
                df = response_table(ordered)
                if reversed_items:
                    df = df.iloc[::-1].reset_index(drop=True)
                with self.subTest(mc=n_mc, cr=n_cr, reverse=reversed_items):
                    self.assertEqual(raw_findings(run_qc(df)),
                                     {"resp_scale_nested_support": "warn"})
                    for profile in ("triage", "upload", "legacy"):
                        report = validate_frame(df, label="math_2026", profile=profile)
                        self.assertTrue(report.ok, report.findings)
                        self.assertEqual(report_findings(report),
                                         {"resp_scale_nested_support": "warn"})

    def test_floor_and_ceiling_nonuse_are_symmetric(self):
        for narrow, wide in (((2, 3, 4, 5), (1, 2, 3, 4, 5)),
                             ((1, 2, 3, 4), (1, 2, 3, 4, 5))):
            for narrow_count in (4, 8):
                supports = {f"i{i:02d}": narrow if i < narrow_count else wide
                            for i in range(12)}
                with self.subTest(narrow=narrow, count=narrow_count):
                    self.assertEqual(raw_findings(run_qc(response_table(supports))),
                                     {"resp_scale_nested_support": "warn"})

    def test_crossing_or_disjoint_ranges_are_only_width_warnings(self):
        for first, second in (((0, 1, 2, 3, 4), (1, 2, 3, 4, 5)),
                              ((0, 1), (3, 4, 5))):
            for first_count in (4, 8):
                supports = {f"i{i:02d}": first if i < first_count else second
                            for i in range(12)}
                with self.subTest(ranges=(first, second), count=first_count):
                    self.assertEqual(raw_findings(run_qc(response_table(supports))),
                                     {"resp_scale_mixed": "warn"})

    def test_an_isolated_crossing_item_is_an_outlier_not_a_failed_construct(self):
        supports = {f"i{i:02d}": (1, 2, 3, 4, 5) for i in range(9)}
        supports["odd_item"] = (0, 1, 2, 3, 4)
        self.assertEqual(raw_findings(run_qc(response_table(supports))),
                         {"item_scale_outlier": "warn"})

    def test_rare_nested_item_is_an_outlier_warning_not_a_failed_construct(self):
        supports = {f"i{i:02d}": (1, 2, 3, 4, 5) for i in range(9)}
        supports["one_wider"] = (0, 1, 2, 3, 4, 5)
        self.assertEqual(raw_findings(run_qc(response_table(supports))),
                         {"item_scale_outlier": "warn"})

    def test_hpq_shaped_count_column_is_named_before_nested_classification(self):
        # Synthetic regression for the reported shape, not a source-data replay.
        supports = {**{f"hpq_{i:02d}": range(1, 6) for i in range(12)},
                    "submiss": range(41)}
        for reverse in (False, True):
            ordered = dict(reversed(list(supports.items()))) if reverse else supports
            df = response_table(ordered)
            if reverse:
                df = df.iloc[::-1].reset_index(drop=True)
            for profile in ("triage", "upload", "legacy"):
                with self.subTest(reverse=reverse, profile=profile):
                    report = validate_frame(df, label="hpq_2026", profile=profile)
                    self.assertTrue(report.ok, report.findings)
                    self.assertEqual(report_findings(report), {"item_scale_outlier": "warn"})
                    finding = next(f for f in report.findings if f.check == "item_scale_outlier")
                    self.assertIn("'submiss' (0-40)", finding.message)

    def test_rare_legitimate_item_format_still_only_warns(self):
        for n_mc, n_cr in ((12, 1), (1, 12)):
            supports = mixed_math(n_mc, n_cr)
            df = response_table(supports)
            for profile in ("triage", "upload", "legacy"):
                with self.subTest(mc=n_mc, cr=n_cr, profile=profile):
                    report = validate_frame(df, label="math_2026", profile=profile)
                    self.assertTrue(report.ok, report.findings)
                    self.assertEqual(report_findings(report), {"item_scale_outlier": "warn"})
                    documented = validate_frame(df, profile=profile, context={
                        "permitted_values": supports,
                        "item_constructs": {item: "math" for item in supports},
                    })
                    self.assertTrue(documented.ok, documented.findings)
                    self.assertEqual(report_findings(documented), {})

    def test_isolated_share_boundary_is_strictly_below_fifteen_percent(self):
        for count, expected in ((2, "item_scale_outlier"), (3, "resp_scale_nested_support")):
            supports = {f"i{i:02d}": range(1, 8) if i < count else range(1, 6)
                        for i in range(20)}
            with self.subTest(off_count=count):
                self.assertEqual(raw_findings(run_qc(response_table(supports))),
                                 {expected: "warn"})

    def test_sdv_shaped_nested_ranges_remain_warning_without_construct_evidence(self):
        # Accepted tradeoff: widths alone cannot establish multiple constructs.
        supports = {f"i{end}_{i}": range(1, end + 1)
                    for end in (5, 7, 8, 9) for i in range(3)}
        for profile in ("triage", "upload", "legacy"):
            with self.subTest(profile=profile):
                report = validate_frame(response_table(supports), label="sdv_2026", profile=profile)
                self.assertTrue(report.ok, report.findings)
                self.assertEqual(report_findings(report), {"resp_scale_nested_support": "warn"})

    def test_prefixes_and_disjoint_respondents_are_not_construct_proof(self):
        # Each item has its own booklet sample, but all assess mathematics.
        df = response_table(mixed_math(8, 4), disjoint=True)
        for context in ({}, {"item_constructs": {item: "math" for item in df.item.unique()}}):
            with self.subTest(context=bool(context)):
                report = validate_frame(df, profile="triage", context=context)
                self.assertTrue(report.ok, report.findings)
                self.assertEqual(report_findings(report),
                                 {"resp_scale_nested_support": "warn"})

    def test_weighted_barthel_supports_do_not_fail_without_documentation(self):
        supports = {
            "feeding": (0, 5, 10), "bathing": (0, 5), "grooming": (0, 5),
            "dressing": (0, 5, 10), "bowels": (0, 5, 10), "bladder": (0, 5, 10),
            "toilet": (0, 5, 10), "transfers": (0, 5, 10, 15),
            "mobility": (0, 5, 10, 15), "stairs": (0, 5, 10),
        }
        df = response_table(supports)
        self.assertEqual(raw_findings(run_qc(df)),
                         {"resp_scale_nested_support": "warn"})
        self.assertEqual(raw_findings(run_qc(df, permitted_values=supports)), {})

    def test_uniform_observed_ranges_produce_no_width_finding(self):
        df = response_table({f"i{i}": range(1, 6) for i in range(4)})
        self.assertEqual(raw_findings(run_qc(df)), {})


class DocumentedResponses(unittest.TestCase):
    def test_complete_shared_documentation_settles_mspss_floor_nonuse(self):
        supports = {f"mspss_{i}": range(2, 8) if i <= 8 else range(1, 8)
                    for i in range(1, 13)}
        df = response_table(supports)
        self.assertEqual(raw_findings(run_qc(df)),
                         {"resp_scale_nested_support": "warn"})
        for permitted in (set(range(1, 8)), list(range(1, 8)),
                          {str(i) for i in range(1, 8)},
                          {item: set(range(1, 8)) for item in supports}):
            with self.subTest(kind=type(permitted).__name__):
                self.assertEqual(raw_findings(run_qc(df, permitted_values=permitted)), {})

    def test_different_documented_sets_are_legal_and_public_context_is_used(self):
        permitted = mixed_math(8, 4)
        df = response_table(permitted)
        context = {"permitted_values": permitted,
                   "item_constructs": {item: "math" for item in permitted}}
        for profile in ("triage", "upload", "legacy", "core"):
            with self.subTest(profile=profile):
                report = validate_frame(df, label="math_2026", profile=profile,
                                        context=context)
                self.assertTrue(report.ok, report.findings)
                self.assertEqual(report_findings(report), {})

    def test_documented_violation_is_caught_even_with_only_two_items(self):
        df = response_table({"bad_item": (0, 1, 9), "good_item": (0, 1, 2)})
        checks = run_qc(df, permitted_values={0, 1, 2, 3})
        self.assertEqual(raw_findings(checks).get("resp_outside_permitted"), "fail")
        detail = next(c.detail for c in checks if c.name == "resp_outside_permitted")
        self.assertIn("bad_item", detail)
        self.assertIn("9", detail)
        self.assertNotIn("good_item", detail)

    def test_per_item_membership_does_not_use_the_union_of_allowed_values(self):
        permitted = {"bathing": {0, 5}, "transfers": {0, 5, 10, 15}}
        df = response_table({"bathing": (0, 5, 15), "transfers": (0, 5, 10, 15)})
        checks = run_qc(df, permitted_values=permitted)
        detail = next(c.detail for c in checks if c.name == "resp_outside_permitted")
        self.assertIn("bathing", detail)
        self.assertIn("15", detail)
        self.assertNotIn("transfers", detail)

    def test_partial_documentation_still_checks_valid_available_items(self):
        df = response_table({"bad_item": (0, 1, 9), "undocumented": (0, 1)})
        for permitted in ({"bad_item": {0, 1}},
                          {"bad_item": {0, 1}, "undocumented": None},
                          {"bad_item": {0, 1}, "undocumented": {float("nan")}}):
            with self.subTest(permitted=permitted):
                got = raw_findings(run_qc(df, permitted_values=permitted))
                self.assertEqual(got.get("permitted_values_unusable"), "warn")
                self.assertEqual(got.get("resp_outside_permitted"), "fail")

    def test_malformed_sets_warn_and_do_not_silence_observed_heterogeneity(self):
        df = response_table(mixed_math(8, 4))
        for bad in (set(), "0-3", {"low", "high"}, {0, float("inf")},
                    {0, float("nan")}, {}, {"not_an_item": {0, 1}}):
            with self.subTest(bad=repr(bad)):
                got = raw_findings(run_qc(df, permitted_values=bad))
                self.assertEqual(got.get("permitted_values_unusable"), "warn")
                self.assertEqual(got.get("resp_scale_nested_support"), "warn")
                self.assertNotIn("resp_outside_permitted", got)
        self.assertNotIn("permitted_values_unusable", raw_findings(run_qc(df)))

    def test_documentation_keys_must_match_original_item_ids(self):
        df = response_table({1: (0, 1), 2: (0, 1, 2, 3), 3: (0, 1)})
        wrong_keys = {"1": {0, 1}, "2": {0, 1, 2, 3}, "3": {0, 1}}
        got = raw_findings(run_qc(df, permitted_values=wrong_keys))
        self.assertEqual(got.get("permitted_values_unusable"), "warn")
        self.assertTrue(WIDTH_CHECKS.intersection(got))

    def test_missing_values_are_not_categories_and_inputs_are_not_modified(self):
        df = response_table({f"i{i}": (0, 1, 2, 3) for i in range(4)})
        df.loc[0, "resp"] = float("nan")
        original = df.copy(deep=True)
        checks = run_qc(df, permitted_values={0, 1, 2, 3})
        self.assertNotIn("resp_outside_permitted", raw_findings(checks))
        self.assertIn("resp_na", [check.name for check in checks])
        pd.testing.assert_frame_equal(df, original)

    def test_numeric_strings_use_numeric_order_for_support_and_membership(self):
        df = response_table({**{f"a{i}": ("1", "2", "5") for i in range(6)},
                             **{f"b{i}": ("1", "5", "10") for i in range(4)}})
        self.assertEqual(raw_findings(run_qc(df)),
                         {"resp_scale_nested_support": "warn"})
        got = raw_findings(run_qc(df, permitted_values={1, 2, 3, 4, 5}))
        self.assertEqual(got.get("resp_outside_permitted"), "fail")

    def test_large_int64_categories_are_compared_without_float_rounding(self):
        first, excluded, last = 2**53 + 1, 2**53 + 2, 2**53 + 3
        df = response_table({f"i{i}": (first, last) for i in range(3)})
        df["resp"] = df["resp"].astype("int64")
        permitted = {first, last}
        self.assertEqual(raw_findings(run_qc(df, permitted_values=permitted)), {})
        df.loc[0, "resp"] = excluded
        checks = run_qc(df, permitted_values=permitted)
        self.assertEqual(raw_findings(checks).get("resp_outside_permitted"), "fail")
        detail = next(c.detail for c in checks if c.name == "resp_outside_permitted")
        self.assertIn("i0", detail)
        self.assertIn(str(excluded), detail)

    def test_float32_categories_respect_representation_without_broad_tolerance(self):
        df = response_table({f"i{i}": (0.1, 0.2) for i in range(3)})
        df["resp"] = df["resp"].astype(np.float32)
        self.assertEqual(raw_findings(run_qc(df, permitted_values={0.1, 0.2})), {})
        df.loc[0, "resp"] = np.float32(0.3)
        got = raw_findings(run_qc(df, permitted_values={0.1, 0.2}))
        self.assertEqual(got.get("resp_outside_permitted"), "fail")
        # A blanket isclose/allclose tolerance would incorrectly admit this
        # distinct float64 category; accommodation is only for representation.
        precise = response_table({f"i{i}": (0.1, 0.2) for i in range(3)})
        precise.loc[0, "resp"] = 0.1000000001
        got = raw_findings(run_qc(precise, permitted_values={0.1, 0.2}))
        self.assertEqual(got.get("resp_outside_permitted"), "fail")

    def test_decimal_integer_strings_preserve_large_documented_categories(self):
        first, excluded, last = 2**53 + 1, 2**53 + 2, 2**53 + 3
        df = response_table({f"i{i}": (first, last) for i in range(3)})
        df["resp"] = df["resp"].astype("int64")
        permitted = {str(first), str(last)}
        self.assertEqual(raw_findings(run_qc(df, permitted_values=permitted)), {})
        df.loc[0, "resp"] = excluded
        got = raw_findings(run_qc(df, permitted_values=permitted))
        self.assertEqual(got.get("resp_outside_permitted"), "fail")
        # A documented decimal fraction must not round into an integer code.
        df.loc[0, "resp"] = 2**53
        got = raw_findings(run_qc(df, permitted_values=permitted | {"9007199254740992.5"}))
        self.assertEqual(got.get("resp_outside_permitted"), "fail")


class NguyenAggregateReplay(unittest.TestCase):
    """Replay public marginal counts; synthetic IDs do not recover source pairs."""

    @staticmethod
    def replay(table_name):
        path = Path(__file__).with_name("fixtures") / "nguyen_item_supports.json"
        fixture = json.loads(path.read_text(encoding="utf-8"))
        source = next(table for table in fixture["tables"] if table["table"] == table_name)
        rows = []
        for item in source["item_supports"]:
            # IDs restart for each item. This preserves each item's exact
            # frequency distribution but invents cross-item alignment; none of
            # these assertions concerns a person's response pattern or IDs.
            synthetic_id = 0
            for value, count in sorted(item["response_counts"].items(),
                                       key=lambda pair: int(pair[0])):
                for _ in range(count):
                    rows.append((synthetic_id, item["item"], int(value)))
                    synthetic_id += 1
        return source, pd.DataFrame(rows, columns=["id", "item", "resp"])

    def test_barthel_deposit_marginals_warn_without_invented_permitted_sets(self):
        source, df = self.replay("nguyen_2026_barthel")
        self.assertEqual((len(df), df.item.nunique()), (3940, 10))
        self.assertIsNone(source["documented_common_permitted_values"])
        # Mobility never uses 5 in this deposit. Missing that interior value
        # does not invalidate interval nesting or define a permitted set.
        mobility = set(df.loc[df.item == "bi_dilai", "resp"])
        self.assertEqual(mobility, {0, 10, 15})
        self.assertEqual(raw_findings(run_qc(df)),
                         {"resp_scale_nested_support": "warn"})
        for profile in ("triage", "upload", "legacy"):
            with self.subTest(profile=profile):
                report = validate_frame(df, label=source["table"], profile=profile)
                self.assertTrue(report.ok, report.findings)
                self.assertIn("imputed_values*", [f.check for f in report.warnings])
                self.assertEqual(report_findings(report),
                                 {"resp_scale_nested_support": "warn"})

    def test_mspss_deposit_marginals_clear_only_with_supplied_codebook_values(self):
        source, df = self.replay("nguyen_2026_mspss")
        self.assertEqual((len(df), df.item.nunique()), (4728, 12))
        minima = df.groupby("item")["resp"].min().value_counts().to_dict()
        self.assertEqual(minima, {2: 8, 1: 4})
        self.assertEqual(raw_findings(run_qc(df)),
                         {"resp_scale_nested_support": "warn"})
        documented = source["documented_common_permitted_values"]
        self.assertEqual(documented, [1, 2, 3, 4, 5, 6, 7])
        context = {"permitted_values": documented}
        for profile in ("triage", "upload", "legacy"):
            with self.subTest(profile=profile):
                report = validate_frame(df, label=source["table"], profile=profile,
                                        context=context)
                self.assertTrue(report.ok, report.findings)
                self.assertEqual(report_findings(report), {})


class DocumentedConstructs(unittest.TestCase):
    def setUp(self):
        self.supports = {**{f"a{i}": range(1, 6) for i in range(4)},
                         **{f"b{i}": range(1, 8) for i in range(4)}}
        self.df = response_table(self.supports)
        self.constructs = {item: "anxiety" if item.startswith("a") else "social_support"
                           for item in self.supports}

    def test_construct_boundary_requires_explicit_evidence(self):
        self.assertEqual(raw_findings(run_qc(self.df)),
                         {"resp_scale_nested_support": "warn"})
        checks = run_qc(self.df, item_constructs=self.constructs)
        self.assertEqual(raw_findings(checks).get("resp_scale_constructs"), "fail")
        detail = next(c.detail for c in checks if c.name == "resp_scale_constructs")
        self.assertIn("anxiety", detail)
        self.assertIn("social_support", detail)

    def test_valid_documented_codes_cannot_cancel_a_construct_boundary(self):
        for permitted in (set(range(1, 8)), self.supports):
            with self.subTest(permitted=type(permitted).__name__):
                got = raw_findings(run_qc(self.df, permitted_values=permitted,
                                         item_constructs=self.constructs))
                self.assertEqual(got, {"resp_scale_constructs": "fail"})

    def test_documented_construct_boundary_is_checked_on_two_item_tables(self):
        df = response_table({"first_item": (0, 1), "second_item": (0, 1, 2, 3)})
        checks = run_qc(df, item_constructs={"first_item": "anxiety",
                                            "second_item": "social_support"})
        self.assertEqual(raw_findings(checks), {"resp_scale_constructs": "fail"})

    def test_equal_group_envelopes_do_not_claim_aligned_width_evidence(self):
        supports = {"a0": (0, 1), "a1": (0, 1, 2, 3), "a2": (0, 1),
                    "b0": (0, 1, 2, 3), "b1": (0, 1), "b2": (0, 1, 2, 3)}
        constructs = {item: item[0] for item in supports}
        got = raw_findings(run_qc(response_table(supports), item_constructs=constructs))
        self.assertEqual(got, {"resp_scale_nested_support": "warn"})

    def test_one_construct_does_not_hide_out_of_documentation_values(self):
        df = self.df.copy()
        df.loc[0, "resp"] = 99
        got = raw_findings(run_qc(df, permitted_values=self.supports,
                                 item_constructs={item: "one_construct"
                                                  for item in self.supports}))
        self.assertEqual(got.get("resp_outside_permitted"), "fail")

    def test_incomplete_or_invalid_construct_mapping_warns_not_guesses(self):
        for bad in ({}, {"a0": "anxiety"}, "anxiety", [],
                    {item: " " for item in self.supports},
                    {item: None for item in self.supports}):
            with self.subTest(bad=repr(bad)):
                got = raw_findings(run_qc(self.df, item_constructs=bad))
                self.assertEqual(got.get("item_constructs_unusable"), "warn")
                self.assertEqual(got.get("resp_scale_nested_support"), "warn")
                self.assertNotEqual(got.get("resp_scale_constructs"), "fail")

    def test_invalid_construct_mapping_cannot_hide_a_known_response_violation(self):
        got = raw_findings(run_qc(self.df, item_constructs={"a0": "anxiety"},
                                 permitted_values={1, 2, 3, 4, 5}))
        self.assertEqual(got.get("item_constructs_unusable"), "warn")
        self.assertEqual(got.get("resp_outside_permitted"), "fail")


class PublicEvidenceContract(unittest.TestCase):
    def test_old_width_waiver_cannot_waive_a_documented_construct_error(self):
        from irw_validate.cli import main

        supports = mixed_math(4, 4)
        df = response_table(supports)
        context = {"item_constructs": {item: item[:2] for item in supports}}
        for waiver, expected_code in (("resp_scale_mixed", 1), ("resp_scale_constructs", 0)):
            with self.subTest(waiver=waiver), tempfile.TemporaryDirectory() as directory:
                report = validate_frame(df, label="mixed_2026.csv", profile="upload", context=context)
                self.assertEqual([f.check for f in report.errors], ["resp_scale_constructs"])
                ledger = Path(directory) / "overrides.csv"
                output = io.StringIO()
                # CLI has no codebook argument. Exercise its real waiver path
                # on a real API report without inventing a new context interface.
                with patch("irw_validate.cli.validate_file", return_value=report), \
                        patch.dict(os.environ, {"IRW_VALIDATE_LEDGER": str(ledger)}), \
                        contextlib.redirect_stdout(output):
                    code = main(["mixed_2026.csv", "--json", "--override-check", waiver,
                                 "--override", "Test-only scoped waiver; no source data altered"])
                self.assertEqual(code, expected_code)
                result = json.loads(output.getvalue())[0]
                if expected_code:
                    self.assertIn("resp_scale_constructs", [f["check"] for f in result["findings"]])
                    self.assertEqual(result["overridden"], [])
                    self.assertFalse(ledger.exists())
                else:
                    self.assertEqual([f["check"] for f in result["overridden"]], ["resp_scale_constructs"])
                    self.assertIn("resp_scale_constructs", ledger.read_text())

    def test_invalid_text_skips_width_inference_but_not_documented_numeric_violation(self):
        df = response_table(mixed_math(4, 4)).astype({"resp": object})
        df.loc[0, "resp"] = "NA"
        report = validate_frame(df, profile="upload", context={"permitted_values": {0, 1}})
        self.assertTrue({"resp_numeric", "resp_outside_permitted"}.issubset(
            {f.check for f in report.errors}))
        self.assertFalse(WIDTH_CHECKS.intersection(f.check for f in report.findings))

    def test_documented_failures_block_triage_upload_and_legacy_but_not_core(self):
        supports = {**{f"a{i}": (0, 1) for i in range(4)},
                    **{f"b{i}": (0, 1, 2, 3) for i in range(4)}}
        df = response_table(supports)
        contexts = [({"permitted_values": {0, 1}}, "resp_outside_permitted"),
                    ({"item_constructs": {item: item[0] for item in supports}},
                     "resp_scale_constructs")]
        for context, expected_check in contexts:
            for profile in ("triage", "upload", "legacy"):
                with self.subTest(check=expected_check, profile=profile):
                    report = validate_frame(df, label="mixed_2026", profile=profile,
                                            context=context)
                    self.assertFalse(report.ok)
                    self.assertIn(expected_check, [f.check for f in report.errors])
            core = validate_frame(df, label="mixed_2026", profile="core", context=context)
            self.assertTrue(core.ok, core.findings)
            self.assertEqual(report_findings(core), {})
            self.assertTrue(all(f.check in CORE_CHECKS or f.check.endswith("_na")
                                for f in core.findings))

    def test_file_api_forwards_both_documentation_inputs(self):
        supports = mixed_math(4, 4)
        df = response_table(supports)
        permitted = supports
        contexts = [
            {"permitted_values": permitted,
             "item_constructs": {item: "math" for item in supports}},
            {"permitted_values": permitted,
             "item_constructs": {item: item[:2] for item in supports}},
            {"permitted_values": {0, 1}},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "math_2026.csv"
            df.to_csv(path, index=False)
            for context in contexts:
                with self.subTest(context=context):
                    frame_report = validate_frame(df, label=str(path), profile="upload",
                                                  context=context)
                    file_report = validate_file(path, profile="upload", context=context)
                    self.assertEqual(report_findings(file_report), report_findings(frame_report))
                    self.assertEqual(file_report.ok, frame_report.ok)
            self.assertTrue(validate_file(path, context=contexts[0]).ok)
            self.assertFalse(validate_file(path, context=contexts[1]).ok)
            self.assertFalse(validate_file(path, context=contexts[2]).ok)

    def test_compatibility_shim_accepts_the_same_optional_evidence(self):
        self.assertIs(compatible_run_qc, run_qc)
        supports = mixed_math(4, 4)
        df = response_table(supports)
        kwargs = {"permitted_values": supports,
                  "item_constructs": {item: "math" for item in supports}}
        self.assertEqual(raw_findings(compatible_run_qc(df, **kwargs)), {})

    def test_unused_categorical_item_level_is_not_an_undocumented_item(self):
        df = response_table({"a": (0, 1), "b": (0, 1, 2, 3)})
        df["item"] = pd.Categorical(df["item"], categories=["a", "b", "unused"])
        original = df.copy(deep=True)
        context = {"permitted_values": {"a": {0, 1}, "b": {0, 1, 2, 3}},
                   "item_constructs": {"a": "math", "b": "math"}}
        self.assertEqual(raw_findings(run_qc(df, **context)), {})
        report = validate_frame(df, label="math_2026", profile="upload", context=context)
        self.assertTrue(report.ok, report.findings)
        self.assertEqual(report_findings(report), {})
        pd.testing.assert_frame_equal(df, original)
        self.assertEqual(df["item"].cat.categories.tolist(), ["a", "b", "unused"])

    def test_missing_columns_bad_responses_and_duplicate_keys_still_fail(self):
        df = response_table({f"i{i}": (0, 1, 2, 3) for i in range(4)})
        checks = run_qc(df.drop(columns="resp"), permitted_values={0, 1, 2, 3})
        self.assertEqual([(c.name, c.status) for c in checks],
                         [("required_columns", "fail")])
        mixed = df.astype({"resp": object})
        mixed.loc[:19, "resp"] = "not_a_response"
        statuses = {c.name: c.status for c in run_qc(mixed, permitted_values={0, 1, 2, 3})}
        self.assertEqual(statuses.get("resp_numeric"), "fail")
        duplicated = pd.concat([df, df.iloc[:1]], ignore_index=True)
        report = validate_frame(duplicated, context={"permitted_values": {0, 1, 2, 3}})
        self.assertIn("dup_id_item", [f.check for f in report.errors])


if __name__ == "__main__":
    unittest.main()
