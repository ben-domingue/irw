#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0168949
# DOI: 10.1371/journal.pone.0168949
# Paper: Yang L, Yan J, Jin X, Jin Y, Yu W, Xu S, et al. (2016). Screening for
#   Dementia in Older Adults: Comparison of Mini-Mental State Examination,
#   Mini-Cog, Clock Drawing Test and AD8. PLoS ONE 11(12): e0168949.
# Data: PLOS Supporting Information S1 Dataset (journal.pone.0168949.s001,
#   "The dataset of the manuscript"), 2,015 adults aged 65+ in Zhejiang,
#   eastern China; tests administered and scored by trained psychiatrists.
#   The deposit has no codebook: column names are short codes (c*, d*, e*,
#   f*, h*, i*).
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 4.
#
# TWO output tables, item codes the deposit's own, every item scored 0/1:
#   yang_2016_mmse  the Mini-Mental State Examination, 30 items: e11-e15,
#     e21-e25, e31-e33, e41-e45, e51-e53, e61-e62, e7, e8, e91-e93, e10,
#     e16. Identified from the data, not a codebook: the blocks have the
#     MMSE's shape (orientation 5 + 5, registration 3, attention 5, recall 3,
#     naming 2, repetition, three-stage command 3, reading, writing ...), and
#     their sum equals the deposit's 0-30 total (e18) on 1,945 of 2,015 rows
#     (96.5%); e19 (0/1) has the 705 positives the paper reports for the
#     MMSE. The 70 rows whose items do not sum to e18 are kept: the item
#     scores are what was recorded, the total may have been entered
#     separately.
#   yang_2016_cdt   the Clock Drawing Test, d1-d5: their sum equals the
#     deposit's 0-5 score d6 on 99.8% of rows, and d7 (0/1) has the 686 CDT
#     positives the paper reports. One d2 cell holds 11, an entry error, and
#     is dropped.
# Covariates: sex (2 = women: 1,165 rows, the paper's count of women; 1 =
#   men), age.
# Dropped: the Mini-Cog (c1-c3: a clock score, a 0-3 word recall and the
#   result, under the 3-item floor as items); the AD8 (f1-f9: f1-f7 carry a
#   code 3 the paper does not describe and f8 has a different distribution;
#   their sum matches the f9 total on only 66% of rows, so the item coding is
#   not recoverable); every total and flag (d6, d7, e17-e19, f9, f10); the
#   health-history and lifestyle blocks (g, h, i), which include free-text
#   entries; five unnamed text columns.
# `id` is the deposit's id (1..2015, unique).
#
# Item text: NOT SHIPPED. No codebook in the deposit.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0168949.s001"
RAW = os.environ.get("YANG_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}
MMSE = ["e11", "e12", "e13", "e14", "e15", "e21", "e22", "e23", "e24", "e25", "e31", "e32", "e33", "e41", "e42",
        "e43", "e44", "e45", "e51", "e52", "e53", "e61", "e62", "e7", "e8", "e91", "e92", "e93", "e10", "e16"]
CDT = ["d1", "d2", "d3", "d4", "d5"]


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_excel(src, sheet_name=0)


def convert():
    df = load()
    assert df.shape == (2015, 121), df.shape
    print(f"PII screen: {len(df.columns)} columns examined; only id, sex, age and the c/d/e blocks are read")
    assert df["id"].is_unique
    assert (df[MMSE].sum(axis=1) == df["e18"]).sum() == 1945
    assert (df["e19"] == 1).sum() == 705 and (df["d7"] == 1).sum() == 686
    assert (df["sex"] == 2).sum() == 1165
    df = df.copy()
    df["id"] = df["id"].astype(int)
    df["cov_sex"] = df["sex"].map({1: "male", 2: "female"})
    df["cov_age"] = df["age"].astype(int)
    covs = ["cov_sex", "cov_age"]
    for name, items in (("mmse", MMSE), ("cdt", CDT)):
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        if name == "cdt":
            assert (long["resp"] > 1).sum() == 1
            long = long[long["resp"] <= 1]
        assert set(long["resp"]) <= {0, 1}, (name, set(long["resp"]))
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [0, 1] for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:150]}")
        out = f"yang_2016_{name}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
