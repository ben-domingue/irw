#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0351694
# DOI: 10.1371/journal.pone.0351694
# Paper: Parisien R, Drost A, Razi A, Ramtin S, Ring D, Janssen SJ (2026).
#   Musculoskeletal surgeons use mixed reasoning rather than pure Bayesian
#   strategies in clinical practice. PLoS One 21(6): e0351694.
# Data: PLOS Supporting Information S1 Dataset (journal.pone.0351694.s001,
#   "Deidentified dataset"), a semicolon-separated Qualtrics export: one
#   header row, then one row of question text, then 153 respondents (Science
#   of Variation Group surgeons).
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (rank 35; source
# leads/plos_leads_2026-10-30.csv), leads batch 1.
#
# ONE output table: parisien_2026_bayesian_reasoning -- 8 clinical
#   test-and-treat scenarios, scenario_1..scenario_8. Each offered four answer
#   options "ranked (1-4) based on adherence to Bayesian principles", "with
#   higher scores indicating more Bayesian reasoning"; the file stores the rank
#   of the option chosen, so resp is ordinal 1-4. The paper reports 142
#   surgeons answering at least one scenario and 124 answering all eight; the
#   eleven respondents who answered none contribute no rows.
# Dropped: SC0 (the Qualtrics total score) and Q2-Q6 (practice region, start
#   of independent practice, supervises trainees, specialty, sub-specialty):
#   the deposit gives them as bare codes with no value labels, and the paper's
#   Table 2 is an image, so the codes cannot be labelled.
# `id` is the deposit's ResponseId (1..153, unique, already a row number).
#
# Item text: NOT SHIPPED. The scenario stems are in the file's second header
#   row, but the four answer options (and which is ranked 1..4) are only in the
#   article's Table 1, an image, and Appendix 2.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0351694.s001&type=supplementary"
RAW = os.environ.get("PARISIEN_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SCEN = [f"Scenario {k}" for k in range(1, 9)]
DROPPED = ["Q2", "Q3", "Q4", "Q5", "Q6", "SC0"]


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=120)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_csv(src, sep=";", encoding="utf-8-sig", skiprows=[1])


def convert():
    df = load()
    assert list(df.columns) == ["ResponseId"] + DROPPED[:5] + SCEN + ["SC0"], list(df.columns)
    assert len(df) == 153 and df["ResponseId"].nunique() == 153
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and not txt
    df["id"] = df["ResponseId"].astype(int)
    long = df[["id"] + SCEN].melt(id_vars=["id"], var_name="item", value_name="resp")
    long["item"] = long["item"].str.replace("Scenario ", "scenario_", regex=False)
    long = long[long["resp"].notna()].copy()
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {1, 2, 3, 4}
    long = long[["id", "item", "resp"]]
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() == 142, long["id"].nunique()
    items = sorted(long["item"].unique())
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "parisien_2026_bayesian_reasoning.csv"), index=False)
    print(f"parisien_2026_bayesian_reasoning: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}; dropped {DROPPED}")


if __name__ == "__main__":
    convert()
