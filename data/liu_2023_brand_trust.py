#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0295133
# DOI: 10.1371/journal.pone.0295133
#
# Liu Q, Wang X (2023) The impact of brand trust on consumers' behavior
# toward agricultural products' regional public brand. PLoS ONE.
#
# S1 Data (XLSX, N=544) contains a Theory-of-Planned-Behavior-style survey,
# all items on a 1-5 Likert scale, split into 6 named subscales by column
# prefix:
#   - BT1-BT4:   Brand Trust (4 items)
#   - ATT1-ATT3: Attitude (3 items)
#   - SN1-SN3:   Subjective Norm (3 items)
#   - PBC1-PBC3: Perceived Behavioral Control (3 items)
#   - PI1-PI3:   Purchase Intention (3 items)
#   - PB1-PB3:   Purchase Behavior (3 items)
# Each is a distinct construct -> one output file per subscale.

import os
import re

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0295133.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "liu_2023_brand_trust": re.compile(r"^BT\d+$"),
    "liu_2023_attitude": re.compile(r"^ATT\d+$"),
    "liu_2023_subjective_norm": re.compile(r"^SN\d+$"),
    "liu_2023_perceived_control": re.compile(r"^PBC\d+$"),
    "liu_2023_purchase_intention": re.compile(r"^PI\d+$"),
    "liu_2023_purchase_behavior": re.compile(r"^PB\d+$"),
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
    print("Fetching S1 Data (XLSX)...")
    raw = fetch_raw()
    raw = raw.rename(columns={"NO.": "id"})

    for name, pattern in SCALES.items():
        item_cols = [c for c in raw.columns if pattern.match(str(c))]
        long = build_long(raw, item_cols)
        write_scale(long, f"{name}.csv")


if __name__ == "__main__":
    convert()
