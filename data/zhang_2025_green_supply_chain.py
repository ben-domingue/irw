#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0322200
# DOI: 10.1371/journal.pone.0322200
#
# Zhang B, Zhao S, Shao D, Fan X, Wang S (2025) Institutional pressures and
# green supply chain integration intention: Evidence from Chinese
# manufacturing firms. PLoS One 20(5): e0322200.
#
# S1 Data (XLSX, N=292; caption says "Regression data" but contains raw
# item-level 1-7 Likert responses, not composite scores) has 5 named
# subscales by column prefix:
#   - CP1-CP4:      Coercive Pressure (4 items)
#   - NP1-NP4:      Normative Pressure (4 items)
#   - EA1-EA5:      Executives' Environmental Awareness (5 items)
#   - SE1-SE5:      Executives' Self-Efficacy (5 items)
#   - GSCII1-GSCII5: Green Supply Chain Integration Intention (5 items)
# Excluded firm-level covariates (age, size, ownership, industry) -- not
# item responses.

import os
import re

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0322200.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "zhang_2025_coercive_pressure": re.compile(r"^CP\d+$"),
    "zhang_2025_normative_pressure": re.compile(r"^NP\d+$"),
    "zhang_2025_environ_awareness": re.compile(r"^EA\d+$"),
    "zhang_2025_self_efficacy": re.compile(r"^SE\d+$"),
    "zhang_2025_green_supply_intent": re.compile(r"^GSCII\d+$"),
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

    for name, pattern in SCALES.items():
        item_cols = [c for c in raw.columns if pattern.match(str(c))]
        long = build_long(raw, item_cols)
        write_scale(long, f"{name}.csv")


if __name__ == "__main__":
    convert()
