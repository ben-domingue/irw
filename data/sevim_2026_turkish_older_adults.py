#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/XMLRKT
# DOI: 10.7910/DVN/XMLRKT (data; no paper DOI on the record)
#   Sevim, K. (2026). "Replication Data for: The Health Cost of Loneliness in
#   Old Age: How Migration Context Shapes Frailty as a Pathway to
#   Health-Related Quality of Life among Turkish Older Adults." Harvard
#   Dataverse.
# Data: yasli.csv (484 community-dwelling Turkish older adults, interviewed in
#   Turkish by CAPI: 258 in Türkiye, 226 in Germany), with the deposit's R
#   cleaning/analysis scripts (data_cleaning.R: "country: 1=Türkiye,
#   2=Almanya").
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped -- codes only; TFI, the De Jong Gierveld scale and
#   SF-12 are published third-party instruments.
#
# Tables (codes as deposited):
#   sevim_2026_tfi    t11_2..t25_2, Tilburg Frailty Indicator part B, 15
#                     items scored 0/1; their sum equals the deposit's
#                     Total_Fraility on every row (asserted)
#   sevim_2026_djgls  l1_2..l11_2, De Jong Gierveld Loneliness Scale, 11
#                     items 0-2 as deposited; the six "t"-suffixed items
#                     (l2,l3,l5,l6,l9,l10) are the deposit's transformed
#                     (reverse-keyed) emotional items, and all 11 sum to its
#                     total_lonliness on every row (asserted)
#   sevim_2026_sf12   q1_2..q12_2, SF-12 as answered (item formats differ:
#                     1-5, 1-3, 1-2, 1-6); the deposit's R reverses q1, q8,
#                     q9, q10 for scoring, not applied here
# id: country * 1000 + ID (ID restarts at 1 in each country sample).
# Covariates: cov_country, cov_sex, cov_age, cov_marital_status,
#   cov_birth_country, cov_education, cov_income_band, cov_lifestyle,
#   cov_chronic_illness, cov_satisfied_environment (Turkish labels as given).
#   Four respondents report ages 18-21; kept as deposited.
# Dropped: experienced_t9 (free-text answer naming a stressful life event,
#   e.g. a bereavement: a short free-text field, dropped in no form);
#   subscale/total scores; PCS12/MCS12/Total_QoL.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = "https://dataverse.harvard.edu/api/access/datafile/13202921?format=original"
TFI = [f"t{i}_2" for i in range(11, 26)]
DJG = ["l1_2", "l2_2t", "l3_2t", "l4_2", "l5_2t", "l6_2t", "l7_2", "l8_2",
       "l9_2t", "l10_2t", "l11_2"]
SF12 = [f"q{i}_2" for i in range(1, 13)]
SF12_RANGE = {"q1_2": 5, "q2_2": 3, "q3_2": 3, "q4_2": 2, "q5_2": 2, "q6_2": 2,
              "q7_2": 2, "q8_2": 5, "q9_2": 6, "q10_2": 6, "q11_2": 6, "q12_2": 5}
COVS = {"sex_t1": "cov_sex", "age_t2": "cov_age",
        "marital_status_t3": "cov_marital_status", "born_t4": "cov_birth_country",
        "education_t5": "cov_education", "income_t6": "cov_income_band",
        "life_style_t7": "cov_lifestyle", "chronic_illness_t8": "cov_chronic_illness",
        "satisfy_living_environment_10": "cov_satisfied_environment"}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content))
    assert d.shape == (484, 60), d.shape
    assert (d[TFI].sum(axis=1) == d["Total_Fraility"]).all()
    assert (d[DJG].sum(axis=1) == d["total_lonliness"]).all()
    d["id"] = d["country"] * 1000 + d["ID"]
    assert d["id"].is_unique
    d["cov_country"] = d["country"].map({1: "Türkiye", 2: "Germany"})
    d = d.rename(columns=COVS)
    cov_cols = ["cov_country"] + list(COVS.values())
    for c in cov_cols:
        if d[c].dtype == object:
            d[c] = d[c].str.strip()

    tables = {
        "sevim_2026_tfi": {c: {0, 1} for c in TFI},
        "sevim_2026_djgls": {c: {0, 1, 2} for c in DJG},
        "sevim_2026_sf12": {c: set(range(1, k + 1)) for c, k in SF12_RANGE.items()},
    }
    for table, perm in tables.items():
        cols = list(perm)
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            assert set(g["resp"]) <= perm[it], (it, set(g["resp"]))
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values=perm)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:130]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
