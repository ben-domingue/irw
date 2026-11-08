#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0285797
# DOI: 10.1371/journal.pone.0285797
# Paper: Mojsa-Kaja J, Szklarczyk-Smolana K, Niedzielska-Andres E, Kurpinska A,
#   Suraj-Prazmowska J, Walczak M, et al. (2023). COVID-19-related social
#   isolation and symptoms of depression and anxiety in young men in Poland:
#   Does insomnia mediate the relationship? PLoS ONE 18(5): e0285797.
# Data: RODBUK (Jagiellonian University Dataverse) doi:10.57903/UJ/DPIPJO,
#   file RUJ_Data_for_PlosOne_paper.xlsx (datafile id 48). 1,025 Polish men
#   aged 18-35, web survey.
# License: CC BY 4.0 (Dataverse license field, confirmed on the dataset page).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 7.
#
# THREE output tables:
#   mojsa_kaja_2023_bdi2   BDI-II, 21 items Q1-Q21, 0-3.
#   mojsa_kaja_2023_stai_s STAI state form, 20 items 1-4 as answered (X1_k).
#     The deposit also carries reversed copies RX1, RX2, RX5, RX8, RX10, RX11,
#     RX15, RX16, RX19, RX20; each equals 5 - X1_k on every row (asserted),
#     and the raw items plus those reversals reproduce the deposited total.
#     The reversed copies are not shipped.
#   mojsa_kaja_2023_ais    Athens Insomnia Scale, 8 items 0-3.
# Checks: each item sum equals the deposit's scale total on every row
#   (asserted); N = 1,025 and mean age 24.08 as in the paper (asserted).
# Dropped: the social isolation index (built from recoded 0/1 indicators of
#   three questions; not item responses), the scale totals.
# Covariates: age, education, marital status, place of residence (Polish
#   labels translated). All respondents are men (no sex covariate).
# `id` is the deposit's running number LP (1..1025, no other identifier).
#
# Item text: NOT SHIPPED. BDI-II, STAI and AIS are published instruments.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://uj.rodbuk.pl/api/access/datafile/48"
RAW = os.environ.get("MOJSAKAJA2023_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}

EDU = {
    "brak wykształcenia": "none",
    "wykształcenie podstawowe/ zawodowe": "primary/vocational",
    "wykształcenie średnie": "secondary",
    "wykształcenie wyższe": "higher",
}
MAR = {
    "Singiel": "single",
    "W związku nieformalnym": "informal relationship",
    "{Mężatka:Żonaty}": "married",
    "Wdo{wa:wiec}": "widowed",
    "Rozwiedzion{a:y}": "divorced",
}
RES = {
    "Wieś": "village",
    "Miasto do 19 999 mieszkańców": "town <20k",
    "Miasto od 20 000 do 99 999 mieszkańców": "town 20k-99k",
    "Miasto od 100 000 do 499 999 mieszkańców": "city 100k-499k",
    "Miasto powyżej 500 000 mieszkańców": "city 500k+",
}


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_mojsakaja2023_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, header=1)
    if not RAW:
        os.remove(path)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def save(df, covs, items, name, values):
    long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(values)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df = load()
    assert len(df) == 1025 and df["LP"].is_unique
    assert (df["Male/Female"] == "Male").all()
    assert round(df["Age"].mean(), 2) == 24.08
    df["id"] = df["LP"].astype(int)
    df["cov_age"] = df["Age"]
    df["cov_education"] = df["Education"].map(EDU)
    df["cov_marital_status"] = df["Marital status"].map(MAR)
    assert df["cov_education"].notna().all() and df["cov_marital_status"].notna().all()
    df["cov_residence"] = (
        df["Locality"]
        .map(RES)
    )
    assert df["cov_residence"].notna().all()
    covs = ["cov_age", "cov_education", "cov_marital_status", "cov_residence"]

    bdi = [f"Q{i}" for i in range(1, 22)]
    assert (df[bdi].sum(axis=1) == df["BDI-II_SUM"]).all()
    out = df.rename(columns={q: f"bdi{q[1:]}" for q in bdi})
    save(out, covs, [f"bdi{i}" for i in range(1, 22)], "mojsa_kaja_2023_bdi2", [0, 1, 2, 3])

    stai_src = {}
    for c in df.columns:
        if c.startswith("X1_") and "SUM" not in c:
            stai_src[int(c.split()[0][3:])] = c
    assert sorted(stai_src) == list(range(1, 21))
    rev = [int(c[2:]) for c in df.columns if c.startswith("RX")]
    assert rev == [1, 2, 5, 8, 10, 11, 15, 16, 19, 20]
    for k in rev:
        assert (df[f"RX{k}"] == 5 - df[stai_src[k]]).all()
    total = sum(df[f"RX{k}"] if k in rev else df[stai_src[k]] for k in range(1, 21))
    assert (total == df["STAI-State X1_SUM"]).all()
    out = df.rename(columns={stai_src[k]: f"stai{k}" for k in stai_src})
    save(out, covs, [f"stai{k}" for k in range(1, 21)], "mojsa_kaja_2023_stai_s", [1, 2, 3, 4])

    asi = [c for c in df.columns if c.startswith("ASI")]
    assert len(asi) == 8
    assert (df[asi].sum(axis=1) == df["Insomnia(ASI)_Sum"]).all()
    out = df.rename(columns={c: f"ais{c.split()[0][3:]}" for c in asi})
    save(out, covs, [f"ais{i}" for i in range(1, 9)], "mojsa_kaja_2023_ais", [0, 1, 2, 3])


if __name__ == "__main__":
    convert()
