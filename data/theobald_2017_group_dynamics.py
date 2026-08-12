#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0181336
# DOI: 10.1371/journal.pone.0181336

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SI_URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0181336.s001"

ITEM_COLS = ["Comfort", "Dominator"]


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = "/tmp/theobald_2017.csv"
    with open(tmp, "wb") as f:
        f.write(r.content)
    df = pd.read_csv(tmp)

    df["id"] = df["StudentID"]
    df["wave"] = df.groupby("StudentID").cumcount() + 1
    df["cov_gender"] = df["Gender"].astype(str)
    df["cov_ethnicity"] = df["Ethnicity"].astype(str)
    df["cov_topic"] = df["Topic"].astype(str)

    for c in ITEM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    keep = ["id", "wave", "cov_gender", "cov_ethnicity", "cov_topic"] + ITEM_COLS
    df = df[keep]

    long = df.melt(id_vars=["id", "wave", "cov_gender", "cov_ethnicity", "cov_topic"],
                    value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 6)]

    long = long[["id", "item", "resp", "wave", "cov_gender", "cov_ethnicity", "cov_topic"]]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "theobald_2017_group_dynamics.csv")
    long.to_csv(out_path, index=False)
    print(f"theobald_2017_group_dynamics: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
