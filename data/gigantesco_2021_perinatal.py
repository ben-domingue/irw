#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0260596
# DOI: 10.1371/journal.pone.0260596
# Paper: Gigantesco, A., Palumbo, G., Cena, L., Camoni, L., Trainini, A.,
#   Stefana, A., & Mirabella, F. (2021). The limited screening accuracy of the
#   Patient Health Questionnaire-2 in detecting depression among perinatal
#   women in Italy. PLOS ONE 16(11): e0260596.
# Data: journal.pone.0260596.s001 (S1 Raw data, .xlsx), 1,155 consecutive
#   perinatal women attending eleven primary or secondary health care centres
#   in Italy (954 in the third trimester of pregnancy, 201 in the first
#   trimester postpartum).
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# TWO output tables:
#   gigantesco_2021_phq9  PHQ1..PHQ9, 0-3 (Italian PHQ-9). The deposit's
#                         PHQ_9_Totale reproduces from the items on 99.8% of
#                         rows; PHQ_2_Totale = PHQ1 + PHQ2 on 100%.
#   gigantesco_2021_epds  EPDS1..EPDS10, 0-3 (Italian Edinburgh Postnatal
#                         Depression Scale), items already scored (reverse-
#                         keyed items carry their scored value). The deposit's
#                         EPDS_Totale reproduces on 96% of complete rows; the
#                         other 47 rows differ by 1-3 points in both
#                         directions, so the item and total columns disagree
#                         somewhere in entry. Items are shipped as deposited.
#                         ONE cell, EPDS6 = 4 on row 564, is outside the 0-3
#                         scale (every other EPDS6 cell is 0-3) and is dropped
#                         as a data-entry error.
# The literal string "MISSING" marks missing responses (PHQ4, PHQ7 and five
# EPDS items); those cells are dropped.
#
# Covariate: cov_perinatal_stage (third trimester of pregnancy / first
# trimester postpartum), from the two mutually exclusive 0/1 flags. Maternal
# age, education, working, economic and marital status are 1-3 codes whose
# categories are given only in the article's Table 1 image; dropped.
# Children_living_pregnancy_or_birth is dropped likewise. Totals and
# screening-cutoff flags are derived and not shipped.
#
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. Column names only; no stems or codebook in the
#   deposit. PHQ-9 is registered `ship` but the Italian wording administered
#   is not here; EPDS is registered `hold`.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("GIGANTESCO_RAW", "journal.pone.0260596.s001.xlsx")
N_ROWS = 1155

BLOCKS = {
    "gigantesco_2021_phq9": [f"PHQ{i}" for i in range(1, 10)],
    "gigantesco_2021_epds": [f"EPDS{i}" for i in range(1, 11)],
}


def convert():
    df = pd.read_excel(RAW).copy()
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text/mixed columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 33
    for c in txt:   # every text cell is a number or the literal MISSING
        vals = set(df[c].astype(str))
        assert all(v == "MISSING" or v.lstrip("-").isdigit() for v in vals), (c, vals)

    items = BLOCKS["gigantesco_2021_phq9"] + BLOCKS["gigantesco_2021_epds"]
    for c in items:
        df[c] = pd.to_numeric(df[c].replace("MISSING", None))
    bad = df["EPDS6"] == 4
    assert int(bad.sum()) == 1 and df.index[bad][0] == 563
    df.loc[bad, "EPDS6"] = None
    phq_total = pd.to_numeric(df["PHQ_9_Totale"].replace("MISSING", None))
    assert (df[BLOCKS["gigantesco_2021_phq9"]].sum(axis=1) == phq_total).mean() > 0.995
    assert ((df["PHQ1"] + df["PHQ2"]) == df["PHQ_2_Totale"]).all()

    p, q = df["Being_in_the_third_trimester_pregnacy"], df["Being_in_the_first_trimester_postpartum"]
    assert ((p + q) == 1).all()
    df["id"] = range(1, N_ROWS + 1)
    df["cov_perinatal_stage"] = p.map({1: "third trimester of pregnancy", 0: "first trimester postpartum"})
    cov_cols = ["cov_perinatal_stage"]

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, cols in BLOCKS.items():
        long = df[["id"] + cov_cols + cols].melt(id_vars=["id"] + cov_cols, var_name="item",
                                                 value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) == {0, 1, 2, 3}, name
        long = long[["id", "item", "resp"] + cov_cols]
        assert not long.duplicated(["id", "item"]).any() and long["item"].nunique() == len(cols)
        checks = run_qc(long, permitted_values={c: [0, 1, 2, 3] for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={len(cols)}")

    dropped = [c for c in df.columns if c not in set(items) | {"id", "cov_perinatal_stage"}]
    print(f"dropped {len(dropped)}: {dropped}")
    assert len(dropped) == 33 - 19
    print(f"TOTAL responses: {total}")


if __name__ == "__main__":
    convert()
