#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0190722
# DOI: 10.1371/journal.pone.0190722
# Paper: Parra-Fernandez ML, Rodriguez-Cano T, Onieva-Zafra MD, et al. (2018).
#   Adaptation and validation of the Spanish version of the ORTO-15
#   questionnaire for the diagnosis of orthorexia nervosa. PLOS ONE 13(1):
#   e0190722.
# Data: S1 File (journal.pone.0190722.s001, .xlsx, sheet "plosone (2)"), 454
#   Spanish university students (Castilla-La Mancha).
# License: CC BY 4.0 (the article; the data is its Supporting Information).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 3, BATCH_LOG.md).
# Not the same respondents as missbach_2015_orto15 (1,029 German-speaking
# adults): a different country, sample and N.
#
# ONE output table, parra_fernandez_2018_orto15: ORTHO-1..ORTHO-15, the Spanish
# ORTO-15 (Donini et al. 2005), 1 always, 2 often, 3 sometimes, 4 never, as
# deposited; ORTO-15 scoring assigns 1 or 4 to the orthorexic answer item by
# item, and nothing is re-keyed here.
# Covariates: gender (1 = female, 2 = male: the paper's 295 women and 159 men
#   match the deposit's 295 and 159 exactly), age, BMI (the deposit's own,
#   from self-reported height and weight).
# Dropped: HEIGHT and WEIGHT (BMI carries them; WEIGHT holds a 21 kg entry
#   error); the CAGE items CAGE-1..4 (1/2 with no labels; the deposit's own
#   CAGE PUNTUATION does not match the count of either code, so the direction
#   cannot be recovered) and CAGE PUNTUATION, ALCOHOL RISK; the EDI-2 subscale
#   totals (no items deposited); CATE BMI; and the unlabelled clinical and
#   household codes (MARITAL STATUS, SMOKER, ALERGIES and type, GASTROINTESTINAL
#   ILLNESS and type, MENTAL DISORDER and type, FAMILY MENTAL DISORDER and type,
#   COHABITACION, PERSON WHO MADE THE SHOP FOR COKING, ANY SPORTS).
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. Column codes only (no labels at any level); the
#   Spanish wording is not in the deposit. ORTO-15 is registered hold
#   (2026-11-02).

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("PARRA_RAW", "journal.pone.0190722.s001.xlsx")
NAME = "parra_fernandez_2018_orto15"


def convert():
    df = pd.read_excel(RAW, sheet_name="plosone (2)")
    assert df.shape == (454, 51)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0
    assert set(txt) == {"ALERGY TYPE", "GASTROINTESTINAL ILLNESS  TYPE"}
    for c in txt:  # coded type columns stored as text: digits, '-' or blank only
        assert df[c].astype(str).str.strip().isin(["", "-"] + [str(i) for i in range(1, 10)]).all()
    assert (df["GENDER"] == 1).sum() == 295 and (df["GENDER"] == 2).sum() == 159
    items = [f"ORTHO-{i}" for i in range(1, 16)]
    df["id"] = range(1, len(df) + 1)
    df["cov_gender"] = df["GENDER"].map({1: "female", 2: "male"})
    df["cov_age"] = df["AGE"]
    df["cov_bmi"] = df["BMI"].round(2)
    cov_cols = ["cov_gender", "cov_age", "cov_bmi"]
    long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
    assert long["resp"].notna().all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) == {1, 2, 3, 4}
    long = long[["id", "item", "resp"] + cov_cols]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    used = set(items) | {"GENDER", "AGE", "BMI"}
    dropped = [c for c in df.columns if c not in used and c not in ("id", *cov_cols)]
    assert len(dropped) == 51 - len(used)
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}; dropped {dropped}")


if __name__ == "__main__":
    convert()
