#!/usr/bin/env python3
# Source: https://doi.org/10.5281/zenodo.17905001 (Zenodo, CC BY 4.0)
# DOI (paper): 10.1371/journal.pone.0341736
# Paper: Cordero DM, Villavicencio MF, Luna KA, et al. (2026). Intention to
#   adopt electric transportation services by university students in
#   emerging countries. PLoS ONE 21(1): e0341736.
# Data: SURVEY_1158_SOURCE.Ecuador_Colombia_Peru.Final.xlsx, sheet
#   UniversityStudents (1,158 students) + sheet Dictionary (item wording,
#   1 = strongly disagree .. 5 = strongly agree). Licence cc-by-4.0 (Zenodo
#   API).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# SIX output tables, one per construct (paper Table 1), 1-5, as answered,
#   item codes = deposit names lower-cased:
#   cordero_2026_ev_attitude (AEV1-3), _perceived_risk (PRI1-3),
#   _emotions (EMO1-3), _social_influence (SOI1-3), _hyperbolic_discounting
#   (HDI1, HDI12 = the dictionary's HDI2), _use_intention (IET1-2).
# Not shipped: consumer characteristics (CCH): the dictionary documents
#   CCH1-2 but the file has CCH1-3, so the third item is unidentified.
# Covariates: country (1 Ecuador, 2 Peru, 3 Colombia), gender (1 male,
#   2 female, 3 LGBTI), age band (1 17-22, 2 23-27, 3 28+).
# `id` = row index.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://zenodo.org/records/17905001/files/SURVEY_1158_SOURCE.Ecuador_Colombia_Peru.Final.xlsx?download=1"
RAW = os.environ.get("CORDERO2026_RAW")

BLOCKS = [("ev_attitude", ["AEV1", "AEV2", "AEV3"]), ("perceived_risk", ["PRI1", "PRI2", "PRI3"]),
          ("emotions", ["EMO1", "EMO2", "EMO3"]), ("social_influence", ["SOI1", "SOI2", "SOI3"]),
          ("hyperbolic_discounting", ["HDI1", "HDI12"]), ("use_intention", ["IET1", "IET2"])]


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_cordero2026_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, sheet_name="UniversityStudents")
    if not RAW:
        os.remove(path)
    return df


def convert():
    df = load()
    assert len(df) == 1158
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_country"] = df["COUNTRY"].map({1: "ecuador", 2: "peru", 3: "colombia"})
    df["cov_gender"] = df["GENDER"].map({1: "male", 2: "female", 3: "lgbti"})
    df["cov_age_band"] = df["AGE"].map({1: "17-22", 2: "23-27", 3: "28+"})
    covs = ["cov_country", "cov_gender", "cov_age_band"]
    for label, src in BLOCKS:
        mapping = {c: ("hdi2" if c == "HDI12" else c.lower()) for c in src}
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
        name = f"cordero_2026_{label}"
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
