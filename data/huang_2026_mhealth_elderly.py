#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0361137
# DOI: 10.1371/journal.pone.0361137
# Paper: Huang, T., & Cai, W. (2026). Factors influencing elderly people's
#   intentions to use smartphone mHealth apps: quantitative research.
#   PLOS ONE 21(10): e0361137.
# Data: journal.pone.0361137.s002 (S2 File, .csv), 263 rows x 30 columns.
# License: CC BY 4.0 -- Supporting Information of the article itself.
# 263 adults aged 60+ in Zhanjiang City, Guangdong, with smartphone and
# mHealth app experience (288 distributed, 25 excluded).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# EIGHT output tables, 24 items, 6,312 responses, zero missing cells. The
# paper: 7-point Likert, 1 "totally disagree" to 7 "totally agree".
#
# AN UNUSUALLY WELL-DOCUMENTED DEPOSIT, and all three parts check out:
#  * The column names carry a running item number AND the construct code
#    ("T1PCON1" ... "T24PRisk3"), so the eight blocks of three are explicit.
#  * S1 File lists all 24 items under their construct headings with their
#    literature source, three per construct in the deposit's own order, so
#    item text ships -- see huang_2026_mhealth_elderly_itemtext.py.
#  * Every published covariate distribution reproduces EXACTLY, in the
#    article's printed order, which is what licenses shipping the codes
#    labelled rather than as opaque indices:
#        gender      136 / 127          -> 1 male, 2 female
#        age         147 / 100 / 16     -> 1 60-69, 2 70-79, 3 80+
#        education   155 / 88 / 20      -> 1 junior high or lower,
#                                          2 high school, 3 bachelor's+
#        smartphone  17 / 44 / 99 / 103 -> 1 0-1yr, 2 1-3yr, 3 3-5yr, 4 >5yr
#    Twelve category counts, twelve exact hits.
#
# THE ARTICLE ONLY STATES TWO OF THE EIGHT ITEM COUNTS (behavioural intention
# 3, perceived quality 3) and the total, 24. The deposit's own numbering gives
# 3 for every construct and 8 x 3 = 24 matches the stated total, so the split
# is forced by arithmetic rather than assumed.
#
# ONE COVARIATE IS NOT PINNED AND SHIPS AS A BAND INDEX: T29, mHealth app
# experience (4 levels, 95/106/48/14). The article reports a smartphone
# experience distribution that matches T28 exactly but publishes nothing for
# a second experience variable, so T29's bands are unlabelled. It ships
# because the column name states what it measures and the levels are ordered;
# the description says the cut-points are unknown.
#
# PERCEIVED RISK POINTS THE OTHER WAY, by construction rather than by reverse
# coding: its three items ask about privacy disclosure, misuse of personal
# information and payment risk, so a high score is a worse perception where a
# high score on the other seven constructs is a better one. No item is
# reverse-keyed within any block, so no recoding is applied -- but anyone
# summing across constructs needs to know.
#
# `id` is the deposit's `Number`, 1..263, verified unique.
#
# PII: screened over all 30 columns. Every one is numeric.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("HUANGMH_RAW", "journal.pone.0361137_S2_File.csv")

N_ROWS = 263
LO, HI = 1, 7

CONSTRUCTS = {
    "PCON": ("huang_2026_mh_convenience", "Perceived convenience"),
    "PQ": ("huang_2026_mh_quality", "Perceived quality"),
    "PU": ("huang_2026_mh_usefulness", "Perceived usefulness"),
    "PEOU": ("huang_2026_mh_ease_of_use", "Perceived ease of use"),
    "ATT": ("huang_2026_mh_attitude", "Attitude"),
    "BI": ("huang_2026_mh_intention", "Behavioural intention"),
    "PTrust": ("huang_2026_mh_trust", "Perceived trust"),
    "PRisk": ("huang_2026_mh_risk",
              "Perceived risk (high = worse, unlike the other seven)"),
}
COVS = {"T25@23Gender": "cov_gender", "T26@24Age": "cov_age_band",
        "T27@25Education": "cov_education",
        "T28@26Experience": "cov_smartphone_experience",
        "T29@YidongyiliaoExperience": "cov_mhealth_experience_band"}
PINNED = {"T25@23Gender": [136, 127], "T26@24Age": [147, 100, 16],
          "T27@25Education": [155, 88, 20],
          "T28@26Experience": [17, 44, 99, 103]}
HEADER = re.compile(r"^T\d+(PCON|PQ|PEOU|PU|ATT|BI|PTrust|PRisk)(\d+)$")


def parse_headers(df):
    """column -> item code, dropping the running T-number. Shared with the
    item-text build so the two cannot drift."""
    out = {}
    for c in df.columns:
        m = HEADER.match(str(c).strip())
        if m:
            out[c] = m.group(1) + m.group(2)
    return out


def convert():
    df = pd.read_csv(RAW)
    assert len(df) == N_ROWS, len(df)
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert not strings, f"unexpected string column(s): {strings}"
    print(f"PII screen: 0 string columns of {len(df.columns)}")

    codes = parse_headers(df)
    assert len(codes) == 24, len(codes)
    blocks = {}
    for col, code in codes.items():
        blocks.setdefault(re.sub(r"\d+$", "", code), []).append((code, col))
    assert {k: len(v) for k, v in blocks.items()} == \
        {k: 3 for k in CONSTRUCTS}, {k: len(v) for k, v in blocks.items()}
    print("8 constructs x 3 items = 24, matching the article's stated total; "
          "the article itself states only two of the eight counts")

    accounted = {"Number"} | set(COVS) | set(codes)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"

    for col, counts in PINNED.items():
        got = df[col].value_counts().sort_index().tolist()
        assert got == counts, (
            f"{col} is {got}, not the published {counts} -- the covariate "
            f"LABELS rest on this match")
    print("all 12 published covariate category counts reproduce exactly in "
          "the article's printed order, so the codes ship labelled")

    assert df["Number"].nunique() == len(df), "Number is not unique"
    df = df.rename(columns={"Number": "id", **COVS})
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, (name, label) in CONSTRUCTS.items():
        pairs = sorted(blocks[prefix], key=lambda p: int(p[0][len(prefix):]))
        cols = [c for _, c in pairs]
        ren = {c: code for code, c in pairs}
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all() and vals.between(LO, HI).all(), \
            (name, sorted(vals.unique()))

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["item"] = long["item"].map(ren)
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == 3
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
              f"items=3 resp={long['resp'].min()}-{long['resp'].max()}  "
              f"[{label}]")

    assert total == 24 * N_ROWS, total
    print(f"8 tables, {total} responses (24 items x {N_ROWS} respondents "
          f"aged 60+)")


if __name__ == "__main__":
    convert()
