#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0310437
# DOI: 10.1371/journal.pone.0310437
# Paper: Sogbesan A, Bakare AA, Herzig van Wees S, Salako J, et al. (2026).
#   Exploring COVID-19 pandemic perceptions and vaccine uptake among community
#   members and primary healthcare workers in Nigeria: A mixed methods study.
#   PLoS ONE 21(3): e0310437.
# Data: PLOS SI S1 Dataset (journal.pone.0310437.s007, .xlsx), 2,602
#   respondents (community members, caregivers, primary healthcare workers);
#   S2 Dataset is the data dictionary. Values are stored as text labels.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# ONE output table, sogbesan_2026_covid_perceptions: 11 statements about
#   COVID-19 (not real, death sentence, disease of elites, no COVID in
#   Nigeria, Africans immune, affects young and old, punishment, biological
#   weapon, designed to sell drugs, exaggerated, scam), 1 = agree,
#   0 = disagree, as answered (item 6 "affects young and old" is the one
#   accurate statement; not reverse-keyed). Item codes perc_1..perc_11 in
#   that order (the deposit's column names trip the covariate lint). "don't know" is a labelled
#   non-response and is dropped (datastandard: in-range sentinel rule).
# Dropped: vaccine-uptake, side-effect, reason and asset items.
# Covariates: age, sex, respondent category.
# `id` = row index (the deposit's own id is not carried).

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0310437.s007"
RAW = os.environ.get("SOGBESAN2026_RAW")

ITEMS = ["covid_is_not_real", "covid_is_a_death_sentence", "covid_is_disease_of_elites",
         "no_covid_in_nigeria", "africans_are_immune_to_covid", "covid_affect_young_old",
         "covid_is_punishmnent", "covid_is_biological_weapon", "virus_designed_to_sell_drug",
         "covid_is_exaggerated", "covid_is_scam"]


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_sogbesan2026_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path)
    if not RAW:
        os.remove(path)
    return df


def convert():
    df = load()
    assert len(df) == 2602
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_age"] = df["res_age"]
    df["cov_sex"] = df["res_sex"]
    df["cov_respondent_category"] = df["res_category"].map(
        {"others": "community member", "caregivers_bringing_their_children_for_i": "caregiver",
         "healthcare_provider": "healthcare provider"})
    covs = ["cov_age", "cov_sex", "cov_respondent_category"]
    mapping = {c: f"perc_{k}" for k, c in enumerate(ITEMS, 1)}
    long = df[["id"] + covs + ITEMS].rename(columns=mapping).melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    assert set(long["resp"].dropna()) <= {"agree", "disagree", "don_t_know"}
    long["resp"] = long["resp"].map({"agree": 1, "disagree": 0})
    long = long[long["resp"].notna()].copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=[0, 1])
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    name = "sogbesan_2026_covid_perceptions"
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
