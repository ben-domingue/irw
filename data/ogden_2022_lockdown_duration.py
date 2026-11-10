#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0271609
# DOI: 10.1371/journal.pone.0271609
# Paper: Ogden RS, Piovesan A (2022). How long was it for you? Memories of the
#   duration of the UK covid-19 lockdown. PLoS ONE 17(7): e0271609.
# Data: PLOS SI S1 Data (journal.pone.0271609.s001, .sav), 767 UK adults,
#   online questionnaire one year after the first national lockdown.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# TWO output tables, items as answered:
#   ogden_2022_dass21  DASS-21, dass_1..21, coded 1-4 in the deposit
#     ("Did not apply to me at all" .. "Applied to me very much or most of
#     the time"); the deposited Depression/Anxiety/Stress columns are the raw
#     sums of these 1-4 codes (asserted for Depression).
#   ogden_2022_tlx     modified NASA-TLX (average day over the year), tlx_1..6
#     in the instrument's order (mental, physical, temporal, success, effort,
#     frustration), 1-5 "Very low".."Very high"; success is as answered.
# Dropped: the single-item ratings (compliance, social interaction, physical
#   activity, routine, year length) and derived scores.
# Covariates: age, gender (1 Male, 2 Female, 3 Other: 504/767 female),
#   covid risk (1-3 as deposited), shielding (1/2 as deposited).
# `id` = row index.

import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0271609.s001"
RAW = os.environ.get("OGDEN2022_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_ogden2022_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, _ = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df


def save(df, covs, src, prefix, name, values):
    mapping = {c: f"{prefix}_{k}" for k, c in enumerate(src, 1)}
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
    assert len(df) == 767
    dass = [f"DASS{i}" for i in range(1, 22)]
    tlx = [f"TLX{i}" for i in range(1, 7)]
    dep = df[[f"DASS{i}" for i in (3, 5, 10, 13, 16, 17, 21)]].sum(axis=1, min_count=7)
    ok = dep.notna() & df["Depression"].notna()
    assert (dep[ok] == df.loc[ok, "Depression"]).all()
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df["cov_age"] = df["Age"]
    df["cov_gender"] = df["Gender"].map({1: "male", 2: "female", 3: "other"})
    df["cov_covid_risk"] = df["Covid_Risk"]
    df["cov_shielding"] = df["Shielding"]
    covs = ["cov_age", "cov_gender", "cov_covid_risk", "cov_shielding"]
    save(df, covs, dass, "dass", "ogden_2022_dass21", range(1, 5))
    save(df, covs, tlx, "tlx", "ogden_2022_tlx", range(1, 6))


if __name__ == "__main__":
    convert()
