#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.24718332 (figshare, CC BY 4.0)
# DOI (paper): 10.1371/journal.pone.0307870
# Paper: Tavares da Silva W, Castelo PM, Pereira LJ, et al. (2024). Score of
#   fear of COVID-19 and physical activity level are related to the habitual
#   consumption of dietary supplements. PLoS ONE 19(9): e0307870.
# Data: figshare 24718332, data.xlsx (sheet data), 461 Brazilian adults
#   (online questionnaire). Licence CC BY 4.0 (api.figshare.com). Column
#   headers for the fear items are the Portuguese item stems.
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# TWO output tables, as answered:
#   tavares_da_silva_2024_fcv19s  Fear of COVID-19 Scale (Brazilian
#     Portuguese), 7 items, 1-5, in the scale's order (first stem "Estou mais
#     amedrontado com a COVID-19"); sum = deposited TOTAL (asserted).
#   tavares_da_silva_2024_lifestyle  Changes in Lifestyle-Related Behavior
#     (Brazilian adaptation), 20 items, 1-5, the deposit's raw columns
#     bruto1-20 (sum = TOTAL1_A, asserted; the DOMINV/TOTALINV columns are
#     the authors' re-keyed scores and are dropped).
# Covariates: age. Sex is not carried: this file codes it 0/1 while the
#   companion file's legend gives 1 masculino / 2 feminino, so the mapping
#   is unverified.
# `id` = row index.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
API = "https://api.figshare.com/v2/articles/24718332"
RAW = os.environ.get("TAVARES2024_RAW")


def load():
    path = RAW
    if not path:
        meta = requests.get(API, timeout=60).json()
        url = meta["files"][0]["download_url"]
        r = requests.get(url, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_tavares2024_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, sheet_name="data")
    if not RAW:
        os.remove(path)
    return df


def save(df, covs, mapping, name):
    src = list(mapping)
    long = df[["id"] + covs + src].rename(columns=mapping).melt(
        id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= set(range(1, 6))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(range(1, 6)))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df = load()
    assert len(df) == 461
    cols = list(df.columns)
    i = cols.index("MEDOEstoumaisamedrontadocomaCOVID19")
    fcv = cols[i:i + 7]
    assert fcv[-1].startswith("Meucora")
    assert (df[fcv].sum(axis=1) == df["TOTAL"]).all()
    life = [f"bruto{k}" for k in range(1, 21)]
    ok = df[life].notna().all(axis=1)
    assert (df.loc[ok, life].sum(axis=1) == df.loc[ok, "TOTAL1_A"]).all()
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_age"] = df["Age"]
    covs = ["cov_age"]
    save(df, covs, {c: f"fcv_{k}" for k, c in enumerate(fcv, 1)}, "tavares_da_silva_2024_fcv19s")
    save(df, covs, {c: f"life_{c[5:]}" for c in life}, "tavares_da_silva_2024_lifestyle")


if __name__ == "__main__":
    convert()
