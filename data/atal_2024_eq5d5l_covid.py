#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/TBCUD7 (Harvard Dataverse, CC0 1.0)
# DOI (paper): 10.1371/journal.pone.0300891
# Paper: Atal R, Bedregal P, Carrasco JA, Gonzalez F, Harrison R, Vizcaya C
#   (2024). The Impacts of COVID-19 Restrictions on Quality Adjusted Life
#   Years (QALY): Heterogeneous effects and post-pandemic recovery. PLoS ONE
#   19(3): e0300891.
# Data: "Replication Data for: The Impacts of COVID-19 Restrictions on QALY",
#   COVID_qaly.tab (Dataverse file 8556075): 1,506 Chilean heads of household
#   surveyed in May 2022.
# License: CC0 1.0 (Dataverse API).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# ONE output table, atal_2024_eq5d5l: EQ-5D-5L descriptive system, 5 items,
#   1-5 (mo, sc, ua, pd, ad = deposit P8a..P8e), each answered retrospectively
#   for three moments, carried in `wave`: 1 = before the pandemic (March
#   2020), 2 = peak restrictions (June 2020 - August 2021), 3 = "today"
#   (May 2022). Deposit suffix 1/2/3 = these moments (paper, Methods).
# Covariates: sex (P1e; 2 = female), age (P1g), survey weight (POND) as
#   cov_weight. Table 1 is weighted: POND-weighted age mean 49.7 and share
#   female 0.44 reproduce it (asserted); unweighted they are 47.7 and 0.63.
#   Municipality code, nationality text and P1h/P2a (unlabelled) dropped.
# `id` = row index.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://dataverse.harvard.edu/api/access/datafile/8556075"
RAW = os.environ.get("ATAL2024_RAW")


def load():
    if RAW:
        return pd.read_csv(RAW, sep="\t")
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
    r.raise_for_status()
    from io import StringIO
    return pd.read_csv(StringIO(r.text), sep="\t")


def convert():
    df = load()
    assert len(df) == 1506
    w = df["POND"]
    assert abs((df["P1g"] * w).sum() / w.sum() - 49.7) < 0.05
    assert abs(((df["P1e"] == 2) * w).sum() / w.sum() - 0.44) < 0.01
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_sex"] = df["P1e"].map({1: "male", 2: "female"})
    df["cov_age"] = df["P1g"]
    df["cov_weight"] = df["POND"]
    covs = ["cov_sex", "cov_age", "cov_weight"]
    dims = {"a": "mo", "b": "sc", "c": "ua", "d": "pd", "e": "ad"}
    parts = []
    for w in (1, 2, 3):
        src = {f"P8{k}{w}": v for k, v in dims.items()}
        sub = df[["id"] + covs + list(src)].rename(columns=src)
        long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long["wave"] = w
        parts.append(long)
    long = pd.concat(parts, ignore_index=True)
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= set(range(1, 6))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave"] + covs].sort_values(["id", "wave", "item"])
    checks = run_qc(long, permitted_values=list(range(1, 6)))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    name = "atal_2024_eq5d5l"
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
