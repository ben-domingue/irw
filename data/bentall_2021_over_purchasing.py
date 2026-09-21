#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0246339
# DOI: 10.1371/journal.pone.0246339
# Data: journal.pone.0246339_S1_Data.sav (S1 Data)
# License: CC BY 4.0 (verified on the article page and in Crossref metadata)
#
# Bentall et al. (2021), "Pandemic buying: Testing a psychological model
# of over-purchasing and panic buying using data from the United Kingdom
# and the Republic of Ireland during the early phase of the COVID-19
# pandemic." PLOS ONE. N=3,066 (UK 2,025 / Ireland 1,041).
#
# Almost all of this deposit is composite scores -- the file ships
# IntolCert_tot, LOC_*, Paranoia_tot, DEP, ANX, the five TIPI
# personality sums, RWA_tot, DAnx_tot and CRT_tot as totals with no
# constituent items. Exactly one instrument survives at item level: the
# nine-item over-purchasing measure (Stock_1..Stock_9), which is what
# this script ships. The two neighbourhood-trust questions and the
# single belongingness question are carried as covariates rather than as
# their own table -- two items is not a scale.
#
# Item text: shipped (SPSS variable labels give each item's object, the
# value labels give all five anchors, and the shared stem is quoted
# verbatim from the article's Measures section, "Over-purchasing").
import os
import numpy as np
import pandas as pd
import pyreadstat
from irw_validate.compat import run_qc

RAW = os.environ.get("BENTALL_SAV", "journal.pone.0246339_S1_Data.sav")
OUTDIR = os.path.join(os.path.dirname(__file__), "..", "automated_finding", "irw_output")

ITEMS = [f"Stock_{n}" for n in range(1, 10)]

COVS = {
    "country": "cov_country",
    "age": "cov_age",
    "Gender_b": "cov_gender",
    "adults#": "cov_n_adults",
    "children#": "cov_n_children",
    "income": "cov_income_band",
    "lost_income_b": "cov_lost_income",
    "Neigh_belog": "cov_neighbourhood_belonging",
    "Neigh_Trust1": "cov_neighbourhood_trust_keys",
    "Neigh_Trust2": "cov_neighbourhood_trust_shopping",
    "Depression_dx": "cov_depression_diagnosis",
    "Anxiety_dx": "cov_anxiety_diagnosis",
    "Ill_self": "cov_at_risk_condition_self",
    "Ill_fam": "cov_at_risk_condition_family",
    "Self_infected": "cov_infected_self",
    "Other_infected": "cov_infected_other",
    "ANX_covid": "cov_covid_anxiety_0_100",
    "RISK_1month": "cov_perceived_risk_1month",
}

# Totals/sums with no constituent items in the deposit.
COMPOSITES = ["IntolCert_tot", "LOC_Chance", "LOC_POthers", "LOC_Internal",
              "Paranoia_tot", "DEP", "ANX", "Extra", "Agree", "Conscient",
              "Neuro", "Open", "RWA_tot", "DAnx_tot", "CRT_tot",
              "Neigh_Trust_tot", "Total_STOCK",
              "No_purchasing_eq9", "No_purchasing_LT18"]

# `gender` carries 536 zeros and 3 -99s that the file's own value labels
# do not define (labels run 1..5 only). `Gender_b` is the depositors' own
# clean binary recode and is used instead; the unlabelled codes are not
# guessed at.
UNUSABLE = ["gender"]


def main():
    df, meta = pyreadstat.read_sav(RAW)

    accounted = set(ITEMS) | set(COVS) | set(COMPOSITES) | set(UNUSABLE)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"columns: {len(ITEMS)} items, {len(COVS)} covariates, "
          f"{len(COMPOSITES)} composites dropped, "
          f"{len(UNUSABLE)} dropped as unlabelled ({UNUSABLE})")

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    assert df["id"].nunique() == len(df)

    df = df.rename(columns=COVS)
    cov_cols = sorted(COVS.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                   var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = pd.to_numeric(long["resp"])

    bad = long.loc[~long["resp"].isin([1, 2, 3, 4, 5]), "resp"].unique()
    assert len(bad) == 0, f"off-scale resp values: {bad}"
    assert (long["resp"] % 1 == 0).all(), "fractional resp -- check for imputation"

    long = long[["id", "item", "resp"] + cov_cols]

    n = long["id"].nunique()
    assert n >= 100, f"below the 100-id floor: {n}"
    print(f"{len(long):,} responses | {n:,} ids | {long['item'].nunique()} items")

    bad = [c for c in run_qc(long, permitted_values=[1, 2, 3, 4, 5],
                             item_constructs={i: "bentall_2021_over_purchasing" for i in long["item"].unique()})
           if c.status == "fail"]
    assert not bad, f"run_qc failures: {[(c.name, c.detail) for c in bad]}"

    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, "bentall_2021_over_purchasing.csv")
    long.to_csv(out, index=False)
    print("wrote", out)


if __name__ == "__main__":
    main()
