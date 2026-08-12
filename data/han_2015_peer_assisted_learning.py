#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0142988
# DOI: 10.1371/journal.pone.0142988

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SI_URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0142988.s001"

ITEM_COLS = [f"B_{i}" for i in range(1, 13)]


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = "/tmp/han_2015.sav"
    with open(tmp, "wb") as f:
        f.write(r.content)
    df = pd.read_spss(tmp)

    df["id"] = df.index
    df["cov_group"] = df["group"].astype(str)
    df["cov_gender"] = df["gender"].astype(str)

    for c in ITEM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    keep = ["id", "cov_group", "cov_gender"] + ITEM_COLS
    df = df[keep]

    long = df.melt(id_vars=["id", "cov_group", "cov_gender"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]

    long = long[["id", "item", "resp", "cov_group", "cov_gender"]]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "han_2015_peer_assisted_learning.csv")
    long.to_csv(out_path, index=False)
    print(f"han_2015_peer_assisted_learning: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
