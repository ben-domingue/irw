#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0217758
# DOI: 10.1371/journal.pone.0217758
#
# Luna-Cortes G, Lopez-Bonilla LM, Lopez-Bonilla JM (2019) The influence of
# social value and self-congruity on interpersonal connections in virtual
# social networks by Gen-Y tourists. PLoS ONE 14(6): e0217758.
#
# S1 File (XLSX, N=444 Spanish Gen-Y travelers) contains 6 short Likert
# (1-7) scales used in the paper's CFA/SEM, identified by column prefix:
# SATIS (satisfaction, 3 items), Self-Cong (self-congruity, 4 items),
# Social-Val (perceived social value, 3 items), ISNCC (4 items), IC
# (interpersonal connections, 4 items), ISNBI (3 items). ISNCC/ISNBI are
# not spelled out in the article text but are clearly distinct instruments
# by column-name prefix and are shipped using those source labels. Shipped
# as 6 separate tables per the pipeline's one-scale-per-file convention.
# A single ISNBI 3 = 32 value (all other responses 1-7) is a data-entry
# error and is dropped.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0217758.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "lunacortes_2019_satisfaction": ["SATIS 1", "SATIS 2", "SATIS 3"],
    "lunacortes_2019_self_congruity": ["Self-Cong1", "Self-Cong2", "Self-Cong3", "Self-Cong4"],
    "lunacortes_2019_social_value": ["Social-Val1", "Social-Val2", "Social-Val3"],
    "lunacortes_2019_isncc": ["ISNCC 1", "ISNCC 2", "ISNCC 3", "ISNCC 4"],
    "lunacortes_2019_interperson_conn": ["IC 1", "IC 2", "IC 3", "IC 4"],
    "lunacortes_2019_isnbi": ["ISNBI 1", "ISNBI 2", "ISNBI 3"],
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content), sheet_name="Hoja1")


def build_long(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    d = df.rename(columns={"Number": "id"})[["id"] + item_cols].copy()
    rename_map = {c: c.strip().lower().replace(" ", "_").replace("-", "_") for c in item_cols}
    d = d.rename(columns=rename_map)
    items = list(rename_map.values())
    for c in items:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    long = d.melt(id_vars=["id"], value_vars=items, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]  # drops isolated ISNBI 3 = 32 error
    return long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    print("Fetching S1 File (XLSX)...")
    raw = fetch_raw()
    for out_name, cols in SCALES.items():
        write_scale(build_long(raw, cols), f"{out_name}.csv")


if __name__ == "__main__":
    convert()
