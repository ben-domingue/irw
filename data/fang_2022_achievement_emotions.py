#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/19546393
# DOI: 10.17608/k6.auckland.19546393.v1
# Achievement Emotions Questionnaire (AEQ) items for Chinese university students.
# Item codes: {valence}{activation}_{item}  e.g. PE1_h1 = Positive-Activating item 1
# All items 1-6. N=448.

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = ["Sex", "CKC", "Faculty", "Major"]


def convert():
    r = requests.get("https://api.figshare.com/v2/articles/19546393/files",
                     headers=UA, timeout=15)
    for f in r.json():
        if f["name"].endswith(".xlsx"):
            r2 = requests.get(f["download_url"], headers=UA, timeout=60)
            df = pd.read_excel(io.BytesIO(r2.content))
            break

    df = df.rename(columns={"ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)

    cov_present = [c for c in COV_COLS if c in df.columns]
    cov_rename = {c: f"cov_{c.lower()}" for c in cov_present}
    df = df.rename(columns=cov_rename)
    cov_out = list(cov_rename.values())

    item_cols = [c for c in df.columns if "_" in str(c) and c not in ["id"] + cov_out]

    long = df.melt(id_vars=["id"] + cov_out, value_vars=item_cols,
                   var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_out]

    path = os.path.join(OUT_DIR, "fang_2022_achievement_emotions.csv")
    long.to_csv(path, index=False)
    print(f"fang_2022_achievement_emotions: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
