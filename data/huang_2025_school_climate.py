#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0321726
# DOI: 10.1371/journal.pone.0321726
# Paper: Huang, Z., Chen, W., Peng, B., & Yan, H. (2025). Exploring the
#   mechanisms linking perceived school climate to negative emotions in
#   adolescents: The mediating roles of social avoidance and distress, and
#   psychological resilience, with physical exercise level as a moderator.
#   PLOS ONE 20(5).
# Data: journal.pone.0321726.s001 (S1 File, .xlsx), single sheet, 1,507 rows x
#   108 columns (ID, Gender, Grade, Family, Q1..Q104).
# License: CC BY 4.0 (Crossref licence record for the version of record,
#   http://creativecommons.org/licenses/by/4.0/; the data is a Supporting
#   Information file of the article itself, not a third-party deposit).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# FOUR output tables. 1,507 students in grades 5-9 across China, stratified
# random sampling.
#
# THE ITEM LABELS ARE OPAQUE AND THE BLOCKS ARE INFERRED -- read this before
# trusting the split. The file names its items Q1..Q104 and carries no block
# markers, so which instrument each column belongs to is not in the data. The
# paper states the composition exactly: "The survey instrument used in this
# study includes a total of 107 items: Perceived school climate scale (25
# items), negative emotions scale (21 items), social avoidance and distress
# scale (28 items), psychological resilience scale (27 items), and physical
# exercise level scale (3 items)." That is 25+21+28+27+3 = 104, which is
# exactly the number of Q columns (the paper's own "107" is its arithmetic
# slip, not a missing block).
#
# Taking them in the printed order gives Q1-25 / Q26-46 / Q47-74 / Q75-101 /
# Q102-104, and the DATA CONFIRMS THAT ORDERING INDEPENDENTLY rather than
# merely permitting it: the social avoidance scale is the only one scored on a
# 2-point scale (1 = No, 2 = Yes), and the columns whose observed domain is
# exactly {1,2} are Q47..Q74 -- 28 columns, beginning and ending precisely
# where the printed order says they should. The asserts below pin all three
# boundaries this way (1-4, then 1-2, then 1-5), so a future re-read cannot
# drift. What this does NOT establish is the order of items WITHIN a block;
# nothing in the deposit could, and no item text is shipped, so nothing depends
# on it.
#
# ONE STRAY CELL, dropped. Q3 holds a single value of 5 (one row of 1,507)
# against a documented 4-point scale, and no other column in either 4-point
# block contains a 5. A value out of range on exactly one item, in exactly one
# cell, is a data-entry error rather than a wider scale -- so that one cell is
# dropped and the other 24 responses from that respondent are kept. Asserted
# below as exactly one cell, so if a future file genuinely uses 1-5 for this
# block the assertion fires instead of silently discarding real data.
#
# NOT shipped: the 3-item physical exercise level scale (Q102-Q104), on two
# grounds that compound. The paper says its frequency item was "rated from 0
# (never) to 4 (always)" while intensity and duration were rated 1-5; all three
# deposited columns in fact run 1-5, so the deposit and the paper disagree
# about the anchors of at least one of the three. And the published measure is
# a PRODUCT of the three ratings (total 0-100), not a summed Likert battery, so
# the three columns are facets of an index rather than items of a scale. Three
# items, one unresolved anchor discrepancy: excluded on the err-on-exclusion
# rule. Noted in BATCH_LOG rather than silently dropped.
#
# ALREADY REVERSE-CODED AT SOURCE. The paper: "Reverse-scored items across the
# scales were adjusted to ensure consistency in positive scoring." So these
# columns are not raw keypresses -- they are the authors' direction-corrected
# values, and for the reverse-keyed items the number in resp is not the
# category the student picked. Stated in the table descriptions, because it
# changes what a reverse-item analysis of these tables would mean.
#
# Item text: NOT shipped, for ALL four tables, and this is an availability
# problem rather than only a rights one. The columns are Q1..Q104 with no
# wording anywhere in the deposit, and the article does not print the item
# stems -- it cites each instrument instead. All four are third-party
# instruments: perceived school climate (Jia et al. 2009), DASS-21 (Chinese
# version validated by Gong et al. 2010; the instrument is Lovibond &
# Lovibond's), the Social Avoidance and Distress Scale (Watson & Friend 1969),
# and the Adolescent Psychological Resilience Scale (Hu & Gan 2008). Even with
# wording in hand there would be no deposit-side key tying stem to column, so
# no mapping is possible from this source. Register rows are written with this
# batch. Administration was in Chinese; `language` is Chinese.
#
# PII: screened over every column. The file is entirely numeric -- ID (a
# sequential record number), three coded demographics, and the 104 item
# columns. No names, emails, dates, free text, or geography; `Family` is a
# binary family-location code, not a place name.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("HUANG_RAW", "journal.pone.0321726_S1_File.xlsx")

N_ROWS = 1507

# name, columns, (lo, hi) -- order and counts are the paper's, boundaries are
# asserted against the observed domains below
BLOCKS = [
    ("huang_2025_school_climate", [f"Q{i}" for i in range(1, 26)], (1, 4)),
    ("huang_2025_dass21", [f"Q{i}" for i in range(26, 47)], (1, 4)),
    ("huang_2025_social_avoidance", [f"Q{i}" for i in range(47, 75)], (1, 2)),
    ("huang_2025_resilience", [f"Q{i}" for i in range(75, 102)], (1, 5)),
]
# Q102-Q104 deliberately absent -- see the header
EXCLUDED = [f"Q{i}" for i in range(102, 105)]

COVS = {"Gender": "cov_gender", "Grade": "cov_grade",
        "Family": "cov_family_location"}
DROP = {"ID": "sequential record number -- becomes id"}


def screen_for_pii(df):
    txt = [c for c in df.columns
           if pd.api.types.is_string_dtype(df[c])
           and pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert not txt, f"unexpected text column(s) -- screen them: {txt}"
    assert all(pd.to_numeric(df[c], errors="coerce").notna().all()
               for c in df.columns), "a non-numeric column escaped the screen"
    print("  every column parses as a number -- no free text, name, email, "
          "date or geographic column exists in this file")


def check_block_boundaries(df):
    """The printed order is only a claim until the observed domains agree with
    it. The 2-point block is the discriminating one: assert that the columns
    whose domain is exactly {1,2} are precisely the 28 the order predicts."""
    two = sorted((c for c in df.columns
                  if str(c).startswith("Q")
                  and set(df[c].dropna().unique().tolist()) == {1, 2}),
                 key=lambda c: int(str(c)[1:]))
    expect = [f"Q{i}" for i in range(47, 75)]
    assert two == expect, (
        "the 2-point block is not where the paper's item order puts it; "
        f"found {two[:3]}..{two[-3:]} ({len(two)} columns)")
    print(f"block boundaries confirmed: the {len(two)} columns with domain "
          f"{{1,2}} are exactly {expect[0]}..{expect[-1]}, as the paper's "
          f"25/21/28/27/3 ordering predicts")


def fix_stray_cell(df):
    """Q3 carries one 5 against a documented 4-point scale. Assert it is a
    single cell before discarding it, so a genuinely 1-5 block would fail here
    rather than lose real responses."""
    four = [c for b in BLOCKS[:2] for c in b[1]]
    stray = {c: int((df[c] > 4).sum()) for c in four if (df[c] > 4).any()}
    assert stray == {"Q3": 1}, f"unexpected out-of-range cells: {stray}"
    df.loc[df["Q3"] > 4, "Q3"] = pd.NA
    print("dropped 1 cell: Q3 = 5 on a documented 4-point scale, the only "
          "out-of-range value in either 4-point block (data-entry error)")
    return df


def convert():
    df = pd.read_excel(RAW, sheet_name=0)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    accounted = set(COVS) | set(DROP) | set(EXCLUDED)
    for _, cols, _ in BLOCKS:
        accounted |= set(cols)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    assert sum(len(c) for _, c, _ in BLOCKS) + len(EXCLUDED) == 104

    check_block_boundaries(df)
    df = fix_stray_cell(df)

    assert df["ID"].nunique() == len(df), "ID is not unique"
    df = df.rename(columns={"ID": "id", **COVS})
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, cols, (lo, hi) in BLOCKS:
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)

        assert long["resp"].between(lo, hi).all(), (name, long["resp"].unique())
        # every documented level must actually appear, or the block is mislabelled
        assert set(long["resp"].unique()) == set(range(lo, hi + 1)), \
            (name, sorted(long["resp"].unique()))
        assert long["id"].nunique() >= 100, (name, long["id"].nunique())
        assert long["item"].nunique() == len(cols), (name, long["item"].nunique())
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name

        long = long[["id", "item", "resp"] + cov_cols]

        # gate before writing -- the contract check requires the validator to
        # run in-script, not just on the output file
        checks = run_qc(long, permitted_values={i: list(range(lo, hi + 1))
                                                for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:170]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")

    assert total == 101 * N_ROWS - 1, total
    print(f"4 tables, {total} responses "
          f"(101 items x {N_ROWS} respondents, less the one dropped cell)")


if __name__ == "__main__":
    convert()
