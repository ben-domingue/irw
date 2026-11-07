#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0257421
# DOI: 10.1371/journal.pone.0257421
# Paper: Hawlader MDH, Rashid MU, Khan MAS, Ara T, Nabi MH, Haque MMA, et al.
#   (2021). Quality of life of COVID-19 recovered patients in Bangladesh. PLoS ONE
#   16(10): e0257421.
# Data: PLOS Supporting Information S1 File (journal.pone.0257421.s001,
#   "Post-COVID QoL in Bangladesh datafile", Stata .dta with variable and value
#   labels), 3,244 people who had recovered from COVID-19, Bangladesh.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 2.
#
# Repeat entries: 31 groups of rows (72 rows) agree on all 26 WHOQOL-BREF
#   answers AND on age, gender and monthly income, differing mostly only in ID
#   and a days-since-recovery field; 5 of the pairs are identical on every
#   column but ID. These are read as the same respondent entered more than once
#   and only the first row of each group is kept (41 rows dropped, 3,203 kept).
#
# TWO output tables:
#   hawlader_2021_whoqol_bref  WHOQOL-BREF (validated Bangla version), 26 items
#     QoL1..QoL26, 1-5, the deposit's own codes and Stata value labels (QoL1
#     "Very poor".."Very good"; QoL3 "Not at all".."An extreme amount", etc.).
#     Stored AS DEPOSITED: QoL3, QoL4 and QoL26 are the instrument's negatively
#     worded items and are not reversed here.
#   hawlader_2021_postcovid_symptoms  22 post-COVID symptoms present (1) or not
#     (0): Q16_1..Q16_22 (fatigue, runny nose, cough, shortness of breath, ...,
#     red eye), Stata labels "No"/"Yes".
# Covariates (value labels applied): age, gender, residence, education,
#   occupation, health-care worker, marital status, monthly family income,
#   hospitalised for COVID-19, smoking.
# Dropped: Religion and the two "other, specify" free-text fields; the six
#   comorbidity flags Q15_1..Q15_6 (a list of conditions, not a scale);
#   dup/dup1 (undocumented flags); daysbetween (unlabelled); every cat_* recode
#   and the derived domain scores (phy, psy, soci, envi, chronic, cat_*).
# `id` is the deposit's respondent ID (unique).
#
# Item text: NOT SHIPPED. The Stata variable labels hold the WHOQOL-BREF stems
#   (truncated to Stata's 80 characters) and the value labels the response
#   options, so the text is in hand, but the WHOQOL-BREF is a WHO instrument
#   distributed under its own terms (not checked in this batch). The symptom
#   labels are study-authored one-word names, not questions.

import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0257421.s001&type=supplementary"
RAW = os.environ.get("HAWLADER_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
QOL = [f"QoL{i}" for i in range(1, 27)]
SYM = [f"Q16_{i}" for i in range(1, 23)]
COVS = {"Age": "cov_age", "Gender": "cov_gender", "Residence": "cov_residence", "Education": "cov_education",
        "Occupation": "cov_occupation", "HCW": "cov_health_care_worker", "MS": "cov_marital_status",
        "Income": "cov_monthly_income", "Hospital": "cov_hospitalised", "Smoke": "cov_smoking"}
LABELLED = ["Gender", "Residence", "Education", "Occupation", "HCW", "MS", "Hospital", "Smoke"]


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=300)
        r.raise_for_status()
        src = os.path.join(OUT_DIR, "_hawlader_tmp.dta")
        os.makedirs(OUT_DIR, exist_ok=True)
        open(src, "wb").write(r.content)
    df, meta = pyreadstat.read_dta(src)
    if not RAW:
        os.remove(src)
    return df, meta


def convert():
    df, meta = load()
    assert df.shape == (3244, 87) and df["ID"].nunique() == 3244, df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and set(txt) == {"Other_religion", "Other_occupaiton"}
    key = QOL + ["Age", "Gender", "Income"]
    rep = df.duplicated(subset=key, keep="first")
    assert rep.sum() == 41, rep.sum()
    df = df[~rep].reset_index(drop=True)
    df["id"] = df["ID"].astype(int)
    for src, dst in COVS.items():
        if src in LABELLED:
            df[dst] = df[src].map(meta.variable_value_labels[src])
            assert df.loc[df[src].notna(), dst].notna().all(), src
        else:
            df[dst] = df[src]
    covs = list(COVS.values())
    for name, items, perm in [("whoqol_bref", QOL, [1, 2, 3, 4, 5]), ("postcovid_symptoms", SYM, [0, 1])]:
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(perm)
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: perm for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:150]}")
        out = f"hawlader_2021_{name}"
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
