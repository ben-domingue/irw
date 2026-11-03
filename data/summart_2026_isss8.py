#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0341756
# DOI: 10.1371/journal.pone.0341756
# Paper: Summart U, Sangruangake M, Wamaloon C, Moungmultri A, A'la MZ (2026).
#   Psychometric properties of the Thai version of the Illness-Specific Social
#   Support Scale Short Version-8 (ISSS-8) among hematological malignancy
#   patients in the Northeastern region of Thailand: A multicenter study.
#   PLOS ONE 21(7): e0341756.
# Data: S1 File (journal.pone.0341756.s001, sheet "data"), 330 patients with
#   haematological malignancies receiving chemotherapy at three hospitals.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 4, BATCH_LOG.md).
#
# PII screen: three text/object columns -- nonhodgin_type and formular
#   (diagnosis and chemotherapy-regimen names, e.g. "DLBCL", "6R-CHOP") and inc
#   (income, typed). No names, emails or identifiers. date_chemo (a
#   chemotherapy date in the Thai calendar) is a clinical event date, not a
#   date of birth; it is dropped and nothing derived from it ships.
#
# TWO output tables:
#   summart_2026_isss8  Illness-Specific Social Support Scale Short Version-8,
#     Thai, support1..support8, 0 never .. 4 always (positive support and
#     detrimental interactions, four items each). 7 cells of 5 (support4 x5,
#     support8 x2) are outside the 0-4 scale and are dropped.
#   summart_2026_sicpa  Stanford Inventory of Cancer Patient Adjustment, Thai,
#     SICPA1..SICPA38, 1 not at all confident .. 10 completely confident. Cells
#     of 0 (outside the 1-10 scale) are dropped.
# NOT SHIPPED: health1..health43 and beh1..beh17 -- batteries from the parent
#   project (health literacy and self-care behaviour) that this paper does not
#   describe, so their instruments and anchors are unknown.
# Covariates: age (years), hospital (1-3, as cluster_id).
# Dropped: id (replaced by the row index; it is a 1..330 sequence), sex (codes
#   0/1/2 = 86/150/94 against the paper's 256 male / 94 female of 350, so code
#   0 cannot be placed), religion, edu, status, occ, inc, nonhodgin_type,
#   stage, date_chemo, formular, and a trailing unnamed column (two "-" cells).
#
# Item text: NOT SHIPPED. Column codes only (no labels at any level); the Thai
#   wording of either instrument is not in the article or SI.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("SUMMART_RAW", "journal.pone.0341756.s001.xlsx")
BLOCKS = {"isss8": ([f"support{i}" for i in range(1, 9)], list(range(0, 5))),
          "sicpa": ([f"SICPA{i}" for i in range(1, 39)], list(range(1, 11)))}
NOT_SHIPPED = [f"health{i}" for i in range(1, 44)] + [f"beh{i}" for i in range(1, 18)]
DROPPED = ["id", "sex", "religion", "edu", "status", "occ", "inc", "nonhodgin_type", "stage", "date_chemo",
           "formular", "Unnamed: 119"]


def convert():
    df = pd.read_excel(RAW, sheet_name="data")
    assert df.shape == (330, 120), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text/object columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and set(txt) == {"inc", "nonhodgin_type", "date_chemo", "formular", "Unnamed: 119"}
    assert (df["id"] == range(1, 331)).all() and set(df["Unnamed: 119"].dropna()) == {"-"}
    df["id"] = range(1, len(df) + 1)
    df["cov_age"] = df["age"]
    df["cluster_id"] = df["hos"]
    covs = ["cov_age", "cluster_id"]
    used = {"age", "hos"} | set(DROPPED) | set(NOT_SHIPPED)
    total = 0
    for block, (items, perm) in BLOCKS.items():
        used |= set(items)
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        assert long["resp"].notna().all()
        bad = ~long["resp"].isin(perm)
        print(f"  {block}: dropping {bad.sum()} out-of-range cells {long.loc[bad, 'resp'].value_counts().to_dict()}")
        assert bad.sum() < 10
        long = long[~bad].copy()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: perm for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"summart_2026_{block}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert used | set(covs) == set(df.columns), set(df.columns) - used
    print(f"total responses {total}; dropped: {DROPPED}; not shipped: health1-43, beh1-17")


if __name__ == "__main__":
    convert()
