#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243193
# DOI: 10.1371/journal.pone.0243193
# Paper: Reiss S, Franchina V, Jutzi C, Willardt R, Jonas E (2020). From
#   anxiety to action -- Experience of threat, emotional states, reactance, and
#   action preferences in the early days of COVID-19 self-isolation in Germany
#   and Austria. PLoS ONE 15(12): e0243193.
# Data: PLOS SI S4 (journal.pone.0243193.s004, LimeSurvey CSV export, = the
#   S1_Data.csv inside S1's zip), 404 adults, online, 20-26 March 2020.
# License: CC BY 4.0 (the article and its SI).
# Codebook: S2 File (German item wording, by block) and the authors' R
#   analysis script in S1 (sex and education codes).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# FIVE output tables (items keep the survey's codes):
#   reiss_2020_discrepancy   15 items (aut/uncer/agenc motivational-affective,
#     expec epistemic), 1-5, raw (reverse-worded items not recoded).
#   reiss_2020_affect        34 state-affect adjectives, 1-5 (the paper's
#     "34 items judged on a 5-point scale"): reactance 7, PANAS-X fear 3,
#     hostility 6, sadness 5, BIS 5, BAS high activation 5, BAS deactivated
#     relaxation 3; item prefixes name the block.
#   reiss_2020_system_justification  8 items, 1-7, raw.
#   reiss_2020_loneliness    15 items (social/family/romantic, SELSA-S), 1-7,
#     raw (the paper reverse-codes some for its score; not recoded here).
#   reiss_2020_covid_knowledge  10 true/false statements, scored 1 correct /
#     0 incorrect, `resp_raw` = Y/N as answered. Key: 4, 5, 7 true, the rest
#     false; with "unsure" counted wrong this reproduces the paper's 78%
#     correct (78.2%). "U" (unsure) is a non-response here and is dropped.
# HELD (not written by default; `--held` writes them to
#   automated_finding/runs/held/): the three action-rating tables (13 actions
#   rated sensible / intended / helps feel better). The paper says "scaled
#   1-7"; the deposit holds 1-5 only.
# Dropped: zip code (2-digit area, geography), the free-text pre-existing
#   condition and "other action" answers, referrer URL, LimeSurvey seed and
#   timestamps, the infection-count guess (open number), education (the
#   authors' own recode is ambiguous for "other").
# Covariates: age, sex (G1 male, G2 female, G3 diverse, G4 undisclosed, from
#   the authors' script), country of residence (DE/AT/other), self-rated risk
#   group (0/1), household size.
# `id` = the LimeSurvey response id (unique).
#
# Item text: NOT SHIPPED. German wording for every block is in S2 File (CC
#   BY); the discrepancy, affect (PANAS-X, BIS/BAS), system-justification
#   (Kay & Jost) and loneliness (SELSA-S) items are adaptations or
#   translations of published scales -- check the register first.

import os
import re
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
HELD_DIR = os.path.join(REPO_ROOT, "automated_finding", "runs", "held")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0243193.s004"
RAW = os.environ.get("REISS2020_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}

KEY_TRUE = {4, 5, 7}


def load():
    if RAW:
        return pd.read_csv(RAW)
    r = requests.get(URL, headers=HDR, timeout=180)
    r.raise_for_status()
    from io import StringIO
    return pd.read_csv(StringIO(r.content.decode("utf-8")))


def save(long, covs, name, values, out_dir=OUT_DIR, raw=False):
    cols = ["id", "item", "resp"] + (["resp_raw"] if raw else []) + covs
    long = long[cols].sort_values(["id", "item"])
    assert set(long["resp"]) <= set(values)
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    if out_dir != OUT_DIR:
        out_dir = os.path.join(out_dir, name)
    os.makedirs(out_dir, exist_ok=True)
    long.to_csv(os.path.join(out_dir, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def block(df, covs, prefix):
    cols = [c for c in df.columns if c.startswith(prefix + "[")]
    long = df[["id"] + covs + cols].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long["item"] = long["item"].str.extract(r"\[(.+)\]", expand=False)
    long = long[long["resp"].notna()].copy()
    long["resp"] = long["resp"].astype(int)
    return long, cols


def convert(held=False):
    df = load()
    assert len(df) == 404 and df["id"].is_unique
    df["cov_age"] = df["age"]
    df["cov_sex"] = df["sex"].map({"G1": "male", "G2": "female", "G3": "diverse", "G4": "undisclosed"})
    df["cov_country"] = df["country"].map({"DE": "Germany", "AT": "Austria", "-oth-": "other"})
    df["cov_risk_group"] = df["risk"]
    df["cov_household_size"] = df["hhpers"]
    covs = ["cov_age", "cov_sex", "cov_country", "cov_risk_group", "cov_household_size"]
    assert df[covs].notna().all().all()

    for prefix, name, values, n in [
        ("discr", "reiss_2020_discrepancy", range(1, 6), 15),
        ("Affekt", "reiss_2020_affect", range(1, 6), 34),
        ("System", "reiss_2020_system_justification", range(1, 8), 8),
        ("lonel", "reiss_2020_loneliness", range(1, 8), 15),
    ]:
        long, cols = block(df, covs, prefix)
        assert len(cols) == n, (prefix, len(cols))
        save(long, covs, name, values)

    wis = [c for c in df.columns if c.startswith("wissen[")]
    assert len(wis) == 10
    long = df[["id"] + covs + wis].melt(id_vars=["id"] + covs, var_name="item", value_name="resp_raw")
    long["item"] = long["item"].str.extract(r"\[(.+)\]", expand=False)
    long = long[long["resp_raw"].isin(["Y", "N"])].copy()
    num = long["item"].str[3:].astype(int)
    truth = num.isin(KEY_TRUE).map({True: "Y", False: "N"})
    long["resp"] = (long["resp_raw"] == truth).astype(int)
    save(long, covs, "reiss_2020_covid_knowledge", [0, 1], raw=True)

    if held:
        for prefix, name in [("sinnv", "reiss_2020_action_sensible"),
                             ("handlint", "reiss_2020_action_intention"),
                             ("coping", "reiss_2020_action_feel_better")]:
            long, cols = block(df, covs, prefix)
            assert len(cols) == 13
            save(long, covs, name, range(1, 6), out_dir=HELD_DIR)


if __name__ == "__main__":
    convert(held="--held" in sys.argv)
