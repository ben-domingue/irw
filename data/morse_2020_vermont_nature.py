#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243697
# DOI: 10.1371/journal.pone.0243697
# Paper: Morse JW, Gladkikh TM, Hackenburg DM, Gould RK (2020). COVID-19 and
#   human-nature relationships: Vermonters' activities in nature and associated
#   nonmaterial values during the pandemic. PLoS ONE 15(12): e0243697.
# Data: PLOS Supporting Information S1 Dataset (journal.pone.0243697.s001,
#   "Survey dataset"), a LimeSurvey export, 3,204 Vermont residents. S1-S8
#   Table are model output, not read.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 3.
#
# TWO output tables, item names the deposit's own activity / value names:
#   morse_2020_activity_change  15 outdoor activities (biking, boating, ...,
#     wildlife), each "whether respondents engage with that activity at all,
#     and if so, if they engaged more, less, or the same during COVID-19".
#     resp = the deposit's own <activity>OrdinalScaleNum: 1 less, 2 no change,
#     3 more (its <activity>OrdinalScaleCat labels, checked one-to-one). Code 0
#     ("Doesn't do activity") is not a point on the change scale and is
#     dropped. The paper asked this on a 7-point scale; the raw answer codes
#     (A2-A8) are in the file but their order is not documented, so the
#     deposit's collapsed, labelled 3-point version ships.
#   morse_2020_nature_values    13 benefits of or values from nature (BENE_
#     AESTH, CREATIVE, TRADITION, FOOD, ID, LIFELESSON, MENTALWB, EXER, FUN,
#     FAMILIAR, SOCIAL, SPIRTUAL [sic], CARE), "a 7-point Likert-scale (from
#     strongly disagree to strongly agree)", 1-7.
# Covariates (the deposit's labelled categories, its "99" set to missing):
#   gender, income (below / median / above median range), urban area or not,
#   race/ethnicity (White / all but white), employment (lost job / other).
# Dropped: Zip (a ZIP code; 2026-10-20 geography ruling), the Census
#   urban-area codes derived from it (UA v. FA, LSAD10, UATYP10), BirthYear and
#   Age (age holds codes up to 960); the BENE_R_* / BENE_RB_* recodes and the
#   benefit rankings; the raw A-coded answers and the CatNum/Inverse
#   duplicates of every covariate; the multi-select race and employment
#   checkboxes.
# `id` is the deposit's id column (unique).
#
# Item text: NOT SHIPPED. Names only; the questionnaire is not in the SI.

import io
import os
import sys

import numpy as np
import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0243697.s001"
RAW = os.environ.get("MORSE_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ACTS = ["Biking", "Boating", "Camping", "Fishing", "Gardening", "Gathering", "Hiking", "Hunting", "Jogging",
        "Photography", "RelaxOthers", "RelaxMyself", "RockClimbing", "Walking", "Wildlife"]
BENE = ["BENE_AESTH", "BENE_CREATIVE", "BENE_TRADITION", "BENE_FOOD", "BENE_ID", "BENE_LIFELESSON", "BENE_MENTALWB",
        "BENE_EXER", "BENE_FUN", "BENE_FAMILIAR", "BENE_SOCIAL", "BENE_SPIRTUAL", "BENE_CARE"]
CAT = {0: "Doesn't do activity", 1: "Less", 2: "No change", 3: "More"}
COVS = {"GenderCat": "cov_gender", "IncomeCat": "cov_income", "GeographyCat": "cov_urban",
        "Race/EthnicityCat": "cov_race_ethnicity", "EmploymentCat": "cov_employment"}


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_excel(src, sheet_name=0)


def convert():
    df = load()
    assert df.shape == (3204, 126), df.shape
    print(f"PII screen: {len(df.columns)} columns examined; Zip, BirthYear and Age not carried")
    assert df["id"].nunique() == len(df)
    acts = [a for a in ACTS if f"{a}OrdinalScaleNum" in df.columns]
    assert len(acts) == 15, acts
    for a in acts:
        pairs = set(zip(df[f"{a}OrdinalScaleNum"], df[f"{a}OrdinalScaleCat"]))
        assert pairs <= set(CAT.items()), (a, pairs)
    df = df.copy()
    df["id"] = df["id"].astype(int)
    for src, dst in COVS.items():
        df[dst] = df[src].astype(str).str.strip().replace({"99": np.nan, "nan": np.nan})
    covs = list(COVS.values())
    sub = df[["id"] + covs + [f"{a}OrdinalScaleNum" for a in acts]].rename(
        columns={f"{a}OrdinalScaleNum": a.lower() for a in acts})
    tables = {"activity_change": (sub, [a.lower() for a in acts], [1, 2, 3]),
              "nature_values": (df[["id"] + covs + BENE], BENE, list(range(1, 8)))}
    for name, (frame, items, perm) in tables.items():
        long = frame.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        long["resp"] = long["resp"].astype(int)
        if name == "activity_change":
            long = long[long["resp"] != 0]
        assert set(long["resp"]) <= set(perm), (name, set(long["resp"]))
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: perm for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:150]}")
        out = f"morse_2020_{name}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
