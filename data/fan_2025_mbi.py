#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0324707
# DOI: 10.1371/journal.pone.0324707
#
# Fan Y, Zhang Y, Pu G, et al. (2025) The relationship between
# person-vocation fit and burnout among resident physicians: A
# single-center cross-sectional survey. PLoS ONE.
#
# S1 File (XLSX, N=636) contains raw 22-item Maslach Burnout Inventory
# (MBI) responses among resident physicians, split into its 3 standard
# subscales by column prefix: Ee (Emotional Exhaustion, 9 items), Pa
# (Personal Accomplishment, 8 items), Dp (Depersonalization, 5 items).
# 0-6 frequency scale. Shipped as 3 separate tables, one per subscale,
# per the pipeline's one-scale-per-file convention. (S1 Table is a
# regression-results summary table, not raw data -- not used.)

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0324707.s002"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

EE_ITEMS = [f"Ee{i}" for i in range(1, 10)]
PA_ITEMS = [f"Pa{i}" for i in range(1, 9)]
DP_ITEMS = [f"Dp{i}" for i in range(1, 6)]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content))


def build_long(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    d = df[item_cols].copy()
    d["id"] = d.index
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

    write_scale(build_long(raw, EE_ITEMS), "fan_2025_mbi_exhaustion.csv")
    write_scale(build_long(raw, PA_ITEMS), "fan_2025_mbi_accomplishment.csv")
    write_scale(build_long(raw, DP_ITEMS), "fan_2025_mbi_depersonalization.csv")


if __name__ == "__main__":
    convert()
