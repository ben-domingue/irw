#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0285293
# DOI: 10.1371/journal.pone.0285293
#
# Saputra DEE, Maulida Rahma V, Eliyana A, Pratama AS, Anggraini RD, Kamil
# NLM, et al. (2023) Do system quality and information quality affect job
# performance? The mediation role of users' perceptions. PLoS ONE 18(6):
# e0285293.
#
# S1 Dataset (XLSX, N=118) contains 5 Likert (3-5 observed range) scales
# identified by column prefix, all named/defined in the article: SQ
# (System Quality, 5 items), IQ (Information Quality, 5 items), PEOU
# (Perceived Ease of Use, 5 items), PU (Perceived Usefulness, 6 items), JP
# (Job Performance, 9 items). Shipped as 5 separate tables per the
# pipeline's one-scale-per-file convention.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0285293.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "saputra_2023_system_quality": [f"SQ{i}" for i in range(1, 6)],
    "saputra_2023_info_quality": [f"IQ{i}" for i in range(1, 6)],
    "saputra_2023_perceived_ease_of_use": [f"PEOU{i}" for i in range(1, 6)],
    "saputra_2023_perceived_usefulness": [f"PU{i}" for i in range(1, 7)],
    "saputra_2023_job_performance": [f"JP{i}" for i in range(1, 10)],
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content), sheet_name="Sheet1")


def build_long(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    d = df.rename(columns={"N": "id"})[["id"] + item_cols].copy()
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
    print("Fetching S1 Dataset (XLSX)...")
    raw = fetch_raw()
    for out_name, cols in SCALES.items():
        write_scale(build_long(raw, cols), f"{out_name}.csv")


if __name__ == "__main__":
    convert()
