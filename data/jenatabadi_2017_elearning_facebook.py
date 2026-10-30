#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0182311
# DOI: 10.1371/journal.pone.0182311
# Paper: Salarzadeh Jenatabadi, H., Moghavvemi, S., Wan Mohamed Radzi,
#   C. W. J. B., Babashamsi, P., & Arashi, M. (2017). Testing students'
#   e-learning via Facebook through Bayesian structural equation modeling.
#   PLOS ONE 12(9): e0182311.
# Data: journal.pone.0182311.s001 (S1 Data, .xls), 170 rows x 44 columns
#   under a TWO-ROW header.
# License: CC BY 4.0 -- Supporting Information of the article itself.
# 170 bachelor students in a business statistics class at the Faculty of
# Business and Accountancy, University of Malaya.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# EIGHT output tables, 43 items, 7,310 responses, zero missing cells.
#
# THE FILE HAS A TWO-ROW HEADER and the two rows carry different information:
# row 1 names the CONSTRUCT once, above its first item ("Performance
# Expectancy" over column 1, "Effort Expectancy" over column 6, ...), and row
# 2 names every ITEM (PE1..PE5, EF1..EF4, ...). Reading with the default
# single header row gives eight named columns and thirty-five called
# "Unnamed: n", which is how this deposit looks like a mess and is not one.
# Both rows are used here: the construct names come from row 1 and the item
# codes from row 2, so neither the blocks nor the codes are inferred.
#
#   PE     5  Performance expectancy     SI      4  Social influence
#   EF     4  Effort expectancy          Habit   4  Habit
#   FC     5  Facilitating conditions    ITU    11  Intention to use
#   HM     6  Hedonic motivation         UB      4  Use behaviour
#
# THE ARTICLE CONTRADICTS ITSELF ABOUT THE RESPONSE SCALE, and both halves of
# the contradiction matter, so both ship in the description. It says:
# "seven-point Likert scale (1 = strongly agree to 5 = strongly disagree)".
#   * SEVEN POINTS IS WRONG, or at least not what was deposited: all 43
#     columns run 1-5 with all five levels used.
#   * 1 = STRONGLY AGREE IS BACKWARDS relative to the usual convention, and
#     it is the only direction statement the article makes. If it is right,
#     a HIGH resp in these tables means DISAGREEMENT -- the opposite of every
#     other table in this batch. If it is a slip of the pen like the
#     seven-point claim, the direction is the usual one.
# Nothing in the data can distinguish those, so resp ships exactly as
# deposited and the description states the problem rather than picking a side.
# This is the third scale-direction case in this batch (li_2024_deg_*, where
# the prose revealed a genuinely reversed scale; li_2024_vr_*, where the
# article said nothing at all) and it is the strongest argument yet for the
# standing suggestion that `datastandard.md` require scale direction to be
# positively confirmed.
#
# THREE CELLS IN THIS FILE MAY BE IMPUTED AND THERE IS NO WAY TO SAY WHICH.
# The article reports that "three missing values were replaced with variable
# medians". The deposit has zero missing cells across 7,310, so either the
# replacement is already baked in or the three were never missing here.
# Flagged in the description; 3 cells in 7,310 is immaterial to most uses but
# not to someone studying missingness.
#
# N IS 170 AND THE ARTICLE IS UNCLEAR ABOUT ITS OWN ANALYSIS SET. It says five
# outliers (cases 18, 36, 48, 101, 127) were deleted, which would leave 165,
# and then refers to "the 170 questionnaires". The deposit holds all 170 with
# `No` running 1..170, so it is the PRE-exclusion file and all 170 ship. The
# five case numbers are recorded here so anyone wanting the article's analysis
# set can reproduce it.
#
# NO COVARIATES: the deposit is the case number plus the 43 item columns. The
# article says no identifying information was collected.
#
# Item text: NOT SHIPPED. The article does not print the items and attributes
# them to Venkatesh, Thong & Xu (2012) -- the UTAUT2 instrument. This is the
# fifth UTAUT/TAM-family deposit in the batch; no new register row, the
# standing TODO asking for a general ruling on that item pool covers it.
#
# PII: screened over all 44 columns. Every one is numeric.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("JENATABADI_RAW", "journal.pone.0182311_S1_Data.xls")

N_ROWS = 170
LO, HI = 1, 5
OUTLIERS = [18, 36, 48, 101, 127]   # the article's, NOT applied here

# row-1 construct label -> (table, expected items)
CONSTRUCTS = {
    "Performance Expectancy": ("jenatabadi_2017_fb_perf_expectancy", 5),
    "Effort Expectancy": ("jenatabadi_2017_fb_effort_expectancy", 4),
    "Facilitating Conditions": ("jenatabadi_2017_fb_facilitating_cond", 5),
    "Hedonic Motivation": ("jenatabadi_2017_fb_hedonic_motivation", 6),
    "Social Influence": ("jenatabadi_2017_fb_social_influence", 4),
    "Habit": ("jenatabadi_2017_fb_habit", 4),
    "Intention to Use": ("jenatabadi_2017_fb_intention_to_use", 11),
    "Use Behavior": ("jenatabadi_2017_fb_use_behavior", 4),
}


def read_two_row_header():
    """Row 1 names each construct over its first item; row 2 names the items.
    Returns (dataframe keyed by item code, construct -> [item codes])."""
    raw = pd.read_excel(RAW, header=None)
    labels, codes = raw.iloc[0], raw.iloc[1]
    blocks, current = {}, None
    for j in range(1, raw.shape[1]):
        if pd.notna(labels.iloc[j]):
            current = str(labels.iloc[j]).strip()
            blocks[current] = []
        assert current is not None, f"column {j} precedes any construct label"
        assert pd.notna(codes.iloc[j]), f"column {j} has no item code"
        blocks[current].append(str(codes.iloc[j]).strip())
    body = raw.iloc[2:].dropna(how="all").reset_index(drop=True)
    body.columns = ["No"] + [str(c).strip() for c in codes.iloc[1:]]
    return body, blocks


def convert():
    df, blocks = read_two_row_header()
    assert len(df) == N_ROWS, len(df)
    got = {k: len(v) for k, v in blocks.items()}
    want = {k: v[1] for k, v in CONSTRUCTS.items()}
    assert got == want, f"construct counts are {got}, expected {want}"
    assert sum(got.values()) == 43, sum(got.values())
    print(f"two-row header parsed: {len(blocks)} constructs from row 1, "
          f"43 item codes from row 2")

    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert not strings, f"unexpected string column(s): {strings}"
    print(f"PII screen: 0 string columns of {len(df.columns)}")

    items = [c for cols in blocks.values() for c in cols]
    assert int(df[items].isna().sum().sum()) == 0, "missing cells"
    vals = pd.to_numeric(df[items].stack(), errors="coerce")
    assert vals.notna().all(), "a non-numeric response"
    assert vals.between(LO, HI).all(), sorted(vals.unique())
    assert set(vals.unique()) == {1, 2, 3, 4, 5}, (
        f"observed levels are {sorted(vals.unique())}; the header says all "
        f"five are used against the article's 'seven-point' claim, so recheck")
    print("observed range is 1-5 on all 43 items with all five levels used, "
          "against the article's 'seven-point Likert scale (1 = strongly "
          "agree to 5 = strongly disagree)' -- the point count is wrong and "
          "the stated direction is BACKWARDS from the usual convention. resp "
          "ships as deposited; see the header")

    assert df["No"].nunique() == len(df), "No is not unique"
    assert set(OUTLIERS) <= set(df["No"]), (
        "the article's five outlier cases are not all present; this may not "
        "be the pre-exclusion file the header describes")
    print(f"all {N_ROWS} cases ship, including the article's five deleted "
          f"outliers {OUTLIERS} -- this is the pre-exclusion file")
    df = df.rename(columns={"No": "id"})

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for label, (name, n) in CONSTRUCTS.items():
        cols = blocks[label]
        long = df.melt(id_vars=["id"], value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name
        long = long[["id", "item", "resp"]]

        checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                                for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}  [{label}]")

    assert total == 43 * N_ROWS, total
    print(f"8 tables, {total} responses (43 items x {N_ROWS} students)")


if __name__ == "__main__":
    convert()
