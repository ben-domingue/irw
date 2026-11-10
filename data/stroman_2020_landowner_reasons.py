#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0238688
# DOI: 10.1371/journal.pone.0238688
# Paper: Stroman DA, Kreuter UP, Wonkka CL (2020). Landowner perceptions of
#   woody plants and prescribed fire in the Southern Plains, USA. PLoS ONE
#   15(9): e0238688.
# Data: PLOS SI S2 File "Anonymized data file" (journal.pone.0238688.s002,
#   old BIFF .xls read with xlrd), 680 rural landowners in Oklahoma and
#   Texas (mail survey); S1 File is the questionnaire.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# ONE output table, stroman_2020_ownership_reasons: questionnaire E1, "how
#   important each reason is to you as to why you own your property", 7-point
#   1 = not at all important .. 7 = very important. The deposit's E1k column
#   is taken to be the k-th of the questionnaire's 19 reasons (E11 operate a
#   farm or ranch ... E118 earn a profit); E113 (browsing livestock) and E119
#   (sell the land someday at a profit) are not in the
#   deposit, so 17 items ship, coded e1_<k>. Values 0.7 / 0.8 (undocumented,
#   not scale points), 8 and 76 (out of range) are dropped.
# Dropped: the A1 attitude items (only 4 of the block deposited), C3/D3,
#   derived factor scores and dummies.
# Covariates: state (0/1 as deposited), age (ageinyr15).
# `id` = row index.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0238688.s002"
RAW = os.environ.get("STROMAN2020_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_stroman2020_tmp.xls")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, engine="xlrd")
    if not RAW:
        os.remove(path)
    return df


def convert():
    df = load()
    assert len(df) == 680
    src = [c for c in df.columns if c.startswith("E1") and "factor" not in c]
    assert len(src) == 17
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_state"] = df["state"]
    df["cov_age"] = df["ageinyr15"]
    covs = ["cov_state", "cov_age"]
    mapping = {c: f"e1_{c[2:]}" for c in src}
    long = df[["id"] + covs + src].rename(columns=mapping).melt(
        id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].isin([1, 2, 3, 4, 5, 6, 7])].copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(range(1, 8)))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    name = "stroman_2020_ownership_reasons"
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
