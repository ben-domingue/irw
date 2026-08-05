#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0320053
# DOI: 10.1371/journal.pone.0320053
#
# Thanh NH, Cong BT (2025) Unleashing the green potential: Unraveling the
# power of environmental concerns in driving employees' green behavior.
# PLoS ONE 20(3): e0320053.
#
# S1 File (XLSX, N=407, after exclusion of missing/outlier responses from
# 755 collected -- listwise deletion, not imputation) contains a survey
# with items on a 1-5 Likert scale, split into 5 named subscales by column
# prefix:
#   - ATT1-ATT5: Attitude (5 items)
#   - PBC1-PBC5: Perceived Behavioral Control (5 items)
#   - EGB1-EGB8: Employee Green Behavior (8 items)
#   - GK1-GK6:   Green Knowledge (6 items)
#   - EC1-EC6:   Environmental Concern (6 items)
# Each is a distinct construct -> one output file per subscale.

import os
import re

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0320053.s002"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "thanh_2025_attitude": re.compile(r"^ATT\d+$"),
    "thanh_2025_perceived_control": re.compile(r"^PBC\d+$"),
    "thanh_2025_green_behavior": re.compile(r"^EGB\d+$"),
    "thanh_2025_green_knowledge": re.compile(r"^GK\d+$"),
    "thanh_2025_environ_concern": re.compile(r"^EC\d+$"),
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content))


def build_long(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    d = df[["id"] + item_cols].copy()
    for c in item_cols:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    long = d.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    return long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    print("Fetching S1 File (XLSX)...")
    raw = fetch_raw()
    raw = raw.rename(columns={"ID": "id"})

    for name, pattern in SCALES.items():
        item_cols = [c for c in raw.columns if pattern.match(str(c))]
        long = build_long(raw, item_cols)
        write_scale(long, f"{name}.csv")


if __name__ == "__main__":
    convert()
