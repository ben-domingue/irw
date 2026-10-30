#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0358753
# DOI: 10.1371/journal.pone.0358753
# Paper: Zhu, T., & Wang, Y. (2026). Live-streaming interaction and young
#   consumers' identification with time-honored brands: the roles of emotional
#   arousal and relationship strength. PLOS ONE 21(9): e0358753.
# Data: journal.pone.0358753.s001 (S1 Data, .xlsx), 415 rows x 35 columns.
# License: CC BY 4.0 -- Supporting Information of the article itself.
# 415 Chinese consumers aged 18-40 who had watched an e-commerce live-stream
# of a time-honored brand in the previous six months (Wenjuanxing panel,
# 2 June - 30 September 2025).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# SEVEN output tables, 28 items, 11,620 responses, zero missing cells. The
# paper: five-point agreement, 1 "strongly disagree" to 5 "strongly agree".
#
# THE PREFIXES ARE THE PAPER'S OWN, matching the Fig 1 legend construct for
# construct and count for count -- nothing inferred:
#   PTIN 3  Product interaction
#   ILIN 3  Interpersonal interaction
#   SLPE 4  Social presence
#   ATHB 6  Perceived authenticity of time-honored brands
#   SSCR 5  Consumer-streamer relationship strength
#   ELAL 4  Emotional arousal
#   ITHB 3  Identification with time-honored brands
#
# EMOTIONAL AROUSAL IS A SEMANTIC DIFFERENTIAL, NOT AN AGREEMENT SCALE, which
# is why it is called out rather than left to be assumed. The paper measures
# ELAL with "four five-point semantic differential items" where a higher score
# means greater arousal; the other six constructs are agreement items. Both run
# 1-5 in the file and are therefore indistinguishable in the data. The adjective
# anchors are not stated in the article's readable text (Table 2 is an image),
# so the table ships with the response format recorded in its description
# instead -- someone pooling ELAL with the agreement constructs should know
# they are not the same scale.
#
# FOUR COVARIATES SHIP AND TWO DO NOT. All six are integer codes with no
# legend, so the test is whether the column NAME fixes what the number means:
#   SHIPPED -- Age (4), Edu (5), Income (5), Frequency (3): ordered bands. The
#     cut-points are not published in readable text, but the ORDER is implied
#     by the name, so the codes are usable as an ordinal covariate. Said in the
#     description: these are band indices, not years or yuan.
#   DROPPED -- Gender (1/2: which is which is not stated anywhere readable) and
#     Employment (5 nominal occupation categories with no legend, so the codes
#     carry no recoverable meaning at all). Same rule as diop_2019's GENDER
#     earlier in this batch.
#
# `id` is the deposit's `No.`, unique across all 415 rows; it runs to 434 with
# gaps, which is consistent with the paper's 492 submissions minus exclusions
# rather than a defect.
#
# Item text: NOT SHIPPED. Table 2 "Measurement items and sources" exists but is
# published only as an image, and the items are adapted from prior marketing
# scales rather than study-authored. No wording is recoverable, so this is an
# availability gap; no register row is written (the TODO asking for a general
# ruling on the adapted-marketing-scale pool covers it).
#
# PII: screened over all 35 columns. Every one is numeric; no names, emails,
# dates, free text or geography.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ZHU_RAW", "journal.pone.0358753_S1_Data.xlsx")

N_ROWS = 415
LO, HI = 1, 5

CONSTRUCTS = {
    "PTIN": ("zhu_2026_lsb_product_interaction", 3, "Product interaction"),
    "ILIN": ("zhu_2026_lsb_interpersonal_interact", 3,
             "Interpersonal interaction"),
    "SLPE": ("zhu_2026_lsb_social_presence", 4, "Social presence"),
    "ATHB": ("zhu_2026_lsb_brand_authenticity", 6,
             "Perceived authenticity of time-honored brands"),
    "SSCR": ("zhu_2026_lsb_streamer_relationship", 5,
             "Consumer-streamer relationship strength"),
    "ELAL": ("zhu_2026_lsb_emotional_arousal", 4,
             "Emotional arousal (semantic differential, not agreement)"),
    "ITHB": ("zhu_2026_lsb_brand_identification", 3,
             "Identification with time-honored brands"),
}
COVS = {"Age": "cov_age_band", "Edu": "cov_education_band",
        "Income": "cov_income_band", "Frequency": "cov_viewing_frequency"}
DROP = {"Gender": "1/2 with no statement anywhere readable of which is which",
        "Employment": "5 nominal occupation codes with no legend"}


def screen_for_pii(df):
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(strings)} string column(s) of {len(df.columns)}")
    assert not strings, f"unexpected string column(s) -- screen them: {strings}"
    print("  every column is numeric; no name, email, date, free text or "
          "geographic column in this file")


def convert():
    df = pd.read_excel(RAW)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    found = {}
    for c in df.columns:
        m = re.fullmatch(r"([A-Z]{4})(\d+)", str(c).strip())
        if m:
            found.setdefault(m.group(1), []).append(c)
    got = {k: len(v) for k, v in found.items()}
    want = {k: v[1] for k, v in CONSTRUCTS.items()}
    assert got == want, f"construct counts are {got}, expected {want}"

    accounted = {"No."} | set(COVS) | set(DROP)
    for cols in found.values():
        accounted |= set(cols)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    print("dropped 2 covariates: " +
          "; ".join(f"{k} ({v})" for k, v in DROP.items()))

    assert df["No."].nunique() == len(df), "No. is not unique"
    df = df.rename(columns={"No.": "id", **COVS})
    cov_cols = sorted(COVS.values())
    for c in cov_cols:
        assert df[c].min() == 1, (c, "band codes no longer start at 1")

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, (name, n, label) in CONSTRUCTS.items():
        cols = sorted(found[prefix], key=lambda c: int(re.sub(r"\D", "", c)))
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all(), (name, "a non-numeric response")
        assert vals.between(LO, HI).all(), (name, sorted(vals.unique()))
        assert (vals % 1 == 0).all(), (name, "a fractional response")

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name
        long = long[["id", "item", "resp"] + cov_cols]

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

    assert total == 28 * N_ROWS, total
    print(f"7 tables, {total} responses (28 items x {N_ROWS} respondents)")


if __name__ == "__main__":
    convert()
