#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0262665
# DOI: 10.1371/journal.pone.0262665
#
# Direkvand-Moghadam et al. (2022) "Development and psychometric properties
# of Iranian midwives job satisfaction instrument (MJSI): A sequential
# exploratory study." PLOS ONE. License: CC BY 4.0.
#
# S2 File ("A minimal set of data for the study", SAV, N=121 midwives) has
# raw item-level responses for the final 25-item MJSI, 5-point Likert scale,
# across five factors identified by column prefix (matches the paper's
# stated factor structure exactly): R (responsibility, 2 items), C/c
# (communication, 7 items), pr (professional, 10 items), p (physical-mental,
# 4 items), s (social, 2 items).

import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0262665.s002"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["R1", "R2", "C1", "C2", "C3", "C4", "c5", "c6", "c7",
             "pr1", "pr2", "pr3", "pr4", "pr5", "pr6", "pr7", "pr8", "pr9", "pr10",
             "p1", "p2", "p3", "p4", "s1", "s2"]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = "/tmp/_direkvand_2022.sav"
    with open(tmp, "wb") as f:
        f.write(r.content)
    df, _meta = pyreadstat.read_sav(tmp)
    return df


def convert():
    print("Fetching S2 File (SAV)...")
    raw = fetch_raw()
    df = raw.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    for c in ITEM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "direkvand_2022_mjsi.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
