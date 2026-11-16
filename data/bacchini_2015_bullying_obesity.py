#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0142715
# DOI: 10.1371/journal.pone.0142715
# Paper: Bacchini D, Licenziati MR, Garrasi A, et al. (2015). Bullying and
#   Victimization in Overweight and Obese Outpatient Children and Adolescents:
#   An Italian Multicentric Study. PLoS ONE 10(11): e0142715.
# Data: figshare 10.6084/m9.figshare.1547919 (overw_bullying.sav), CC BY 4.0
#   (confirmed via api.figshare.com/v2/articles/1547919). 973 rows; the
#   paper's analytic sample is the 947 with filter_$ == 1 (status_bmiz > 1:
#   129 normal weight, 126 overweight, 568 moderately obese, 124 severely
#   obese, matching the abstract), which is what ships.
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# TWO output tables, adapted revised Olweus Bully/Victim Questionnaire, 11
# parallel items each, 1-5 (mai / 1 volta o due / qualche volta /
# 1 a settimana / piu di una a settimana), items as answered:
#   bacchini_2015_victimization  vict_1..11 (Vit.1..Vit11)
#   bacchini_2015_bullying       bully_1..11 (Bu1..Bu11)
#   Item k is the same behaviour in both (1 teased about appearance, 2 teased
#   for other reasons, 3 called names, 4 hit, 5 threatened, 6 ignored,
#   7 rumours, 8 stealing, 9 excluded from sports, 10 from groups, 11 from
#   parties).
# Covariates: sex (1 maschio / 2 femmina), age in months, weight status
#   (status_bmiz 2-5 as labelled), ethnicity (italian / not italian),
#   centre code (1-14, hospital).
# `id` = row index (PROGRESSIVO repeats across centres).

import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://api.figshare.com/v2/articles/1547919"
RAW = os.environ.get("BACCHINI2015_RAW")


def load():
    path = RAW
    if not path:
        meta = requests.get(URL, timeout=60).json()
        f = [x for x in meta["files"] if x["name"] == "overw_bullying.sav"][0]
        r = requests.get(f["download_url"], headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_bacchini2015_tmp.sav")
        with open(path, "wb") as fh:
            fh.write(r.content)
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
    assert len(df) == 973
    df = df[df["filter_$"] == 1].reset_index(drop=True)
    assert len(df) == 947
    vict = [f"Vit.{i}" for i in range(1, 10)] + ["Vit10", "Vit11"]
    bully = [f"Bu{i}" for i in range(1, 12)]
    df["id"] = df.index + 1
    df["cov_sex"] = df["Sex"].map({1: "male", 2: "female"})
    df["cov_age_months"] = df["age"]
    df["cov_weight_status"] = df["status_bmiz"].map(
        {2: "normal weight", 3: "overweight", 4: "moderately obese", 5: "severely obese"})
    df["cov_ethnicity"] = df["ethnic"].map({1: "italian", 2: "not italian"})
    df["cov_centre"] = df["Codice_centro"].astype("Int64")
    covs = ["cov_sex", "cov_age_months", "cov_weight_status", "cov_ethnicity", "cov_centre"]
    save(df, covs, vict, "vict", "bacchini_2015_victimization", range(1, 6))
    save(df, covs, bully, "bully", "bacchini_2015_bullying", range(1, 6))


if __name__ == "__main__":
    convert()
