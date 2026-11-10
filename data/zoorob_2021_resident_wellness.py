#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0250104
# DOI: 10.1371/journal.pone.0250104
# Paper: Zoorob D, Shah S, La Saevig D, Murphy C, Aouthmany S, Brickman K
#   (2021). Insight into resident burnout, mental wellness, and coping
#   mechanisms early in the COVID-19 pandemic. PLoS ONE 16(4): e0250104.
# Data: PLOS SI S1 Data (journal.pone.0250104.s001, .xlsx), 1,115 US resident
#   physicians; the first data row holds the code legends and is dropped.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# TWO output tables:
#   zoorob_2021_wellbeing  Resident Well-Being Index (Mayo Clinic), 7 yes/no
#     items (0 = no, 1 = yes; burnout, hardening, depressed, falling asleep,
#     piling up, emotional problems, physical health), in deposit order. Sum =
#     the deposited Wellness Score (asserted).
#   zoorob_2021_brs  Brief Resilience Scale, 6 items, 1-5. The negatively
#     worded items 2, 4, 6 are deposited ALREADY REVERSE-SCORED (higher = more
#     resilient): every inter-item r is positive (0.44-0.62) and the six sum
#     to the deposited Total Resilience (asserted). Item codes brs_2r, brs_4r,
#     brs_6r flag this; the BRS key fixes which items they are.
# Covariates (code legends from the deposit's first row): gender, age band
#   (<25, 25-29, 30-34, 35-39, >39), marital status, US region, mindfulness
#   strategies (0/1), institutional support (0/1; one stray 11 set missing).
# `id` = row index.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0250104.s001"
RAW = os.environ.get("ZOOROB2021_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_zoorob2021_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path)
    if not RAW:
        os.remove(path)
    return df


def save(df, covs, mapping, name, values):
    src = list(mapping)
    sub = df[["id"] + covs + src].rename(columns=mapping)
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= set(values)
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
    assert str(df.iloc[0, 0]).startswith("Response")
    df = df.iloc[1:].reset_index(drop=True).copy()
    assert len(df) == 1115
    cols = list(df.columns)
    wb = cols[8:15]
    brs = cols[16:22]
    assert wb[0].startswith("During the past month, have you felt burned out")
    assert brs[0].startswith("I tend to bounce back")
    num = df[wb + brs + [cols[15], cols[22]]].apply(pd.to_numeric)
    ok = num[cols[15]].notna()
    assert (num.loc[ok, wb].sum(axis=1) == num.loc[ok, cols[15]]).all()
    assert (num.loc[ok, brs].sum(axis=1) == num.loc[ok, cols[22]]).all()
    df[wb + brs] = num[wb + brs]
    df["id"] = df.index + 1
    c = lambda i: pd.to_numeric(df[cols[i]])  # noqa: E731
    df["cov_gender"] = c(0).map({0: "female", 1: "male"})
    df["cov_age_band"] = c(1).map({0: "<25", 1: "25-29", 2: "30-34", 3: "35-39", 4: ">39"})
    df["cov_marital"] = c(2).map({0: "single", 1: "married", 2: "divorced"})
    df["cov_region"] = c(4).map({0: "midwest", 1: "northeast", 2: "south", 3: "west"})
    df["cov_mindfulness"] = c(6)
    df["cov_institutional_support"] = c(7).where(c(7).isin([0, 1]))
    covs = ["cov_gender", "cov_age_band", "cov_marital", "cov_region", "cov_mindfulness",
            "cov_institutional_support"]
    save(df, covs, {q: f"wb_{k}" for k, q in enumerate(wb, 1)}, "zoorob_2021_wellbeing", (0, 1))
    names = ["brs_1", "brs_2r", "brs_3", "brs_4r", "brs_5", "brs_6r"]
    save(df, covs, dict(zip(brs, names)), "zoorob_2021_brs", range(1, 6))


if __name__ == "__main__":
    convert()
