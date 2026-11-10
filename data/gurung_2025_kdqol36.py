#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0335990
# DOI: 10.1371/journal.pone.0335990
# Paper: Gurung S, Devkota N (2025). Quality of life among hemodialysis
#   patients in a referral center in Kathmandu: A mixed method study.
#   PLoS ONE 20(11): e0335990.
# Data: PLOS SI S1 Data (journal.pone.0335990.s002, .xlsx converted by the
#   authors from .sav), 260 hemodialysis patients; S1 File is the survey.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# ONE output table, gurung_2025_kdqol36: Kidney Disease Quality of Life-36
#   (Nepali), kdqol_1..36 as deposited (raw item codes, not the 0-100
#   transformed scores, which are dropped): items 1-12 the SF-12 core with
#   their own formats (1-3, 1-5, 1-6), 13-16 burden, 17-28 symptoms, 29-36
#   effects (1-5). Response formats differ by item; each is ordinal as
#   coded. One cell kdqol_4 = 5 (item 4 otherwise 1/2) is dropped.
# Dropped: socioeconomic-status items (SE1-SE9), referral/registration
#   items and the derived scores.
# Covariates: sex (SD2: 1 = male: 167 = the paper's 64.2%), SD3 / SD5 / SD6
#   are not carried (unlabelled codes).
# `id` = row index.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0335990.s002"
RAW = os.environ.get("GURUNG2025_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_gurung2025_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path)
    if not RAW:
        os.remove(path)
    return df


def convert():
    df = load()
    assert len(df) == 260
    assert (df["SD2"] == 1).sum() == 167
    df = df.reset_index(drop=True).copy()
    df["KDQOL4"] = df["KDQOL4"].where(df["KDQOL4"] != 5)
    df["id"] = df.index + 1
    df["cov_sex"] = df["SD2"].map({1: "male", 2: "female"})
    covs = ["cov_sex"]
    items = {f"KDQOL{i}": f"kdqol_{i}" for i in range(1, 37)}
    sub = df[["id"] + covs + list(items)].rename(columns=items)
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= set(range(1, 7))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(range(1, 7)))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    name = "gurung_2025_kdqol36"
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
