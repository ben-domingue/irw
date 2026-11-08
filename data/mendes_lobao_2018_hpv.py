#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0206726
# DOI: 10.1371/journal.pone.0206726
# Paper: Mendes Lobao W, Duarte FG, Burns JD, de Souza Teles Santos CA,
#   Chagas de Almeida MC, Reingold A, Duarte Moreira E (2018). Low coverage
#   of HPV vaccination in the national immunization programme in Brazil:
#   Parental vaccine refusal or barriers in health-service based vaccine
#   delivery? PLoS ONE 13(11): e0206726.
# Data: PLOS Supporting Information S1 Dataset (journal.pone.0206726.s001,
#   .sav, no value labels); S2 Questionnaire (English) gives the codes.
#   826 parents in seven Brazilian cities, telephone interviews 2015-16.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 6.
#
# TWO output tables:
#   mendes_lobao_2018_hpv_knowledge  the paper's 21 true/false knowledge
#     statements (Table 2: B2-B11, C22, C31-C40), SCORED 1 = correct,
#     0 = incorrect against the paper's T/F key. "I don't know" (code 2,
#     not read aloud) is a non-response and is dropped, not scored 0.
#   mendes_lobao_2018_hpv_attitudes  the 19 remaining agree/disagree
#     statements C11-C21, C23-C30, 1 = yes I agree, 0 = no; code 2
#     (don't know) dropped. Stored as answered (no reversals).
# Codes checked against Table 2: with 1 = yes the share endorsing each
#   true statement matches the paper's % correct (e.g. B3 92/92, B6 55/55,
#   B11 88/89, C34 82/86); for the false statements the paper's % equals
#   100 minus the % saying yes (B2 66, B9 37), i.e. the paper counted
#   "don't know" as correct there. This table does not.
# Covariates: city (labelled from the questionnaire), education, marital
#   status. Sex (A8) is blank for 673 of 826 rows and is dropped; age is not
#   deposited. All free-text "other/what?" fields dropped.
# `id` is the row index (the deposit carries no identifier).
#
# Item text: NOT SHIPPED. Study-written KAP questionnaire, English and
#   Portuguese versions in S1/S2 Questionnaire (CC BY 4.0). Cheap.

import io
import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0206726.s001"
RAW = os.environ.get("MENDES_LOBAO_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}

# Table 2 key: True / False statements.
KEY = {
    "b2": 0, "b3": 1, "b4": 0, "b5": 0, "b6": 1, "b7": 0, "b8": 1, "b9": 0,
    "b10": 0, "b11": 1, "c22": 1, "c31": 0, "c32": 1, "c33": 0, "c34": 1,
    "c35": 0, "c36": 0, "c37": 1, "c38": 0, "c39": 0, "c40": 1,
}
ATT = [f"c{i}" for i in range(11, 31) if i != 22]
CITY = {1: "Belem", 2: "Belo Horizonte", 3: "Brasilia", 4: "Porto Alegre",
        5: "Rio de Janeiro", 6: "Salvador", 7: "Sao Paulo"}
EDU = {1: "no formal education", 2: "adult literacy class", 3: "adult school",
       4: "primary school", 5: "middle school", 6: "high school",
       7: "high school equivalence", 8: "technical certificate",
       9: "college degree", 10: "graduate degree"}
MAR = {1: "married or civil union", 2: "separated", 3: "divorced", 4: "widowed",
       5: "single"}


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        path = os.path.join(OUT_DIR, "_mendes_lobao_tmp.sav")
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(path, "wb") as f:
            f.write(r.content)
    df, _ = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df


def save(long, name, items):
    long = long[long["resp"].notna()].copy()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {0, 1}
    long = long.sort_values(["id", "item"])
    checks = run_qc(long, permitted_values={c: [0, 1] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df = load()
    assert df.shape == (826, 147), df.shape
    df["id"] = range(1, len(df) + 1)
    df["cov_city"] = df["city"].map(CITY)
    df["cov_education"] = df["a7"].map(EDU)
    df["cov_marital_status"] = df["a3"].map(MAR)
    assert df["cov_city"].notna().all()
    covs = ["cov_city", "cov_education", "cov_marital_status"]
    for c in list(KEY) + ATT:
        assert set(df[c].dropna()) <= {0, 1, 2}, c
    # B3 is endorsed by 92% (paper: 92% correct); B11 by 88% (paper 89%).
    assert round(100 * (df["b3"] == 1).mean()) == 92

    k = df[["id"] + covs + list(KEY)].melt(id_vars=["id"] + covs, var_name="item", value_name="ans")
    k = k[k["ans"].isin([0, 1])].copy()
    k["resp"] = (k["ans"] == k["item"].map(KEY)).astype(int)
    save(k[["id", "item", "resp"] + covs], "mendes_lobao_2018_hpv_knowledge", list(KEY))

    a = df[["id"] + covs + ATT].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    a = a[a["resp"].isin([0, 1])]
    save(a[["id", "item", "resp"] + covs], "mendes_lobao_2018_hpv_attitudes", ATT)


if __name__ == "__main__":
    convert()
