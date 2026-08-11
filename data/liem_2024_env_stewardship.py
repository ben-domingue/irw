#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0306616
# DOI: 10.1371/journal.pone.0306616
#
# "Customer pressure and environmental stewardship: The moderator role of
# perceived benefit by managers" (PLOS ONE, 2024). S1 Data (CSV) contains
# raw item-level Likert responses (1-5) from 234 CEOs/managers of Vietnamese
# manufacturing enterprises across seven distinct measurement scales.
# Each scale is written as its own IRW file per the "one file per scale" rule.

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
