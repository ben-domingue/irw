#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0359881
# DOI: 10.1371/journal.pone.0359881
# Paper: Padchasuwan, N. H., Benchamas, J., Laoraksawong, P., Senahad, N.,
#   Banchonhattakit, P., & Phimha, S. (2026). Development and psychometric
#   validation of the Sexual Health Literacy Measurement Tool for
#   Undergraduate Students (SHL-US) in Thailand. PLOS ONE 21(10).
# Data: journal.pone.0359881.s001 (S1 Dataset, .xlsx). One sheet, whose name is
#   the Thai for "Form responses 1". 1,235 rows x 50 columns.
# License: CC BY 4.0 (Crossref licence record for the version of record; the
#   data is a Supporting Information file of the article itself -- "All
#   relevant data are within the manuscript and its Supporting information
#   file (S1 Dataset)").
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# ONE output table. 1,235 Thai undergraduates; the instrument was administered
# in Thai.
#
# THIS TABLE IS THE 49-ITEM ADMINISTERED FORM, NOT THE PUBLISHED 45-ITEM
# INSTRUMENT -- the single most important thing to know about it, and the
# reason is in the abstract: "Forty-nine items entered the EFA; 47 were
# retained (4 factors, 53.17% variance explained). CFA removed two more
# low-loading items (<0.50), yielding the final 45-item, four-factor
# structure: access (12), understanding (12), appraisal (10), application
# (11)."
#
# The deposit holds all 49 administered items -- AC 14, UN 12, APR 12, APL 11
# -- so the four that the scale-development process discarded are still here,
# and the arithmetic of which subscales lost them is recoverable even though
# the specific item codes are not: access went 14 -> 12 and appraisal 12 -> 10,
# while understanding (12) and application (11) are unchanged. WHICH two items
# each lost is not stated in the article or marked in the data, so no attempt
# is made to drop them.
#
# Shipping all 49 is the right call rather than a shortcut: every one of them
# is a real response that a real undergraduate gave to a real administered
# item, which is exactly what this corpus is for, and a psychometric user is
# better served by the full administered form than by a subset reconstructed
# from an unstated key. But a user who assumes this table IS the SHL-US as
# published would be wrong by four items, so the table description says so
# outright. The assert below pins the 14/12/12/11 split, so if a future
# version of this deposit ships the trimmed form instead, it fails loudly.
#
# ONE table, not four. AC/UN/APR/APL are the four dimensions of the health
# literacy construct the paper defines ("access, understand, appraise, and
# apply information pertaining to sexual health"), measured by one instrument
# on one 4-point scale in one administration. That is a subscale structure, not
# four instruments -- the same shape as hocine_2016_psychosocial_stressors'
# five blocks in this batch. Shipped as one table per the
# collapse-same-instrument rule, with the subscale recoverable from the item
# code prefix.
#
# Clean source, verified rather than assumed: zero missing cells across all 49
# items, every item's observed domain is exactly 1-4, and all four levels
# appear on every item. No sentinel codes, so there is no undeclared
# no-answer value to strip (contrast three of five deposits in 2026-10-29f).
#
# No covariates. The deposit carries ID and the 49 item columns and nothing
# else -- no age, sex, year of study or institution. Worth stating because
# their absence is the deposit's choice, not an omission here.
#
# Item text: NOT SHIPPED, and the obstacle is the MAPPING. Rights are not the
# problem: this is a scale-development paper, the instrument is the authors'
# own, and it arrives under the article's CC BY 4.0 -- registered ship. The
# problem is that the deposit holds no wording at all (columns are AC1..APL11),
# the item stems live in the article's own tables, and those tables present the
# RETAINED items against their loadings and item-total correlations. With four
# items dropped between administration and publication, and no key tying a
# printed stem to a deposited column code, a code-to-stem mapping cannot be
# established from this source -- and an off-by-two error inside a subscale is
# exactly the failure an itemtext table must not ship. Queued in TODO.md with
# that diagnosis rather than attempted.
#
# PII: screened over all 50 columns. Every one is numeric; the export carries
# no free-text, name, email, date or timestamp column, and no geography. ID is
# a sequential record number, unique per row.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("PADCHASUWAN_RAW", "journal.pone.0359881_S1_Dataset.xlsx")

TABLE = "padchasuwan_2026_sexual_health_literacy"
N_ROWS = 1235
LO, HI = 1, 4

# administered counts, NOT the published 45-item form's 12/12/10/11
SUBSCALES = {"AC": 14, "UN": 12, "APR": 12, "APL": 11}


def screen_for_pii(df):
    txt = [c for c in df.columns
           if pd.api.types.is_string_dtype(df[c])
           and pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert not txt, f"unexpected text column(s) -- screen them: {txt}"
    assert all(pd.to_numeric(df[c], errors="coerce").notna().all()
               for c in df.columns), "a non-numeric column escaped the screen"
    print("  every column is numeric: no free text, name, email, date, "
          "timestamp or geographic column in this file")


def convert():
    df = pd.read_excel(RAW, sheet_name=0)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    items = []
    found = {}
    for c in df.columns:
        m = re.match(r"^([A-Z]+)(\d+)$", str(c))
        if m and m.group(1) in SUBSCALES:
            found.setdefault(m.group(1), []).append(c)
            items.append(c)
    # pin the ADMINISTERED split: if a future deposit ships the trimmed
    # 45-item form (12/12/10/11), this fails rather than silently relabelling
    got = {k: len(v) for k, v in found.items()}
    assert got == SUBSCALES, (
        f"subscale counts are {got}, expected the administered {SUBSCALES}. "
        "The published instrument is the 45-item form (AC 12, UN 12, APR 10, "
        "APL 11) -- if this is that form, the table is a different thing and "
        "the description must change.")
    left_out = [c for c in df.columns if c not in items and c != "ID"]
    assert not left_out, f"unaccounted source columns: {left_out}"
    assert len(items) == 49, len(items)
    print(f"49 administered items: " +
          ", ".join(f"{k} {v}" for k, v in SUBSCALES.items()) +
          " (the PUBLISHED form is 45: AC 12, UN 12, APR 10, APL 11 -- "
          "4 items were dropped by EFA/CFA and which ones is not stated)")

    assert int(df[items].isna().sum().sum()) == 0, "unexpected missing cells"
    vals = pd.to_numeric(df[items].stack(), errors="coerce")
    assert vals.between(LO, HI).all(), sorted(vals.unique())
    assert all(set(df[c].unique()) == set(range(LO, HI + 1)) for c in items), \
        "an item is missing one of the four documented levels"
    print(f"resp domain is exactly {sorted(set(vals.unique()))} on all 49 "
          f"items, all four levels present on every item, zero missing cells")

    assert df["ID"].nunique() == len(df), "ID is not unique"
    df = df.rename(columns={"ID": "id"})

    long = df.melt(id_vars=["id"], value_vars=items,
                   var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(int)

    assert long["id"].nunique() == N_ROWS
    assert long["item"].nunique() == 49
    assert not long.duplicated(["id", "item"]).any()
    assert len(long) == 49 * N_ROWS, len(long)
    assert len(TABLE) <= 40, TABLE

    long = long[["id", "item", "resp"]]

    # gate before writing -- the contract check requires the validator to run
    # in-script, not just on the output file
    checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                            for i in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:175]}")

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
