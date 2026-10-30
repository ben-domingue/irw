#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0259888
# DOI: 10.1371/journal.pone.0259888
# Paper: Bock, D., Harms, U., & Mahler, D. (2021). Examining the dimensionality
#   of pre-service teachers' enthusiasm for teaching by combining frameworks of
#   educational science and organizational psychology. PLOS ONE 16(11).
# Data: journal.pone.0259888.s001 (S1 Dataset, .sav), 211 rows x 150 columns.
#   An SPSS file with a variable label on all 150 columns and value labels on
#   75 of them.
# License: CC BY 4.0 (Crossref licence record for the version of record; the
#   data is a Supporting Information file of the article itself).
# 211 pre-service biology teachers.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# ELEVEN output tables, and the two most valuable are not Likert scales. This
# deposit carries two ACHIEVEMENT TESTS alongside the self-report batteries:
#   PCK  34 items, partial credit 0/1/2  pedagogical content knowledge
#   CK   38 items, partial credit 0/1/2  content knowledge
# Scored cognitive items with partial credit are much rarer in this corpus
# than agreement scales, and they are the reason this deposit is worth the
# eleven tables.
#
# THE TESTS USE A ROTATED-BOOKLET (PLANNED MISSING) DESIGN, which is the thing
# to get right. Per-item response counts run from 36 to 211 -- I100Cf has 36,
# I53Cf 105, P8Af all 211 -- while every self-report item has 193-211. That
# pattern is not attrition; it is multi-matrix sampling, where each respondent
# sees a subset of the item pool. The consequences for this script:
#   * missing cells are dropped and NO respondent is dropped, so every table
#     keeps all 211 ids where any item was answered;
#   * the tests are NOT split by booklet, because the deposit carries no
#     booklet indicator at all -- only the missingness pattern would reveal
#     the design, and reconstructing booklets from it would be inference;
#   * the script asserts the planned-missing shape rather than just tolerating
#     it, so a future file with ordinary attrition would look different and
#     fail here.
# A user fitting an IRT model to either test needs to know the missingness is
# by design and ignorable; a user computing a raw sum does not, and would be
# wrong. Both tables say so in their descriptions.
#
# THE VARIABLE LABELS NAME THE CONSTRUCT, NOT THE ITEM -- which is why no item
# text ships. All 150 columns carry a label, but the labels repeat across a
# battery ("ck-related self-concept" five times, "PCK" thirty-four times), so
# they identify the scale and not the question. The VALUE labels, by contrast,
# are full anchor text ("does not apply at all" / "does not much apply" /
# "largely applies" / "fully applies"), so for the Likert tables the options
# exist and the stems do not -- the exact inverse of the usual situation in
# this batch, and still unshippable: option text alone is barred (irw#1770),
# and the itemtext schema needs a stem per item.
#
# REVERSED ITEMS ARE ALREADY RECODED AT SOURCE and the deposit says so in the
# label: `ITQ_2_c` is labelled "intention to quit, reversed", and three of the
# six occupational-commitment items are labelled "occupational commitment,
# reversed". The `_c` suffix plus that label is the depositors' recode marker,
# so for those items resp is the corrected value rather than the category the
# respondent chose. The script asserts the labels still carry "reversed", and
# both affected descriptions say it.
#
# The eleven tables, grouped by the deposit's own variable labels rather than
# by column-name guesswork:
#   bock_2021_intention_to_quit        5 items, 1-5  (includes 1 recoded item)
#   bock_2021_self_concept_ck          5 items, 1-4
#   bock_2021_self_concept_pck         5 items, 1-4
#   bock_2021_self_concept_ppk         5 items, 1-4
#   bock_2021_enthusiasm_generic       6 items, 1-4
#   bock_2021_enthusiasm_subject       6 items, 1-4
#   bock_2021_career_choice_motives   32 items, 1-4  (six labelled subscales)
#   bock_2021_emotional_exhaustion     4 items, 1-4
#   bock_2021_occupational_commitment  6 items, 1-4  (includes 3 recoded items)
#   bock_2021_pck_test                34 items, 0-2
#   bock_2021_ck_test                 38 items, 0-2
#
# CAREER CHOICE MOTIVES IS ONE TABLE, NOT SIX, unlike the enthusiasm and
# self-concept splits above. The six labels are "career choice motives - X"
# for six X's: they are explicitly subscales of one named instrument
# (FEMOLA-style career-choice-motivation inventory) on one 1-4 scale, so they
# collapse per the same rule that kept padchasuwan_2026 and oppong_2026 whole
# in this batch. The self-concept and enthusiasm blocks stay separate because
# their labels name three different knowledge domains and two different
# referents rather than facets of one scale.
#
# `id` is the deposit's `code`, a zero-padded string '001'..'211', verified
# unique. Note it reads as numeric 1-211 if coerced, which is why it is
# handled as the string it is.
#
# Covariates: sex, age in years, semester.
#
# PII: screened over all 150 columns. One string column (`code`, the
# participant number) and no names, emails, dates, free text or geography.

import os
import sys
from collections import defaultdict

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("BOCK_RAW", "journal.pone.0259888_S1_Dataset.sav")

N_ROWS = 211

# the deposit's own variable labels -> (table, lo, hi, expected item count)
# ("intention to quit" and "occupational commitment" each have a second,
#  "..., reversed" label for their recoded items; both fold into one table)
GROUPS = {
    "intention to quit": ("bock_2021_intention_to_quit", 1, 5, 5),
    "ck-related self-concept": ("bock_2021_self_concept_ck", 1, 4, 5),
    "pck-related self-concept": ("bock_2021_self_concept_pck", 1, 4, 5),
    "ppk-related self-concept": ("bock_2021_self_concept_ppk", 1, 4, 5),
    "generic enthusiasm for teaching": ("bock_2021_enthusiasm_generic", 1, 4, 6),
    "enthusiasm for teaching the subject":
        ("bock_2021_enthusiasm_subject", 1, 4, 6),
    "emotional exhaustion": ("bock_2021_emotional_exhaustion", 1, 4, 4),
    "occupational commitment": ("bock_2021_occupational_commitment", 1, 4, 6),
    "PCK": ("bock_2021_pck_test", 0, 2, 34),
    "CK": ("bock_2021_ck_test", 0, 2, 38),
}
# the six "career choice motives - X" labels collapse into one table
MOTIVES = ("bock_2021_career_choice_motives", 1, 4, 32)
MOTIVE_PREFIX = "career choice motives - "
# labels whose items the depositors already reverse-recoded
REVERSED = {"intention to quit, reversed": "intention to quit",
            "occupational commitment, reversed": "occupational commitment"}
META = {"code", "sex", "age", "semester"}
TESTS = {"bock_2021_pck_test", "bock_2021_ck_test"}


PII_PAT = (r"[\w.+-]+@[\w-]+\.[a-z]{2,}"
           r"|\+?\d{9,}"
           r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")


def screen_for_pii(df):
    """Two passes, because one would miss something here.

    The usual selector drops string columns whose every value parses as a
    number, so that long decimals do not trip the phone pattern. That guard is
    right, but it also drops `code` -- a genuine string column holding
    '001'..'211', every value of which parses as a number. So the free-text
    pattern match runs over the non-numeric-looking string columns, and the
    string columns as a whole are reported and checked separately."""
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    free_text = [c for c in strings
                 if pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: {len(strings)} string column(s) of {len(df.columns)} "
          f"({strings}), of which {len(free_text)} are not numeric-looking "
          f"({free_text})")
    assert strings == ["code"], f"unexpected string column(s): {strings}"
    assert not free_text, f"unexpected free-text column(s): {free_text}"
    hits = [(c, v) for c in free_text
            for v in df[c].dropna().astype(str).unique()
            if pd.Series([v]).str.contains(PII_PAT, regex=True,
                                           case=False).any()]
    assert not hits, f"PII screen hit: {hits[:5]}"
    assert df["code"].str.fullmatch(r"\d{3}").all(), "code is not a 3-digit number"
    print("  clean: the only string column is `code`, a zero-padded "
          "participant number; no name, email, date, free text or geography")


def assert_planned_missing(df, cols, name):
    """A rotated-booklet design, not attrition. Assert the shape so a file with
    ordinary dropout fails here instead of being silently treated as planned."""
    counts = df[cols].notna().sum()
    lo, hi = int(counts.min()), int(counts.max())
    assert lo < 0.7 * N_ROWS, (
        f"{name}: lowest per-item n is {lo} of {N_ROWS}, which is too high for "
        f"the rotated-booklet design this script assumes -- recheck the source")
    assert df[cols].notna().any(axis=1).all(), f"{name}: a respondent saw no items"
    print(f"  {name}: per-item n ranges {lo}-{hi} of {N_ROWS} "
          f"(rotated-booklet / planned-missing design; cells dropped, no "
          f"respondent dropped)")


def convert():
    # pyreadstat for BOTH data and metadata, deliberately: pandas'
    # read_spss drops the labels this script groups by, and it also coerces
    # `code` away from the zero-padded string '001'..'211' that the file
    # actually stores, which the PII screen below checks for.
    import pyreadstat
    df, meta = pyreadstat.read_sav(RAW)
    labels = meta.column_names_to_labels
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    for rev, base in REVERSED.items():
        assert any(str(labels.get(c)) == rev for c in df.columns), (
            f"the depositors' recode marker {rev!r} is gone from the labels; "
            f"the reversed-item note in the descriptions depends on it")
    print(f"confirmed the depositors' reverse-recode markers are present: "
          f"{sorted(REVERSED)}")

    by_label = defaultdict(list)
    for c in df.columns:
        if c not in META:
            by_label[str(labels.get(c) or "")].append(c)

    blocks = {}
    for lab, cols in by_label.items():
        if lab in GROUPS:
            blocks.setdefault(GROUPS[lab][0], []).extend(cols)
        elif lab in REVERSED:
            blocks.setdefault(GROUPS[REVERSED[lab]][0], []).extend(cols)
        elif lab.startswith(MOTIVE_PREFIX):
            blocks.setdefault(MOTIVES[0], []).extend(cols)
        else:
            raise AssertionError(f"unaccounted variable label: {lab!r} {cols}")

    spec = {t: (lo, hi, n) for t, lo, hi, n in
            [(v[0], v[1], v[2], v[3]) for v in GROUPS.values()] + [MOTIVES]}
    for t, cols in blocks.items():
        lo, hi, n = spec[t]
        assert len(cols) == n, (t, len(cols), n)

    df = df.rename(columns={"code": "id", "sex": "cov_sex", "age": "cov_age",
                            "semester": "cov_semester"})
    cov_cols = ["cov_age", "cov_semester", "cov_sex"]

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for t in sorted(blocks):
        cols = sorted(blocks[t])
        lo, hi, n = spec[t]
        if t in TESTS:
            assert_planned_missing(df, cols, t)

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)

        assert long["resp"].between(lo, hi).all(), (t, sorted(long["resp"].unique()))
        assert long["id"].nunique() >= 100, (t, long["id"].nunique())
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()
        assert len(t) <= 40, t

        long = long[["id", "item", "resp"] + cov_cols]

        # gate before writing -- the contract check requires the validator to
        # run in-script, not just on the output file
        checks = run_qc(long, permitted_values={i: list(range(lo, hi + 1))
                                                for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (t, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {t} {c.name}: {c.detail[:140]}")

        long.to_csv(os.path.join(OUT_DIR, t + ".csv"), index=False)
        total += len(long)
        print(f"{t}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")

    print(f"{len(blocks)} tables, {total} responses "
          f"(two of them partial-credit achievement tests)")


if __name__ == "__main__":
    convert()
