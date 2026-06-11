#!/usr/bin/env python3
# Source: https://plos.figshare.com/articles/dataset/31284877
# DOI (data): 10.1371/journal.pone.0340479.s002
# DOI (paper): 10.1371/journal.pone.0340479
# Learner perspective questionnaire on EFL oral English learning (Chinese students).
# N=154. Mix of Likert (1-3, 1-4) and binary multi-select (0/1) items.
# File structure: row 0 = question text labels (skip); rows 1-154 = data.
# Col 0=id, cols 1-4=metadata (skip), col 5=gender, col 6=grade, cols 7-42=items.

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
OUT_NAME = "yang2026_efl_learner_perspective"


def convert():
    r = requests.get("https://api.figshare.com/v2/articles/31284877/files",
                     headers=UA, timeout=30)
    files = r.json()
    rec = next(f for f in files if f["name"].lower().endswith((".xlsx", ".xls", ".csv")))
    r2 = requests.get(rec["download_url"], headers=UA, timeout=60, allow_redirects=True)

    if rec["name"].lower().endswith(".csv"):
        raw = pd.read_csv(io.BytesIO(r2.content), header=None)
    else:
        raw = pd.read_excel(io.BytesIO(r2.content), header=None)

    # The first row of the worksheet is a proper header row consumed differently across tools;
    # detect it: if col-0 of row 0 cannot be coerced to a number, it's a label row.
    try:
        pd.to_numeric(raw.iloc[0, 0])
        df = raw.copy()
    except (ValueError, TypeError):
        df = raw.iloc[1:].reset_index(drop=True)

    df = df.reset_index(drop=True)
    df.columns = range(len(df.columns))

    df["id"] = pd.to_numeric(df[0], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)

    df["cov_gender"] = pd.to_numeric(df[5], errors="coerce")
    df["cov_grade"]  = pd.to_numeric(df[6], errors="coerce")

    item_positions = list(range(7, 43))
    item_names = [f"item_{i - 6:02d}" for i in item_positions]

    for pos, name in zip(item_positions, item_names):
        df[name] = pd.to_numeric(df[pos], errors="coerce")

    long = df.melt(id_vars=["id", "cov_gender", "cov_grade"],
                   value_vars=item_names, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "cov_gender", "cov_grade"]]

    path = os.path.join(OUT_DIR, f"{OUT_NAME}.csv")
    long.to_csv(path, index=False)
    print(f"{OUT_NAME}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
