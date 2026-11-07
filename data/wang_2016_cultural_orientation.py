#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0165858
# DOI: 10.1371/journal.pone.0165858
# Paper: Wang S, Newman IM, Shell DF (2016). Cultural Orientation and Its
#   Associations with Alcohol Use by University Students in China. PLoS ONE
#   11(11): e0165858.
# Data: PLOS Supporting Information S1 Dataset (journal.pone.0165858.s001,
#   "Cultural Orientation and Drinking Data University Students China"),
#   sheet 1 (1,305 students) plus a "codebook" sheet, which names CO1-CO116
#   "Cultural orientation items" and the derived factor-score columns.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 2.
#
# ONE output table: wang_2016_cultural_orientation -- the revised Chinese
#   Cultural Orientation Questionnaire as administered, 116 items CO1-CO116,
#   1-5 ("1 = strongly disagree ... 5 = strongly agree"). The paper's FINAL
#   questionnaire keeps 67 of these items (nine sub-factors under Chinese and
#   Western cultural orientation); all 116 administered items ship, as the
#   deposit gives them, and the item-to-factor assignment is not in the file.
# Covariates: gender (2 = female: 776 of 1,302 coded, 59.6%; the paper reports
#   60% female), age, year of study (1 freshman, 2 sophomore, 3 junior,
#   4 senior, 5 graduate: the coded shares match the paper's 62/15/11/6/6%),
#   drinking category (the deposit's DrinkingCateg: 1 nondrinker, 2 drinker in
#   the last year but not the last 30 days, 3 recent drinker, per the paper).
# Dropped: ID (a six-digit code; newid, the row number, is used as `id`);
#   Hometown (five codes, while the paper reports two categories, so the
#   labels cannot be assigned); DrinkingQ (the raw drinking question, its codes
#   unlabelled); the eleven factor-score columns.
#
# Item text: NOT SHIPPED. Header codes only; the article quotes one example
#   item per sub-factor; the CCOQ wording is in the cited sources.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0165858.s001"
RAW = os.environ.get("WANG_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ITEMS = [f"CO{i}" for i in range(1, 117)]
FACTORS = ["F_Chi", "F_App", "F_Wes", "F_Fil", "F_Har", "F_Con", "F_Resp", "F_Collect", "F_Att", "SF_Chinese",
           "SF_Western"]
YEAR = {1: "freshman", 2: "sophomore", 3: "junior", 4: "senior", 5: "graduate"}
DRINK = {1: "nondrinker", 2: "drinker, not in last 30 days", 3: "recent drinker"}


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=120)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_excel(src, sheet_name=0)


def convert():
    df = load()
    assert df.shape == (1305, 135), df.shape
    used = {"newid", "ID", "Age", "Gender", "Grade", "Hometown", "DrinkingQ", "DrinkingCateg"} | set(ITEMS) | set(
        FACTORS)
    assert used == set(df.columns), set(df.columns) ^ used
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and not txt
    assert df["newid"].nunique() == len(df)
    df["id"] = df["newid"].astype(int)
    df["cov_gender"] = df["Gender"].map({1: "male", 2: "female"})
    df["cov_age"] = df["Age"]
    df["cov_year"] = df["Grade"].map(YEAR)
    df["cov_drinking"] = df["DrinkingCateg"].map(DRINK)
    covs = ["cov_gender", "cov_age", "cov_year", "cov_drinking"]
    long = df[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:150]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "wang_2016_cultural_orientation.csv"), index=False)
    print(f"wang_2016_cultural_orientation: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
