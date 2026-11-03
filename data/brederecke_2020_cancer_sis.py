#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0240619
# DOI: 10.1371/journal.pone.0240619
# Paper: Brederecke J, Zimmermann T (2020). Psychometric properties of the
#   German version of the Self Image Scale (SIS-D) in a sample of cancer
#   patients. PLOS ONE 15(10): e0240619.
# Data: S1 Dataset (journal.pone.0240619.s001, .sav), 285 rows of German
#   cancer patients in a relationship.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# NOT the same sample as data/brederecke_2020_self_image.py, which is the
# companion general-population paper (10.1371/journal.pone.0230331, N=1,367).
# This deposit is the cancer-patient sample, and its tables are named
# brederecke_2020_cancer_* to keep the two apart.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 5, BATCH_LOG.md).
#
# FIVE output tables. Every anchor below is the .sav's own value label:
#   brederecke_2020_cancer_sis  Self Image Scale (German, SIS-D), 11 items,
#     1 strongly disagree .. 5 strongly agree. SIS4_recoded and SIS9_recoded
#     are stored reversed, as their names say -- confirmed: SIS1+SIS2+
#     SIS4_recoded+SIS5+SIS7+SIS9_recoded equals the deposit's SIS_self on
#     every row. Codes kept as deposited, `_recoded` suffix included.
#   brederecke_2020_cancer_phq9  PHQ-9, 0 not at all .. 3 nearly every day.
#   brederecke_2020_cancer_gad7  GAD-7, same anchors.
#   brederecke_2020_cancer_qmi   Quality of Marriage Index, QMI1-5 1 strongly
#     disagree .. 7 strongly agree, QMI6 (overall happiness) 1 extremely low
#     .. 10 extremely high -- the instrument's own two formats.
#   brederecke_2020_cancer_qsc   Questionnaire on Stress in Cancer Patients
#     (QSC-R23), 23 items, 0 not applicable, 1 applies and is a slight
#     problem .. 5 applies and is a very serious problem (items sum to the
#     deposit's QSC_sum on every row).
# Composites PHQ_sum, GAD_sum, QMI_sum, QSC_sum, SIS_self, SIS_partner not
#   shipped.
# Covariates (all from value labels): sex, age, education, employment,
#   cancer group, months since diagnosis. `Cancer` (23 diagnosis codes, only
#   four labelled) is dropped in favour of the labelled CancerGroups.
# `id` is the row index.
#
# Item text: NOT SHIPPED. No variable labels on any item (value labels
#   only); the German wording is not in the article or SI.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("BREDERECKE_CANCER_RAW", "journal.pone.0240619.s001.sav")
SIS = ["SIS1", "SIS2", "SIS4_recoded", "SIS5", "SIS7", "SIS9_recoded", "SIS6", "SIS8", "SIS3", "SIS10", "SIS11"]
QMI = [f"QMI{i}" for i in range(1, 7)]
BLOCKS = {
    "sis": (SIS, {c: list(range(1, 6)) for c in SIS}),
    "phq9": ([f"PHQ{i}" for i in range(1, 10)], {f"PHQ{i}": [0, 1, 2, 3] for i in range(1, 10)}),
    "gad7": ([f"GAD{i}" for i in range(1, 8)], {f"GAD{i}": [0, 1, 2, 3] for i in range(1, 8)}),
    "qmi": (QMI, {**{c: list(range(1, 8)) for c in QMI[:5]}, "QMI6": list(range(1, 11))}),
    "qsc": ([f"QSC{i}" for i in range(1, 24)], {f"QSC{i}": list(range(0, 6)) for i in range(1, 24)}),
}
COMPOSITES = {"PHQ_sum", "GAD_sum", "QMI_sum", "QSC_sum", "SIS_self", "SIS_partner"}
COVS = {"Sex": "cov_sex", "Age": "cov_age", "Education": "cov_education", "Employment": "cov_employment",
        "CancerGroups": "cov_cancer_group", "TimeSinceDiagnosis": "cov_months_since_diagnosis"}


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert df.shape == (285, 69), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    assert (df[["SIS1", "SIS2", "SIS4_recoded", "SIS5", "SIS7", "SIS9_recoded"]].sum(axis=1, min_count=6)
            .sub(df["SIS_self"]).abs().max()) == 0
    df["id"] = range(1, len(df) + 1)
    for s, t in COVS.items():
        lab = meta.variable_value_labels.get(s)
        df[t] = df[s].map(lab) if lab else df[s]
    covs = list(COVS.values())
    used = set(COVS) | COMPOSITES | {"Cancer"}
    names, total = [], 0
    for block, (items, ok) in BLOCKS.items():
        used |= set(items)
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        bad = long[[r not in ok[i] for i, r in zip(long["item"], long["resp"])]]
        assert bad.empty, bad
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values=ok)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"brederecke_2020_cancer_{block}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert len(set(names)) == len(names)
    left = set(df.columns) - used - {"id"} - set(covs)
    assert not left, left
    print(f"total responses {total}")


if __name__ == "__main__":
    convert()
