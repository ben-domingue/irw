#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0319246
# DOI: 10.1371/journal.pone.0319246
# Paper: Zhang, K., Yang, T., Liu, Z., Yi, C., Hou, Y., & Wu, T. (2025).
#   Effects and functional mechanisms of digital fitness platforms on online
#   fitness payment behavior under the perspective of "She-economy".
#   PLOS ONE 20(3): e0319246.
# Data: journal.pone.0319246.s001 (S1 Table, .xls), 259 rows x 22 columns.
# License: CC BY 4.0 -- Supporting Information of the article itself.
# 259 Chinese women recruited by snowball sampling online (Keep, WeChat
# fitness communities) and offline (a running group, a triathlon club, a
# Pilates and yoga club), March-April 2024.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# FIVE output tables, 16 items, 4,144 responses, zero missing cells. The
# deposit names its own constructs in the column headers ("perceived
# usefulness1", "Online Fitness Paying behavior3"), so no block inference.
#
# SATISFACTION IS NOT SHIPPED: two items only, below IRW's three-item floor.
# The paper lists it as one of its six constructs, so this is a real loss
# rather than an oversight -- same call as diop_2019's two-item attitude scale
# earlier in this batch. 18 items in the deposit, 16 shipped.
#
# THE PAPER'S ITEM SPLIT IS VAGUER THAN THE DEPOSIT'S, and the deposit wins
# because it is explicit. The article says "perceived ease of use and
# perceived usefulness: 6 items" without saying how they divide; the headers
# say 3 and 3. The article's other counts (enjoyment 4, satisfaction 2,
# continuance 3, payment behaviour 3) match the headers exactly, and 3+3+4+2+
# 3+3 = 18 = the number of item columns, so the split is forced.
#
# THE COVARIATE CODES ARE PINNED AGAINST PUBLISHED PERCENTAGES. The deposit
# codes education 1-4 while the paper summarises only three bands, which is
# the kind of mismatch that sank xu_2026's covariates earlier today -- so it
# was checked rather than assumed. Two levels land exactly:
#     education 3 = 119 of 259 = 45.95%, the paper's bachelor's degree
#     education 4 = 105 of 259 = 40.54%, the paper's postgraduate and above
#     frequency 2 = 143 of 259 = 55.21%, the paper's "occasional" use
# Three exact hits to two decimal places. So the codes ascend, the file is the
# analysed data, and the paper's three-band education summary simply collapsed
# the two smallest levels (16 and 19 respondents). All three covariates ship as
# ordered band indices; their cut-points are the paper's, not re-derived.
#
# THE SAMPLE IS ALL WOMEN by design ("She-economy"), so there is no gender
# covariate to ship and its absence is not an omission. Recorded in the
# description, where a constant belongs. Age is not in the deposit at all.
#
# `id` is the deposit's `No.`, 1..259, verified unique.
#
# Item text: NOT SHIPPED. The headers name the CONSTRUCT and the item number
# but carry no wording, and the article's measurement table is an image. The
# items are adapted from Davis (1989) and later TAM work rather than
# study-authored, so this is both an availability gap and a third-party
# question; covered by the existing TODO asking for a general ruling on the
# UTAUT/TAM item pool.
#
# PII: screened over all 22 columns. Every one is numeric.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ZHANGDF_RAW", "journal.pone.0319246_S1_Table.xls")

N_ROWS = 259
LO, HI = 1, 5

# header stem (lower-cased) -> table, expected items, label
CONSTRUCTS = {
    "perceived usefulness": ("zhang_2025_dfp_usefulness", 3,
                             "Perceived usefulness"),
    "perceived ease of use": ("zhang_2025_dfp_ease_of_use", 3,
                              "Perceived ease of use"),
    "perceived enjoyment": ("zhang_2025_dfp_enjoyment", 4,
                            "Perceived enjoyment"),
    "continue using intention": ("zhang_2025_dfp_continuance", 3,
                                 "Continuance intention"),
    "online fitness paying behavior": ("zhang_2025_dfp_payment_behavior", 3,
                                       "Online fitness payment behaviour"),
}
BELOW_FLOOR = ("satisfaction", 2)

COVS = {"educational background": "cov_education_band",
        "Frequency of use of digital fitness platforms": "cov_use_frequency",
        "Duration of each use of  the platform": "cov_use_duration_band"}
# published percentages that pin the codes -- see the header
PINNED = {("educational background", 3): 119,
          ("educational background", 4): 105,
          ("Frequency of use of digital fitness platforms", 2): 143}


def convert():
    df = pd.read_excel(RAW)
    assert len(df) == N_ROWS, len(df)
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert not strings, f"unexpected string column(s): {strings}"
    print(f"PII screen: 0 string columns of {len(df.columns)}")

    def stem(c):
        return re.sub(r"\d+$", "", str(c).strip()).strip().lower()

    blocks = {}
    for c in df.columns:
        s = stem(c)
        if s in CONSTRUCTS or s == BELOW_FLOOR[0]:
            blocks.setdefault(s, []).append(c)
    got = {k: len(v) for k, v in blocks.items()}
    want = {k: v[1] for k, v in CONSTRUCTS.items()}
    want[BELOW_FLOOR[0]] = BELOW_FLOOR[1]
    assert got == want, f"construct counts are {got}, expected {want}"
    assert sum(got.values()) == 18, sum(got.values())
    print(f"NOT shipping {BELOW_FLOOR[0]} ({BELOW_FLOOR[1]} items): below the "
          f"three-item floor, though the paper names it as a construct")

    accounted = {"No."} | set(COVS)
    for cols in blocks.values():
        accounted |= set(cols)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"

    for (col, code), n in PINNED.items():
        got_n = int((df[col] == code).sum())
        assert got_n == n, (
            f"{col}={code} now has {got_n} rows, not the {n} the paper's "
            f"published percentage implies -- the covariate codes are no "
            f"longer pinned, so recheck before shipping them")
    print("covariate codes pinned against published percentages: education "
          "3=119 (45.95%, bachelor's), 4=105 (40.54%, postgraduate), "
          "frequency 2=143 (55.21%, occasional) -- three exact hits")

    assert df["No."].nunique() == len(df), "No. is not unique"
    df = df.rename(columns={"No.": "id", **COVS})
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for s, (name, n, label) in CONSTRUCTS.items():
        cols = sorted(blocks[s], key=lambda c: int(re.search(r"\d+$", str(c))
                                                   .group()))
        ren = {c: re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower())
               for c in cols}
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all() and vals.between(LO, HI).all(), \
            (name, sorted(vals.unique()))
        assert (vals % 1 == 0).all(), (name, "a fractional response")

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["item"] = long["item"].map(ren)
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
    print(f"5 tables, {total} responses (16 items x {N_ROWS} respondents; "
          f"2 satisfaction items withheld below the floor)")


if __name__ == "__main__":
    convert()
