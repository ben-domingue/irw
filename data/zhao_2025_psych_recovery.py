#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0325755
# DOI: 10.1371/journal.pone.0325755
#
# Zhao K, Zhang S, Zhao F (2025) How the natural environment affects
# psychological recovery: A case study in Changsha, China. PLoS ONE 20(6):
# e0325755.
#
# S1 Dataset (XLSX, N=199 respondents from urban forest parks in Changsha)
# contains 5 Likert (1-5) scales identified by column prefix: NEP (Natural
# Environment Perception, 6 items), LI (Leisure Involvement, 12 items), PA
# (Place Attachment, 8 items), REP (Restorative Environment Perception, 12
# items), PRE (Psychological Recovery Evaluation, 12 items) -- all named
# and defined in the article abstract. Shipped as 5 separate tables per
# the pipeline's one-scale-per-file convention. Demographic columns
# (gender/age/education/income/occupation) omitted.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0325755.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "zhao_2025_nat_env_perception": [f"NEP{i}" for i in range(1, 7)],
    "zhao_2025_leisure_involvement": [f"LI{i}" for i in range(1, 13)],
    "zhao_2025_place_attachment": [f"PA{i}" for i in range(1, 9)],
    "zhao_2025_restor_env_perception": [f"REP{i}" for i in range(1, 13)],
    "zhao_2025_psych_recovery_eval": [f"PRE{i}" for i in range(1, 13)],
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content), sheet_name="Sheet1")


def build_long(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    d = df.rename(columns={"1.number": "id"})[["id"] + item_cols].copy()
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
