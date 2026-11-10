#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0252779
# DOI: 10.1371/journal.pone.0252779
# Paper: Karawekpanyawong N, Kaewkitikul K, Maneeton B, Maneeton N,
#   Siriaree S (2021). The prevalence of depressive disorder and its
#   association in Thai cervical cancer patients. PLoS ONE 16(6): e0252779.
# Data: figshare 10.6084/m9.figshare.14124017 ("dataset-prevalence of
#   depression in cervical cancer.xlsx"), CC0 (api.figshare.com). Sheet
#   data-upload (200 patients) + sheet variables (codebook). Gynecologic
#   oncology clinic, Northern Thailand, Oct 2018 - Aug 2019; all female.
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# FOUR output tables, items as answered (Thai versions):
#   karawekpanyawong_2021_phq9     PHQ-9, phq_1..9, 0-3.
#   karawekpanyawong_2021_chalder  Chalder Fatigue Scale (Likert), 11 items,
#     0-3 ("Better than usual" .. "Much worse than usual").
#   karawekpanyawong_2021_qlq_c30  EORTC QLQ-C30, q_1..30: q_1-28 1-4,
#     q_29-30 (global health, global QoL) 1-7.
#   karawekpanyawong_2021_qlq_cx24 EORTC QLQ-CX24 (deposit Q31-Q54, renamed
#     cx_1..24), 1-4. Code 0 on the sexual-activity-conditional items
#     cx_20..24 (deposit Q50-Q54) is "no SI" (not sexually active, item not
#     applicable) and is dropped.
# Dropped: Charlson comorbidity items, the 8 MINI suicidality items
#   (weighted scores 0/1/2/4/10, not responses), derived scores, diagnoses.
# Covariates: age (year of assessment - year of birth), education
#   (1 none .. 4 higher education), cancer stage (StageCANew, as deposited).
# `id` = row index (CRN, a case report number, is not carried).

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://ndownloader.figshare.com/files/26634500"
RAW = os.environ.get("KARAWEKPANYAWONG2021_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_karawekpanyawong2021_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, sheet_name="data-upload")
    if not RAW:
        os.remove(path)
    return df


def save(df, covs, mapping, name, values):
    src = list(mapping)
    sub = df[["id"] + covs + src].rename(columns=mapping)
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= set(values), set(long["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df = load()
    assert len(df) == 200
    df = df.reset_index(drop=True).copy()
    phq = {f"PHQ{i}": f"phq_{i}" for i in range(1, 10)}
    assert (df[list(phq)].sum(axis=1) == df["PHQtotal"]).all()
    fat = {f"fatigue{i}": f"fatigue_{i}" for i in range(1, 12)}
    c30 = {f"Q{i}": f"q_{i}" for i in range(1, 31)}
    assert (df[[f"Q{i}" for i in range(1, 29)]].sum(axis=1) == df["Q1to28"]).all()
    cx = {f"Q{i}": f"cx_{i - 30}" for i in range(31, 55)}
    for i in range(50, 55):
        df[f"Q{i}"] = df[f"Q{i}"].where(df[f"Q{i}"] != 0)
    df["id"] = df.index + 1
    df["cov_age"] = df["agebyCal"]
    df["cov_education"] = df["EduNew"].map({1: "none", 2: "primary", 3: "secondary", 4: "higher"})
    df["cov_stage"] = df["StageCANew"]
    covs = ["cov_age", "cov_education", "cov_stage"]
    save(df, covs, phq, "karawekpanyawong_2021_phq9", range(0, 4))
    save(df, covs, fat, "karawekpanyawong_2021_chalder", range(0, 4))
    save(df, covs, c30, "karawekpanyawong_2021_qlq_c30", range(1, 8))
    save(df, covs, cx, "karawekpanyawong_2021_qlq_cx24", range(1, 5))


if __name__ == "__main__":
    convert()
