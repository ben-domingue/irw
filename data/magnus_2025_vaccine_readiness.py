#!/usr/bin/env python3
# Source: https://doi.org/10.17605/OSF.IO/4QU5D (OSF, CC-By Attribution 4.0)
# DOI (paper): 10.1371/journal.pone.0328045
# Paper: Magnus KD, Dammann N, Ludecke D (2025). Vaccination readiness and
#   political party preference in Germany: Trust, collective responsibility,
#   and the populist radical right. PLoS ONE 20(7): e0328045.
# Data: OSF 4qu5d, osfio_data.csv (2,191 German adults) and the authors'
#   analyses_final.r (recodes, party labels). PLOS SI S1/S2 Tables give the
#   item wording (German / English) and weighted percentages.
# Licence: CC-By Attribution 4.0 (OSF API, node public).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# ONE output table, magnus_2025_vaccine_readiness: 9 vaccine-readiness
#   statements, 1 = disagree completely, 2 = tend to disagree, 3 = tend to
#   agree, 4 = agree completely (checked: item 1 unweighted shares 16/16/37/25%
#   = S2 Table's "I have full confidence in the safety of vaccinations"; "do
#   not know / no response" is missing in the file). Items 4, 6 and 8 are
#   deposited ALREADY REVERSE-CODED (authors' recoded_* columns) and are coded
#   vr_4r, vr_6r, vr_8r; the others vr_1..vr_9 as answered. The authors score
#   trust = items 1-3 and collective responsibility = items 4-7.
# Covariates: age group (1-6), education (1-3), party preference (labels from
#   analyses_final.r: SPD, CDU, Greens, AfD, FDP, Left), survey weight. q1
#   (unlabelled, 1/2) is not carried.
# `id` = row index.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://osf.io/download/jmdgc/"
RAW = os.environ.get("MAGNUS2025_RAW")

ITEMS = {"uke2_1_neu": "vr_1", "uke2_2_neu": "vr_2", "uke2_3_neu": "vr_3",
         "recoded_uke2_4_neu": "vr_4r", "uke2_5_neu": "vr_5", "recoded_uke2_6_neu": "vr_6r",
         "uke2_7_neu": "vr_7", "recoded_uke2_8_neu": "vr_8r", "uke2_9_neu": "vr_9"}


def load():
    if RAW:
        return pd.read_csv(RAW)
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
    r.raise_for_status()
    from io import StringIO
    return pd.read_csv(StringIO(r.text))


def convert():
    df = load()
    assert len(df) == 2191
    assert (df["uke2_1_neu"] == 3).sum() == 817
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_age_group"] = df["age_group"]
    df["cov_education"] = df["educ_rec"]
    df["cov_party"] = df["Parties"].map({1: "SPD", 2: "CDU", 3: "Greens", 4: "AfD", 5: "FDP", 6: "Left"})
    df["cov_weight"] = df["weight"]
    covs = ["cov_age_group", "cov_education", "cov_party", "cov_weight"]
    long = df[["id"] + covs + list(ITEMS)].rename(columns=ITEMS).melt(
        id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= {1, 2, 3, 4}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=[1, 2, 3, 4])
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    name = "magnus_2025_vaccine_readiness"
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
