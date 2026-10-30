#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0299231
# DOI: 10.1371/journal.pone.0299231
# Paper: Li, Y., Yang, D., & Liu, S. (2024). The impact of environmental
#   education at Chinese Universities on college students' environmental
#   attitudes. PLOS ONE 19(2): e0299231.
# Data: journal.pone.0299231.s001 (S1 File, .xlsx), 398 rows x 21 columns.
# License: CC BY 4.0 -- Supporting Information of the article itself.
# 398 Chinese college students, online survey 24-29 May 2023 (400 collected,
# 2 removed as invalid).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# FOUR output tables, 16 items, 6,368 responses, zero missing cells. The
# paper: five-point, 1 "strongly disagree" to 5 "strongly agree".
#
#   EA   4  Environmental attitudes
#   SN   3  Subjective norms
#   PBC  4  Perceived behavioural control
#   CE   5  School curriculum education
#
# THE PAPER CALLS THE FOURTH CONSTRUCT SCE AND THE DEPOSIT CALLS IT CE, which
# is recorded rather than silently harmonised. The article's abbreviation for
# "school curriculum education" is SCE throughout; the data's columns are
# CE1..CE5. There is no other candidate construct for them -- the paper names
# exactly four and the other three prefixes match exactly -- so the identity is
# certain, but the item codes ship as the DEPOSIT writes them (CE), because
# renaming a column to match prose is the kind of silent edit that makes a
# table disagree with its own source.
#
# PBC HAS A DUPLICATE COLUMN NAME IN THE SOURCE: the four perceived-behavioural-
# control columns are headed PBC1, PBC2, PBC4, PBC4. pandas disambiguates the
# second to `PBC4.1`, so nothing is lost, but the source numbering skips 3 and
# repeats 4. PBC3 is the obvious intent and is NOT assumed: the second PBC4
# ships as `PBC4_dup` rather than being renamed PBC3, so no item carries a code
# the deposit did not give it. Flagged in the description; a user joining to a
# future item-text table needs to know this one code is ambiguous.
#
# ALL FOUR COVARIATES SHIP WITH MEANINGS, NOT JUST BAND INDICES, because every
# one is pinned exactly against the paper's published percentages -- all four
# distributions reproduce to the decimal, in the paper's own printed order:
#     Gender     214 / 184   = 53.8% / 46.2%  -> 1 male, 2 female
#     Degree     182/186/30  = 45.7/46.7/7.5  -> 1 specialized, 2 undergraduate,
#                                                3 master's or doctoral
#     Hometown   218 / 180   = 54.8% / 45.2%  -> 1 rural, 2 city
#     Expenses   91/203/75/29 = 22.9/51.0/18.8/7.3 -> 1 under RMB1,500,
#                                                2 1,500-2,000, 3 2,001-3,000,
#                                                4 above 3,000
# Twelve category counts, twelve exact hits. That is enough to label the codes
# rather than ship them as opaque indices, and the assertions below make the
# labelling fail loudly if the file changes.
#
# `id` is the deposit's `No.`, 1..398, verified unique.
#
# Item text: NOT SHIPPED. The items are adapted from earlier studies and the
# article's Table 2 is published only as an image, so no wording is
# recoverable. An availability gap.
#
# PII: screened over all 21 columns. Every one is numeric.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LIEE_RAW", "journal.pone.0299231_S1_File.xlsx")

N_ROWS = 398
LO, HI = 1, 5

CONSTRUCTS = {
    "EA": ("li_2024_ee_attitudes", 4, "Environmental attitudes"),
    "SN": ("li_2024_ee_subjective_norms", 3, "Subjective norms"),
    "PBC": ("li_2024_ee_behavioral_control", 4,
            "Perceived behavioural control"),
    "CE": ("li_2024_ee_curriculum_education", 5,
           "School curriculum education (the paper's SCE)"),
}
COVS = {"Gender": "cov_gender", "Current Degree": "cov_degree",
        "Hometown Location": "cov_hometown",
        "Monthly living expenses": "cov_living_expenses_band"}
# every published category count, which is what licenses labelling the codes
PINNED = {"Gender": [214, 184], "Current Degree": [182, 186, 30],
          "Hometown Location": [218, 180],
          "Monthly living expenses": [91, 203, 75, 29]}


def convert():
    df = pd.read_excel(RAW)
    assert len(df) == N_ROWS, len(df)
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert not strings, f"unexpected string column(s): {strings}"
    print(f"PII screen: 0 string columns of {len(df.columns)}")

    blocks = {}
    for c in df.columns:
        m = re.fullmatch(r"(EA|SN|PBC|CE)(\d+)(\.\d+)?", str(c).strip())
        if m:
            blocks.setdefault(m.group(1), []).append(c)
    got = {k: len(v) for k, v in blocks.items()}
    want = {k: v[1] for k, v in CONSTRUCTS.items()}
    assert got == want, f"construct counts are {got}, expected {want}"
    # the source numbering skips PBC3 and repeats PBC4 -- assert it rather
    # than quietly renaming, see the header
    assert sorted(str(c) for c in blocks["PBC"]) == \
        ["PBC1", "PBC2", "PBC4", "PBC4.1"], sorted(blocks["PBC"])
    print("PBC columns are PBC1, PBC2, PBC4, PBC4 in the source (pandas "
          "renames the second to PBC4.1). PBC3 is the obvious intent and is "
          "NOT assumed: the duplicate ships as PBC4_dup")

    accounted = {"No."} | set(COVS)
    for cols in blocks.values():
        accounted |= set(cols)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"

    for col, counts in PINNED.items():
        got_c = df[col].value_counts().sort_index().tolist()
        assert got_c == counts, (
            f"{col} is {got_c}, not the paper's {counts} -- the covariate "
            f"LABELS rest on this match, so do not ship them labelled")
    print("all 12 covariate category counts reproduce the paper's published "
          "percentages exactly, in its printed order, so the codes ship "
          "labelled (1 male / 1 rural / 1 specialized / 1 under RMB1,500)")

    assert df["No."].nunique() == len(df), "No. is not unique"
    df = df.rename(columns={"No.": "id", **COVS})
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, (name, n, label) in CONSTRUCTS.items():
        cols = sorted(blocks[prefix], key=lambda c: str(c))
        ren = {c: (str(c).replace(".1", "_dup") if ".1" in str(c) else str(c))
               for c in cols}
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all() and vals.between(LO, HI).all(), \
            (name, sorted(vals.unique()))

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["item"] = long["item"].astype(str).map(ren)
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name
        long = long[["id", "item", "resp"] + cov_cols]

        checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                                for i in long["item"].unique()})
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

    assert total == 16 * N_ROWS, total
    print(f"4 tables, {total} responses (16 items x {N_ROWS} respondents)")


if __name__ == "__main__":
    convert()
