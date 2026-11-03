#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0156288
# DOI: 10.1371/journal.pone.0156288
# Paper: Spexoto, M. C. B., Serrano, S. V., Halliday, V., Maroco, J., &
#   Campos, J. A. D. B. (2016). Cancer Appetite and Symptom Questionnaire
#   (CASQ) for Brazilian patients: Cross-cultural adaptation and validation
#   study. PLOS ONE 11(6): e0156288.
# Data: journal.pone.0156288.s002 (S1 Dataset, .sav), 1,140 adult cancer
#   patients at a Brazilian cancer hospital (outpatients and inpatients).
#   S1 Appendix (.docx) prints the English original and the Portuguese
#   version of all 12 items with their five options.
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# ONE output table, spexoto_2016_casq: CASQ1..CASQ12, the 12-item Cancer
# Appetite and Symptom Questionnaire (Halliday et al.), Brazilian
# Portuguese, scored 0-4 as deposited (the .sav has no value labels; each
# item has its own five option wordings). All 12 administered items are
# shipped, including the two the paper's CFA later removed.
#
# Covariates (all from .sav value labels): sex (1 male / 2 female; 699 of
# 1,140 = 61.3% women, the paper's figure), age, religion, religious
# practice, marital status, labour activity, cancer specialty, clinical
# stage, metastasis, treatment modality, interview location, nutritional
# status, ABEP socioeconomic class (its 8 codes collapse to the labelled
# A/B/C/D-E). Not shipped: height, weight, BMI (measurements) and filter_$
# (the deposit's random ~60% split-sample flag).
#
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. Stems and options in both languages are in S1
#   Appendix, keyed It1..It12, so the stems are cheap; the score key is not.
#   The deposit stores 0-4 with no value labels, and the appendix lists
#   options with no scores, so which option is 0 on each item (the CASQ
#   reverse-keys some items) would have to be reconstructed.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("SPEXOTO_RAW", "journal.pone.0156288.s002.sav")
NAME = "spexoto_2016_casq"
N_ROWS = 1140

COVS = {"Sex": "cov_sex", "Religion": "cov_religion", "Religious_practice": "cov_religious_practice",
        "Marital_status": "cov_marital_status", "Labor_activity": "cov_labor_activity",
        "Specialty": "cov_cancer_specialty", "Clinical_staging": "cov_clinical_stage",
        "Metastasis": "cov_metastasis", "Treatment_modality": "cov_treatment",
        "Interview_location": "cov_interview_location", "Nutritional_status": "cov_nutritional_status",
        "Classification_ABEP": "cov_abep_class"}


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 29 and txt == []
    items = [f"CASQ{i}" for i in range(1, 13)]
    vl = meta.variable_value_labels
    assert not any(c in vl for c in items)
    assert int((df["Sex"] == 2).sum()) == 699 and vl["Sex"] == {1.0: "male", 2.0: "female"}

    df["id"] = range(1, N_ROWS + 1)
    df["cov_age"] = df["Age"]
    for src, dst in COVS.items():
        df[dst] = df[src].map(vl[src])
    cov_cols = ["cov_age"] + list(COVS.values())
    long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item",
                                              value_name="resp")
    assert long["resp"].notna().all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) == {0, 1, 2, 3, 4}
    long = long[["id", "item", "resp"] + cov_cols]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [0, 1, 2, 3, 4] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    accounted = set(items) | set(COVS) | {"Age", "Height_meters", "Weight_kg", "BMI", "filter_$"}
    assert set(meta.column_names) == accounted
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
