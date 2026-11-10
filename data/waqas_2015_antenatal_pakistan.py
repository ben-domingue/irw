#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0116510
# DOI: 10.1371/journal.pone.0116510
# Paper: Waqas A, Raza N, Lodhi HW, Muhammad Z, Jamal M, Rehman A (2015).
#   Psychosocial Factors of Antenatal Anxiety and Depression in Pakistan: Is
#   Social Support a Mediator? PLoS ONE 10(1): e0116510.
# Data: PLOS SI S1 (journal.pone.0116510.s001, a CSV despite having no
#   extension), 500 pregnant women at four Lahore teaching hospitals, 2014,
#   interviewed with the Urdu HADS and the Urdu Social Provisions Scale.
# License: CC BY 4.0 (the article and its SI).
# Codebook: none deposited; scales and codes from the paper's Methods/Results.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# TWO output tables:
#   waqas_2015_hads  HADS, Statement1..14, 0-3 as scored. Odd statements sum
#     to the deposit's Anxiety total on 499/500 rows, even ones to Depression
#     on all 500; means 9.71 / 7.85 as in the paper.
#   waqas_2015_sps   Social Provisions Scale, Stat1..24, 1-4. The 12
#     negatively worded SPS items are deposited already reversed: they
#     correlate +0.15..+0.38 with the positive items (none negative), and the
#     plain item sum equals the deposited Social_Support on 498/500 rows (mean
#     72.3, as in the paper). Five 0s in Stat2 (outside 1-4) and two blanks
#     dropped.
# Covariates: age; ethnicity (1 Punjabi, 2 Urdu-speaking, other codes pooled
#   as "other": 369/110/21 as in the paper); education coarsened to the
#   paper's four groups (1 illiterate 85; 2-4 high school 315; 5 intermediate
#   60; 6-7 university 40, counts match); occupation (housewife 441 /
#   employed 59); background (rural 182 / urban 208 / semiurban 110); class
#   from Household_Income (1 lower 148, 2 lower-middle 284, 3-4 middle 68).
#   Obstetric history and life-event flags not carried (sensitive and
#   unlabelled beyond the paper's prose); children's ages dropped.
# `id` = row index (no identifier deposited).
#
# Item text: NOT SHIPPED. Statement labels are positional; the HADS is a
#   register block, the Urdu SPS wording is not deposited.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0116510.s001"
RAW = os.environ.get("WAQAS2015_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}


def load():
    if RAW:
        return pd.read_csv(RAW)
    r = requests.get(URL, headers=HDR, timeout=180)
    r.raise_for_status()
    from io import StringIO
    return pd.read_csv(StringIO(r.content.decode("utf-8", errors="replace")))


def save(df, covs, items, name, values):
    long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[long["resp"].isin(values)].copy()
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
    assert len(df) == 500
    hads = [f"Statement{i}" for i in range(1, 15)]
    sps = [f"Stat{i}" for i in range(1, 25)]
    for c in sps:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    assert (df[hads[1::2]].sum(axis=1) == df["Depression"]).all()
    assert (df[hads[0::2]].sum(axis=1) == df["Anxiety"]).sum() >= 499
    assert (df[sps].sum(axis=1) == df["Social_Support"]).sum() >= 498
    assert (df["Stat2"] == 0).sum() == 5
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df["cov_age"] = df["Age"]
    df["cov_ethnicity"] = df["Ethnicity"].map(lambda v: {1: "Punjabi", 2: "Urdu-speaking"}.get(v, "other"))
    df["cov_education"] = df["Education"].map(
        {1: "illiterate", 2: "high school", 3: "high school", 4: "high school",
         5: "intermediate", 6: "university", 7: "university"})
    df["cov_occupation"] = df["Occupation"].map({1: "housewife", 2: "employed"})
    df["cov_background"] = df["background"].map({1: "rural", 2: "urban", 3: "semiurban"})
    df["cov_class"] = df["Household_Income"].map({1: "lower", 2: "lower-middle", 3: "middle", 4: "middle"})
    covs = ["cov_age", "cov_ethnicity", "cov_education", "cov_occupation", "cov_background", "cov_class"]
    assert df[covs].notna().all().all()
    assert (df["cov_education"] == "high school").sum() == 315
    save(df, covs, hads, "waqas_2015_hads", range(0, 4))
    save(df, covs, sps, "waqas_2015_sps", range(1, 5))


if __name__ == "__main__":
    convert()
