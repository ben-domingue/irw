#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0289317
# DOI: 10.1371/journal.pone.0289317
# Paper: Altarawneh WM, Masa'deh R, Hamaideh SH, et al. (2023). Nurses'
#   knowledge, attitudes and practices towards palliative care provided to
#   patients diagnosed with cancer. PLOS ONE 18(10): e0289317.
# Data: S1 Data (journal.pone.0289317.s002, .xlsx), 228 registered nurses
#   caring for cancer patients in four Jordanian hospitals.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 5, BATCH_LOG.md).
#
# ONE output table:
#   altarawneh_2023_pcps  Palliative Care self-reported Practices Scale
#     (PCPS, Nakazawa et al. 2010), Practice1..Practice18, 1 never, 2 rarely,
#     3 sometimes, 4 usually, 5 always (paper, Methods). Checked: the item
#     sum averages 52.7 (paper: 52.7) and, with gender 0 = female, 57.9 for
#     women and 44.4 for men (paper: 57.9 and 44.4).
# NOT shipped, because the deposit does not reconcile with the paper:
#   Knowledge1..20 (PCKT) -- the paper says 1 = correct, 2 = incorrect,
#     3 = unsure and reports a mean of 8.8 correct; counting the 1s gives
#     12.8, so the codes cannot be scored with confidence.
#   Attitudes1..30 (FATCOD-B, 220 answered) -- the raw item sum averages
#     78.1 against the paper's 80.9, so whether reverse-keyed items were
#     already flipped in the file cannot be established.
# Covariates: age, gender (0 female / 1 male: 140 women, the paper's
#   61.4%), education (1-3, unlabelled -> dropped), years in oncology,
#   palliative-care training (0/1). Ward is decoded from the paper's counts
#   (1 oncology 32, 2 medical 72, 3 surgical 64, 4 ICU 60 -- checked below).
#   Dropped: RN and Oneyearonco (constant), Education, Hospital and
#   PalTrainType (no labels), DyingPatient (0/1, question not described).
# `id` is the row index.
#
# Item text: NOT SHIPPED. Column codes only; the PCPS wording is not in the
#   article or SI.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ALTARAWNEH_RAW", "journal.pone.0289317.s002.xlsx")
ITEMS = [f"Practice{i}" for i in range(1, 19)]
NOT_SHIPPED = {f"Knowledge{i}" for i in range(1, 21)} | {f"Attitudes{i}" for i in range(1, 31)}
DROPPED = {"RN", "Oneyearonco", "Education", "Hospital", "PalTrainType", "DyingPatient"}
WARD = {1: "oncology", 2: "medical", 3: "surgical", 4: "intensive care"}


def convert():
    df = pd.read_excel(RAW)
    assert df.shape == (228, 79), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    tot = df[ITEMS].sum(axis=1)
    assert round(tot.mean(), 1) == 52.7
    assert round(tot[df["Gender"] == 0].mean(), 1) == 57.9 and round(tot[df["Gender"] == 1].mean(), 1) == 44.4
    assert df["Ward"].value_counts().to_dict() == {2: 72, 3: 64, 4: 60, 1: 32}
    df["id"] = range(1, len(df) + 1)
    df["cov_age"] = df["Age"]
    df["cov_gender"] = df["Gender"].map({0: "female", 1: "male"})
    df["cov_years_oncology"] = df["TotalExponco"]
    df["cov_ward"] = df["Ward"].map(WARD)
    df["cov_pc_training"] = df["Paltraining"]
    covs = ["cov_age", "cov_gender", "cov_years_oncology", "cov_ward", "cov_pc_training"]
    long = df[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    used = set(ITEMS) | NOT_SHIPPED | DROPPED | {"Age", "Gender", "TotalExponco", "Ward", "Paltraining"}
    left = set(df.columns) - used - {"id"} - set(covs)
    assert not left, left
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "altarawneh_2023_pcps.csv"), index=False)
    print(f"altarawneh_2023_pcps: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
