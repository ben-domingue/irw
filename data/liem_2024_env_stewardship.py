#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0306616
# DOI: 10.1371/journal.pone.0306616
#
# "Customer pressure and environmental stewardship: The moderator role of
# perceived benefit by managers" (PLOS ONE, 2024). S1 Data (CSV) contains
# raw item-level Likert responses (1-5) from 234 CEOs/managers of Vietnamese
# manufacturing enterprises across seven distinct measurement scales.
# Each scale is written as its own IRW file per the "one file per scale" rule.
#
# NOTE (liem_2024_attitude_env): the seven even-numbered items ATE2, ATE4,
# ATE6, ATE8, ATE10, ATE12 and ATE14 are STORED REVERSE-SCORED in the deposit
# (S1 Data), so for them resp runs in the pro-ecological direction, not as
# agreement with the printed statement. The scale is Dunlap et al.'s (2000)
# revised NEP, whose even items are anti-ecological (e.g. ATE12 "Humans were
# designed to dominate the remainder of nature"), yet every item behaves alike:
# all 105 inter-item correlations are +0.35 to +0.86, item-rest correlations
# are all >= +0.67 (alpha 0.949, as the paper's Table 2 reports, with positive
# loadings for all 15), and the pattern holds after removing careless
# responders. The paper never says "reverse". So resp = 5 on ATE12 means strong
# DISagreement with human dominance. This script does no recoding; values are
# as deposited and are not changed here (irw#2118).

import os
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "automated_finding", "raw_downloads",
                    "liem_2024_pone0306616_s1data.csv")

# Scale prefix -> (output name, item column list)
SCALES = {
    "liem_2024_customer_pressure": ["CuP1", "CuP2", "CuP3", "CuP4"],
    "liem_2024_env_mgmt_acct": ["EMA1", "EMA2", "EMA3", "EMA4", "EMA5", "EMA6"],
    "liem_2024_attitude_env": [f"ATE{i}" for i in range(1, 16)],
    "liem_2024_green_competitive_adv": ["GCA1", "GCA2", "GCA3", "GCA4"],
    "liem_2024_perceived_benefit_ema": ["PB_EMA1", "PB_EMA2", "PB_EMA3", "PB_EMA4"],
    "liem_2024_cleaner_production": ["CP1", "CP2", "CP3", "CP4", "CP5"],
    "liem_2024_perceived_benefit_cp": [f"PB_CP{i}" for i in range(1, 10)],
}


def convert():
    df = pd.read_csv(SRC)
    df = df.rename(columns={"STT": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id column is not unique per respondent"

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]
        long = long[["id", "item", "resp"]]

        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
