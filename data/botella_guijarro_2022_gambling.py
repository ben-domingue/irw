#!/usr/bin/env python3
# Source: https://doi.org/10.17632/fsd2cgcmc8.2 (Mendeley Data, CC BY 4.0)
# DOI (paper): 10.1371/journal.pone.0277520
# Paper: Botella-Guijarro A, Lloret-Irles D, Segura-Heras JV, Moriano-Leon JA
#   (2022). Characterization and prediction of gambling behavior in
#   adolescents using the COM-B model. PLoS ONE 17(11): e0277520.
# Data: adolescent_gambling_v2.csv + variable_description_en-US.docx
#   (Mendeley fsd2cgcmc8 v2; licence CC BY 4.0 via the Mendeley public API).
#   354 Spanish students aged 14-16, paired data from T1 (2016) and T3
#   (2018); suffix a = T1, c = T3.
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# TWO output tables, `wave` 1 = T1 (2016), 3 = T3 (2018), as answered:
#   botella_guijarro_2022_gambling_intent  Intent to gamble, 3 items, 1-7
#     (X4.1-X4.3). Scale score X4 = item mean at both waves (asserted >= 0.99).
#   botella_guijarro_2022_peer_norms  Perceived gambling norm among
#     peers (EDGAR PN), 4 items, 0-4 (X5.1-X5.4). Item 3 ("Most young people
#     my age have never gambled") is deposited ALREADY REVERSED at both waves
#     (it correlates +0.21..+0.58 with the others); coded norm_3r.
# Not shipped: capability (X3: the T1 description lists 6 items, the file
#   has 4, and the T1 scale score is not their mean), parents' attitude (X8)
#   and risk perception (X20) (T1 scale scores do not reproduce from the
#   items, so the keying of the deposited items is unverified).
# Covariates: sex (1 male / 2 female), age at T1.
# `id` = row index. X0 is a self-generated personal code and is not carried.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = ("https://data.mendeley.com/public-files/datasets/fsd2cgcmc8/files/"
       "0d4e9435-335b-454b-8f5b-11d272e0411e/file_downloaded")
RAW = os.environ.get("BOTELLA2022_RAW")


def load():
    if RAW:
        return pd.read_csv(RAW)
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
    r.raise_for_status()
    from io import StringIO
    return pd.read_csv(StringIO(r.text))


def build(df, covs, block, n, prefix, names, name, values):
    parts = []
    for suffix, wave in (("a", 1), ("c", 3)):
        src = [f"{block}.{i}{suffix}" for i in range(1, n + 1)]
        mean = df[src].mean(axis=1)
        ok = df[src].notna().all(axis=1)
        assert ((mean[ok] - df.loc[ok, block + suffix]).abs() < 1e-6).mean() >= 0.99
        sub = df[["id"] + covs + src].rename(columns=dict(zip(src, names)))
        long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long["wave"] = wave
        parts.append(long)
    long = pd.concat(parts, ignore_index=True)
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= set(values)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave"] + covs].sort_values(["id", "wave", "item"])
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df = load()
    assert len(df) == 354
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_sex"] = df["X1"].map({1: "male", 2: "female"})
    df["cov_age_t1"] = df["X2"]
    covs = ["cov_sex", "cov_age_t1"]
    build(df, covs, "X4", 3, "intent", ["intent_1", "intent_2", "intent_3"],
          "botella_guijarro_2022_gambling_intent", range(1, 8))
    build(df, covs, "X5", 4, "norm", ["norm_1", "norm_2", "norm_3r", "norm_4"],
          "botella_guijarro_2022_peer_norms", range(0, 5))


if __name__ == "__main__":
    convert()
