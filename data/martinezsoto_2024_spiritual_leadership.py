#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0299671
# DOI: 10.1371/journal.pone.0299671
#
# Martinez-Soto L, Ontiveros Ramirez F, Toro Jaramillo ID, Moreno-Leyva NR
# (2024) Revisiting Louis Fry's spiritual leadership model in confessional
# school teachers using structural equation modeling (SEM). PLoS ONE 19(9):
# e0299671.
#
# S1 Data (XLSX, N=299 Colombian Adventist-school teachers) contains a
# 5-point Likert ("Completamente en desacuerdo".."Completamente de
# acuerdo") item block p1..p26 with a parallel numeric-recoded version
# p1_re..p26_re. Verified the two are a consistent forward 1-5 mapping
# (no direction reversal), so p_re columns are used directly as resp.
# The paper's Methods text explicitly describes only a 21-item Spiritual
# Leadership (SL) scale (5 subscales: vision 4, hope/faith 4, altruistic
# love 5, vocation 4, membership 4), but the raw file has 26 p-items in
# the identical response format with no separating marker; items 22-26
# could not be confirmed against the text as SL items or a distinct
# instrument, so all 26 are shipped together as one table (flagged in
# notes). PII (email address) and timestamp columns dropped; demographic
# covariates (Genero/Edad/etc.) omitted (categorical, not essential to
# the item scale).

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0299671.s004"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"p{i}_re" for i in range(1, 27)]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content), sheet_name="bd_base_3")


def convert():
    print("Fetching S1 Data (XLSX)...")
    raw = fetch_raw()
    d = raw.rename(columns={"nro": "id"})[["id"] + ITEM_COLS].copy()
    rename_map = {c: c.replace("_re", "") for c in ITEM_COLS}
    d = d.rename(columns=rename_map)
    items = list(rename_map.values())
    for c in items:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    long = d.melt(id_vars=["id"], value_vars=items, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "martinezsoto_2024_spiritual_leadership.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
