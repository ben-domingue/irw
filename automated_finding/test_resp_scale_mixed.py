#!/usr/bin/env python3
"""Regression tests for run_qc()'s response-scale and permitted-value checks.

Run from `automated_finding/`:

    python3 test_resp_scale_mixed.py

Plain asserts, no pytest, no new dependency -- same idiom as the self-checking
scripts in `data/`. Every fixture is built in memory: no network, no files, no
reliance on the gitignored `irw_output/`, and no dependence on any deposit.

WHAT THE THREE STATUSES MEAN HERE. The distinction these tests exist to hold:

  pass  no observed evidence of incompatible response coding. NOT a claim that
        the items' permitted response scales have been verified identical --
        observed support is a lower bound on what an instrument permitted, and
        run_qc sees only observations. An item observed 3-5 inside a modal 1-5
        table passes because nothing contradicts one shared scale, not because
        one shared scale has been established.
  warn  the observed supports are equally consistent with ordinary category
        non-use and with a genuine coding difference. Documentation or a human
        is required; the data cannot settle it.
  fail  an observed pattern incompatible with the modal scale, or with the
        caller's documented permitted values.

Diagnostic identifiers exercised below (all stable, no wildcards):
  resp_scale_mixed          fail  incompatible observed ranges
  item_scale_outlier        warn  one or two items outside the table's scale
  resp_scale_nested_support warn  nested support, shared ceiling -- ambiguous
  resp_outside_permitted    fail  a response outside its documented set
  permitted_values_unusable warn  documentation supplied but not usable
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irw_triage_updated import run_qc  # noqa: E402

SCALE_CHECKS = {"resp_scale_mixed", "item_scale_outlier",
                "resp_scale_nested_support"}
DOC_CHECKS = {"resp_outside_permitted", "permitted_values_unusable"}


# --------------------------------------------------------------- helpers ----

def table(items):
    """Long frame from {item_name: [response values]}.

    Values are cycled to a common length, so an item's observed (min, max) is
    exactly the (min, max) of the list handed in -- deterministic, with no
    reliance on a random draw happening to hit an endpoint.
    """
    n = max(len(v) for v in items.values()) * 4
    rows = []
    for name, vals in items.items():
        for i in range(n):
            rows.append({"id": i, "item": name, "resp": vals[i % len(vals)]})
    return pd.DataFrame(rows)


def findings(checks, names):
    return {c.name: c.status for c in checks if c.name in names}


def status_of(checks, name):
    hits = [c.status for c in checks if c.name == name]
    return hits[0] if hits else None


def detail_of(checks, name):
    hits = [c.detail for c in checks if c.name == name]
    return hits[0] if hits else ""


RESULTS = []


def expect(label, condition):
    print(f"  {'PASS' if condition else 'FAIL'}  {label}")
    RESULTS.append(bool(condition))


# ------------------------------------------------------------ PASS cases ----
# "pass" here = no observed evidence of incompatible coding. See module docstring.


def test_identical_ranges_pass():
    checks = run_qc(table({f"i{n:02d}": [1, 2, 3, 4, 5] for n in range(1, 6)}))
    expect("identical observed ranges -> no evidence of incompatible coding",
           findings(checks, SCALE_CHECKS | DOC_CHECKS) == {})


def test_contained_support_no_evidence_but_no_claim():
    """Items observed 1-3 and 3-5 inside a modal 1-5 table.

    Nothing reaches below the modal floor, so nothing contradicts one shared
    scale and no check fires. That is the *absence of counter-evidence*, not a
    verification: 3-5 could in principle be a 3-point scale, and run_qc has no
    way to know. The assertion below is deliberately about what is NOT claimed.
    """
    items = {f"i{n:02d}": [1, 2, 3, 4, 5] for n in range(1, 6)}
    items.update({"i06": [1, 2, 3], "i07": [3, 4, 5], "i08": [2, 3, 4]})
    checks = run_qc(table(items))
    expect("support contained inside the modal range -> no evidence of "
           "incompatible coding",
           findings(checks, SCALE_CHECKS | DOC_CHECKS) == {})
    expect("...and no check claims the permitted scales were verified",
           not any("verified" in c.detail or "confirmed identical" in c.detail
                   for c in checks))


def test_uniform_with_unused_ceiling_passes():
    """Shared floor, some items stop short of the ceiling."""
    items = {f"i{n:02d}": [1, 2, 3, 4, 5] for n in range(1, 7)}
    items.update({f"i{n:02d}": [1, 2, 3, 4] for n in range(7, 10)})
    checks = run_qc(table(items))
    expect("shared floor with an unused ceiling on some items -> no evidence",
           findings(checks, SCALE_CHECKS | DOC_CHECKS) == {})


# ------------------------------------------------------- AMBIGUOUS (WARN) ----


def test_adversarial_one_vs_zero_warns_without_documentation():
    """THE adversarial case: 9 items observed 1-5, 1 item observed 0-5, no docs.

    Equally consistent with one 0-5 scale whose zero went unobserved on nine
    items, and with a 6-point item among nine 5-point items. Must never pass.
    """
    items = {f"i{n:02d}": [1, 2, 3, 4, 5] for n in range(1, 10)}
    items["i10"] = [0, 1, 2, 3, 4, 5]
    checks = run_qc(table(items))
    expect("adversarial 1-5 majority vs 0-5 minority, no docs -> WARN",
           findings(checks, SCALE_CHECKS | DOC_CHECKS)
           == {"resp_scale_nested_support": "warn"})
    expect("...and never a pass",
           status_of(checks, "resp_scale_nested_support") is not None)


def test_nguyen_mspss_shape_warns_without_documentation():
    """nguyen_2026_mspss shape: 8 items observed 2-7, 4 observed 1-7."""
    items = {f"i{n:02d}": list(range(2, 8)) for n in range(1, 9)}
    items.update({f"i{n:02d}": list(range(1, 8)) for n in range(9, 13)})
    checks = run_qc(table(items))
    expect("Nguyen MSPSS shape without documentation -> WARN",
           findings(checks, SCALE_CHECKS | DOC_CHECKS)
           == {"resp_scale_nested_support": "warn"})


def test_nguyen_mspss_shape_passes_only_with_valid_documentation():
    items = {f"i{n:02d}": list(range(2, 8)) for n in range(1, 9)}
    items.update({f"i{n:02d}": list(range(1, 8)) for n in range(9, 13)})
    df = table(items)
    expect("Nguyen MSPSS shape with the documented 1-7 set -> PASS",
           findings(run_qc(df, permitted_values=set(range(1, 8))),
                    SCALE_CHECKS | DOC_CHECKS) == {})
    expect("...same via a per-item dict of that set -> PASS",
           findings(run_qc(df, permitted_values={i: set(range(1, 8)) for i in items}),
                    SCALE_CHECKS | DOC_CHECKS) == {})


def test_documented_equal_permitted_values_clear_the_warning():
    items = {f"i{n:02d}": [1, 2, 3, 4, 5] for n in range(1, 10)}
    items["i10"] = [0, 1, 2, 3, 4, 5]
    df = table(items)
    expect("documented 0-5 shared by every item clears the warning",
           findings(run_qc(df, permitted_values={0, 1, 2, 3, 4, 5}),
                    SCALE_CHECKS | DOC_CHECKS) == {})


# ------------------------- documentation that must NOT clear the warning ----


def test_contradictory_documentation_is_rejected_not_honoured():
    """Docs that the data contradicts, or that disagree per item."""
    items = {f"i{n:02d}": [1, 2, 3, 4, 5] for n in range(1, 10)}
    items["i10"] = [0, 1, 2, 3, 4, 5]
    df = table(items)

    checks = run_qc(df, permitted_values={1, 2, 3, 4, 5})
    expect("documented 1-5 while a 0 is observed -> FAIL + warning stands",
           status_of(checks, "resp_outside_permitted") == "fail"
           and status_of(checks, "resp_scale_nested_support") == "warn")
    # Assert the exact item-to-value pairing. A bare `"0" in detail` would pass
    # on the item label "i10" alone, so it is not evidence that the offending
    # value was reported at all.
    detail = detail_of(checks, "resp_outside_permitted")
    expect("...and the failure names the exact offending item -> value pairing",
           "i10 has ['0']" in detail)
    expect("...and names only that item, not the nine compliant ones",
           sum(f"i{n:02d} has" in detail for n in range(1, 11)) == 1)

    disagreeing = {i: {1, 2, 3, 4, 5} for i in items}
    disagreeing["i10"] = {0, 1, 2, 3, 4, 5}
    expect("per-item sets that disagree -> warning stands (that IS two scales)",
           status_of(run_qc(df, permitted_values=disagreeing),
                     "resp_scale_nested_support") == "warn")


def test_incomplete_or_malformed_documentation_is_reported_not_silent():
    """A broken codebook must not look identical to an absent one."""
    items = {f"i{n:02d}": [1, 2, 3, 4, 5] for n in range(1, 10)}
    items["i10"] = [0, 1, 2, 3, 4, 5]
    df = table(items)

    incomplete = {i: {0, 1, 2, 3, 4, 5} for i in list(items)[:-1]}
    checks = run_qc(df, permitted_values=incomplete)
    expect("an item missing from the documented dict -> unusable + warn stands",
           status_of(checks, "permitted_values_unusable") == "warn"
           and status_of(checks, "resp_scale_nested_support") == "warn")
    expect("...and the reason names the undocumented item",
           "i10" in detail_of(checks, "permitted_values_unusable"))

    for label, bad in [("non-numeric labels", {"low", "mid", "high"}),
                       ("an empty set", set()),
                       ("a bare string", "0-5"),
                       ("a None entry", {i: None for i in items}),
                       ("a NaN value", {0, 1, 2, 3, 4, float("nan")})]:
        checks = run_qc(df, permitted_values=bad)
        expect(f"malformed documentation ({label}) -> reported as unusable",
               status_of(checks, "permitted_values_unusable") == "warn"
               and status_of(checks, "resp_scale_nested_support") == "warn")

    expect("no documentation at all -> warn, but NO unusable diagnostic",
           status_of(run_qc(df), "permitted_values_unusable") is None)


def test_numeric_types_normalise_consistently():
    items = {f"i{n:02d}": [1, 2, 3, 4, 5] for n in range(1, 10)}
    items["i10"] = [0, 1, 2, 3, 4, 5]
    df = table(items)
    for label, pv in [("python ints", {0, 1, 2, 3, 4, 5}),
                      ("python floats", {0.0, 1.0, 2.0, 3.0, 4.0, 5.0}),
                      ("numpy int64", {np.int64(v) for v in range(6)}),
                      ("numpy float64", {np.float64(v) for v in range(6)}),
                      ("a list, not a set", [0, 1, 2, 3, 4, 5]),
                      ("a range object", range(0, 6)),
                      ("numeric strings", {"0", "1", "2", "3", "4", "5"})]:
        expect(f"documented as {label} -> clears identically",
               findings(run_qc(df, permitted_values=pv),
                        SCALE_CHECKS | DOC_CHECKS) == {})


def test_missing_responses_are_not_a_response_category():
    """NaN must not count as an observed value, nor satisfy a permitted set."""
    items = {f"i{n:02d}": [1, 2, 3, 4, 5] for n in range(1, 5)}
    df = table(items)
    df.loc[df.index[:10], "resp"] = np.nan
    checks = run_qc(df, permitted_values={1, 2, 3, 4, 5})
    expect("NaN responses do not trigger resp_outside_permitted",
           status_of(checks, "resp_outside_permitted") is None)
    expect("NaN responses do not widen an item's observed support",
           findings(checks, SCALE_CHECKS) == {})
    expect("NaN is still reported by the existing resp NA check",
           status_of(checks, "resp_na") == "warn")


def test_documented_violation_reported_even_without_nested_support():
    """The check must not be reachable only via the nested-support arm."""
    df = table({f"i{n:02d}": [1, 2, 3, 9] for n in range(1, 5)})
    checks = run_qc(df, permitted_values={1, 2, 3, 4, 5})
    expect("uniform ranges but a documented violation -> FAIL (not silent)",
           status_of(checks, "resp_outside_permitted") == "fail")


# ------------------------------------------------------------- FAIL cases ----


def test_mixed_scales_still_fail():
    """Eugene-Springfield `sdv`: incompatible ceilings in one table."""
    items = {f"i{n:02d}": list(range(1, 6)) for n in range(1, 7)}
    items.update({f"i{n:02d}": list(range(1, 10)) for n in range(7, 11)})
    expect("genuinely mixed 1-5 / 1-9 scales -> FAIL",
           status_of(run_qc(table(items)), "resp_scale_mixed") == "fail")


def test_translated_scales_still_fail():
    """0-4 mixed with 1-5: non-nested -- floor AND ceiling both shift.

    The three items reaching 0 also stop short of the modal ceiling, which puts
    them in the incompatible-range bucket and NOT in the ambiguous one. The two
    buckets must stay disjoint: emitting `resp_scale_nested_support` here as
    well would tell a reviewer the table is merely ambiguous at the same moment
    it is being failed as incompatible. Asserting the exact diagnostic set is
    what pins that -- `off["max"] == modal[1]` in the nested predicate is
    load-bearing, and a loosened `<=` would put these items in both buckets.
    """
    items = {f"i{n:02d}": list(range(0, 5)) for n in range(1, 4)}
    items.update({f"i{n:02d}": list(range(1, 6)) for n in range(4, 11)})
    checks = run_qc(table(items))
    expect("translated 0-4 / 1-5 scales -> FAIL",
           status_of(checks, "resp_scale_mixed") == "fail")
    expect("...and emits no ambiguity finding: the buckets are disjoint",
           status_of(checks, "resp_scale_nested_support") is None)
    expect("...exact non-pass scale diagnostics == {(resp_scale_mixed, fail)}",
           {(c.name, c.status) for c in checks
            if c.name in SCALE_CHECKS and c.status != "pass"}
           == {("resp_scale_mixed", "fail")})


def test_admin_column_still_warns():
    """Eugene-Springfield `submiss`: a count column swept in as an item."""
    items = {f"i{n:02d}": list(range(1, 6)) for n in range(1, 10)}
    items["submiss"] = list(range(0, 21))
    checks = run_qc(table(items))
    expect("a lone administrative count column -> WARN item_scale_outlier",
           status_of(checks, "item_scale_outlier") == "warn"
           and status_of(checks, "resp_scale_mixed") is None
           and "submiss" in detail_of(checks, "item_scale_outlier"))


def test_nguyen_barthel_shape_remains_a_failure():
    """nguyen_2026_barthel: legitimate per-item point ceilings, still a fail.

    The Barthel Index is one instrument in one file, but its items carry
    different weights (Bathing/Grooming 0/5, six items 0/5/10, Transfers and
    Mobility 0/5/10/15). Those ceilings are incompatible, not nested, so this
    is the FAIL arm and not the ambiguous one -- and from observed values alone
    it is indistinguishable from a mailing that bundled two scales.

    This asserts the check STILL FIRES. Intentional: the case is resolved by a
    named waiver in the processing script, not by weakening the check, and
    pinning it here means a future change cannot quietly alter it.
    """
    items = {f"i{n:02d}": [0, 5] for n in range(1, 3)}
    items.update({f"i{n:02d}": [0, 5, 10] for n in range(3, 9)})
    items.update({f"i{n:02d}": [0, 5, 10, 15] for n in range(9, 11)})
    expect("weighted per-item ceilings (Barthel) -> FAIL",
           status_of(run_qc(table(items)), "resp_scale_mixed") == "fail")


def test_two_item_table_skips_the_range_heuristics():
    checks = run_qc(table({"i01": [1, 2, 3, 4, 5], "i02": [0, 1, 2, 3, 4, 5]}))
    expect("a two-item table skips the modal-range checks",
           findings(checks, SCALE_CHECKS) == {})


# --------------------------------------- every other check must be untouched


def test_unrelated_checks_unchanged():
    clean = table({f"i{n:02d}": [1, 2, 3, 4, 5] for n in range(1, 6)})
    expect("a clean table yields exactly the three passing structural checks",
           {(c.name, c.status) for c in run_qc(clean)}
           == {("required_columns", "pass"), ("resp_numeric", "pass"),
               ("dup_id_item", "pass")})

    missing = clean.drop(columns=["resp"])
    checks = run_qc(missing)
    expect("required_columns still fails and short-circuits",
           len(checks) == 1 and checks[0].status == "fail"
           and checks[0].name == "required_columns")

    text = clean.copy()
    text["resp"] = "high"
    expect("resp_numeric still fails on text responses",
           status_of(run_qc(text), "resp_numeric") == "fail")

    dup = pd.concat([clean, clean], ignore_index=True)
    expect("dup_id_item still fails without a longitudinal column",
           status_of(run_qc(dup), "dup_id_item") == "fail")

    dup_wave = dup.copy()
    dup_wave["wave"] = [1] * len(clean) + [2] * len(clean)
    expect("dup_id_item still downgrades to warn with a wave column",
           status_of(run_qc(dup_wave), "dup_id_item") == "warn")

    flat = clean.copy()
    flat["resp"] = 3
    expect("resp_variation* still fails when resp never varies",
           status_of(run_qc(flat), "resp_variation*") == "fail")

    wide = table({f"i{n:02d}": list(range(1, 61)) for n in range(1, 4)})
    expect("resp_ordinal* still warns above 50 distinct responses",
           status_of(run_qc(wide), "resp_ordinal*") == "warn")

    composite = table({"total": [1, 2, 3], "mean": [1, 2, 3], "sum": [1, 2, 3]})
    expect("composite_items* still fails when every label is a score",
           status_of(run_qc(composite), "composite_items*") == "fail")

    partial = table({"i01": [1, 2, 3], "i02": [1, 2, 3], "subscale_a": [1, 2, 3]})
    expect("composite_items* still warns when only some labels are scores",
           status_of(run_qc(partial), "composite_items*") == "warn")

    stray = clean.copy()
    stray["age"] = 30
    expect("cov_prefix still warns on an unrecognized column",
           status_of(run_qc(stray), "cov_prefix") == "warn")

    skewed = table({f"i{n:02d}": [1] * 9 + [2] for n in range(1, 4)})
    expect("imputed_values* still warns on a >60% modal response",
           status_of(run_qc(skewed), "imputed_values*") == "warn")

    melted = run_qc(clean, coercion_method="wide-to-long")
    expect("resp_direction* still warns under a wide-to-long coercion",
           status_of(melted, "resp_direction*") == "warn")

    expect("valid permitted_values never makes an unrelated check stricter",
           {(c.name, c.status) for c in run_qc(clean, permitted_values={1, 2, 3, 4, 5})}
           == {(c.name, c.status) for c in run_qc(clean)})


def test_diagnostic_contract():
    """Exact (name, status) contract for every fixture this module relies on.

    Replaces an earlier assertion that searched check names for a "*" on a
    fixture that could never produce one -- it passed regardless of what the
    new keys were called, so it guaranteed nothing. This asserts the exact
    diagnostic set per fixture instead: a renamed key, a changed status, or a
    newly-emitted diagnostic all break it, with no source-text matching.
    """
    clean = table({f"i{n:02d}": [1, 2, 3, 4, 5] for n in range(1, 6)})
    mixed = table({**{f"i{n:02d}": list(range(1, 6)) for n in range(1, 7)},
                   **{f"i{n:02d}": list(range(1, 10)) for n in range(7, 11)}})
    nested = table({**{f"i{n:02d}": [1, 2, 3, 4, 5] for n in range(1, 10)},
                    "i10": [0, 1, 2, 3, 4, 5]})
    outlier = table({**{f"i{n:02d}": list(range(1, 6)) for n in range(1, 10)},
                     "submiss": list(range(0, 21))})

    expect("clean table emits exactly three checks, all passing",
           {(c.name, c.status) for c in run_qc(clean)}
           == {("required_columns", "pass"), ("resp_numeric", "pass"),
               ("dup_id_item", "pass")})

    contract = [
        ("incompatible ceilings, no docs", mixed, None,
         {("resp_scale_mixed", "fail")}),
        ("nested support, no docs", nested, None,
         {("resp_scale_nested_support", "warn")}),
        ("nested support, confirming docs", nested, {0, 1, 2, 3, 4, 5},
         set()),
        ("nested support, docs contradicted by the data", nested, {1, 2, 3, 4, 5},
         {("resp_outside_permitted", "fail"),
          ("resp_scale_nested_support", "warn")}),
        ("nested support, unusable docs", nested, {"low", "high"},
         {("permitted_values_unusable", "warn"),
          ("resp_scale_nested_support", "warn")}),
        ("lone out-of-scale column", outlier, None,
         {("item_scale_outlier", "warn")}),
    ]
    for label, df, pv, want in contract:
        got = {(c.name, c.status) for c in run_qc(df, permitted_values=pv)
               if c.status != "pass"}
        expect(f"contract: {label}", got == want)


# ------------------------- FAIL must survive unusable documentation ---------


def test_malformed_documentation_cannot_conceal_an_independent_fail():
    """A broken codebook must not downgrade or hide a real incompatibility.

    resp_scale_mixed never consults documentation, so an unusable, incomplete
    or over-permissive set can only ADD a diagnostic, never remove one. This
    pins that: the fail has to survive every flavour of bad documentation.
    """
    mixed = table({**{f"i{n:02d}": list(range(1, 6)) for n in range(1, 7)},
                   **{f"i{n:02d}": list(range(1, 10)) for n in range(7, 11)}})
    for label, pv in [("no documentation", None),
                      ("non-numeric labels", {"low", "high"}),
                      ("an empty set", set()),
                      ("an incomplete dict", {"i01": {1, 2, 3}}),
                      ("an over-permissive set 0-9", set(range(0, 10)))]:
        checks = run_qc(mixed, permitted_values=pv)
        expect(f"incompatible ceilings still FAIL with {label}",
               status_of(checks, "resp_scale_mixed") == "fail")


def test_non_finite_permitted_value_is_unusable_and_hides_nothing():
    """inf / -inf are not response categories; treat them as broken docs."""
    mixed = table({**{f"i{n:02d}": list(range(1, 6)) for n in range(1, 7)},
                   **{f"i{n:02d}": list(range(1, 10)) for n in range(7, 11)}})
    for label, bad in [("+inf", {1, 2, 3, float("inf")}),
                       ("-inf", {1, 2, 3, float("-inf")})]:
        checks = run_qc(mixed, permitted_values=bad)
        expect(f"a {label} permitted value -> unusable documentation",
               status_of(checks, "permitted_values_unusable") == "warn")
        expect(f"...and the independent FAIL still stands with {label}",
               status_of(checks, "resp_scale_mixed") == "fail")


# ------------------------------------------- response dtype robustness ------


def test_numeric_strings_order_numerically():
    """Responses stored as strings must be compared as numbers, not text.

    Lexicographically "10" < "5", which hid a genuine 1-5 vs 1-10 scale mix.
    Ordering on the numeric coercion catches it.
    """
    items = {f"i{n:02d}": ["1", "2", "3", "4", "5"] for n in range(1, 7)}
    items.update({f"i{n:02d}": ["1", "5", "10"] for n in range(7, 11)})
    checks = run_qc(table(items))
    expect("numeric-string responses: a real 1-5 vs 1-10 mix is detected",
           status_of(checks, "resp_scale_mixed") == "fail")
    expect("...and no spurious nested-support finding is raised",
           status_of(checks, "resp_scale_nested_support") is None)


def test_mixed_numeric_and_text_responses_do_not_crash():
    """A part-numeric, part-text resp column must not raise out of run_qc.

    Comparing str against int inside the per-item min/max aggregation used to
    raise TypeError, and no caller catches it -- the 46 scripts in `data/` call
    run_qc bare and triage_dataset has no try/except around it.
    """
    df = table({f"i{n:02d}": [1, 2, 3, 4, 5] for n in range(1, 5)})
    df = df.astype({"resp": object})
    df.loc[df.index[:2], "resp"] = "n/a"
    try:
        checks = run_qc(df)
        raised = None
    except Exception as exc:                       # noqa: BLE001 - test probe
        checks, raised = [], exc
    expect("a mixed numeric/text resp column does not raise", raised is None)
    expect("...and is reported as resp_numeric: fail",
           status_of(checks, "resp_numeric") == "fail")


# ------------------------------------------------------------------- main ----

if __name__ == "__main__":
    print("response-scale / permitted-value regression tests\n")
    print(" no observed evidence of incompatible coding (pass):")
    test_identical_ranges_pass()
    test_contained_support_no_evidence_but_no_claim()
    test_uniform_with_unused_ceiling_passes()
    print("\n ambiguous without documentation (warn):")
    test_adversarial_one_vs_zero_warns_without_documentation()
    test_nguyen_mspss_shape_warns_without_documentation()
    test_nguyen_mspss_shape_passes_only_with_valid_documentation()
    test_documented_equal_permitted_values_clear_the_warning()
    print("\n documentation that must not clear the warning:")
    test_contradictory_documentation_is_rejected_not_honoured()
    test_incomplete_or_malformed_documentation_is_reported_not_silent()
    test_numeric_types_normalise_consistently()
    test_missing_responses_are_not_a_response_category()
    test_documented_violation_reported_even_without_nested_support()
    print("\n incompatible with the modal scale (fail / outlier warn):")
    test_mixed_scales_still_fail()
    test_translated_scales_still_fail()
    test_admin_column_still_warns()
    test_nguyen_barthel_shape_remains_a_failure()
    test_two_item_table_skips_the_range_heuristics()
    print("\n a bad codebook must never conceal a real incompatibility:")
    test_malformed_documentation_cannot_conceal_an_independent_fail()
    test_non_finite_permitted_value_is_unusable_and_hides_nothing()
    print("\n response dtype robustness:")
    test_numeric_strings_order_numerically()
    test_mixed_numeric_and_text_responses_do_not_crash()
    print("\n unrelated checks, must be unchanged:")
    test_unrelated_checks_unchanged()
    print("\n exact diagnostic contract:")
    test_diagnostic_contract()

    failed = RESULTS.count(False)
    print(f"\n{len(RESULTS) - failed}/{len(RESULTS)} passed")
    sys.exit(1 if failed else 0)
