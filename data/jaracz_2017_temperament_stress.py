#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0176698
# DOI: 10.1371/journal.pone.0176698
#
# Jaracz M, Rosiak I, Bertrand-Bucińska A, et al. (2017) Affective
# temperament, job stress and professional burnout in nurses and civil
# servants. PLoS ONE.
#
# S1 Dataset (XLSX, N=258 rows) mixes two occupational groups (nurses,
# civil servants, "group" col = 1/2) plus a third block of 58 rows with all
# scale columns blank (no group label either) -- dropped as non-respondents.
# Two genuine multi-item raw scales found:
#   - Zmn8..Zmn116: TEMPS-A-style affective temperament items, binary 0/1
#     (109 items)
#   - stres_1, stres_2, stres3, stres4, stres_5, stres_6, stres_7, stres8:
#     8-item job stress scale, 0-5 scale (column names have inconsistent
#     underscores in the source file itself, renamed item1..item8 here)
# MBI_WE/MBI_DEP/MBI_ocena_wm/MBI_general columns are pre-computed
# composite/subscale scores, not raw items -- excluded per the
# no-composite-scores rule. TEMPS1 is a single lead-in item, excluded per
# the no-single-item-scale rule.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0176698.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

TEMPS_ITEMS = [f"Zmn{i}" for i in range(8, 117)]
STRESS_ITEMS = ["stres_1", "stres_2", "stres3", "stres4", "stres_5", "stres_6", "stres_7", "stres8"]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content))


def build_long(df: pd.DataFrame, item_cols: list[str], rename: dict | None = None) -> pd.DataFrame:
    d = df[item_cols].copy()
    d["id"] = d.index
    for c in item_cols:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    long = d.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    if rename:
        long["item"] = long["item"].map(rename)
    return long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    print("Fetching S1 Dataset (XLSX)...")
    raw = fetch_raw()

    temps = build_long(raw, TEMPS_ITEMS)

    stress_rename = {old: f"stress_item{i+1}" for i, old in enumerate(STRESS_ITEMS)}
    stress = build_long(raw, STRESS_ITEMS, rename=stress_rename)
    # only keep respondents with the full 8-item stress battery (drops the
    # 58 blank rows, which show up as NaN across every stres_* column)
    stress = stress[stress.groupby("id")["item"].transform("count") == len(STRESS_ITEMS)]

    write_scale(temps, "jaracz_2017_temperament.csv")
    write_scale(stress, "jaracz_2017_job_stress.csv")


if __name__ == "__main__":
    convert()
