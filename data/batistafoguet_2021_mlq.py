#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0254329
# DOI: 10.1371/journal.pone.0254329
# S1 Data (XLSX, Qualtrics export) -- Multifactor Leadership Questionnaire
# (MLQ-5X), 45 items rated 1-5, US online sample recruited via Prolific
# (PROLIFIC_PID). The paper's Catalan Police sample (S1/S2 File) is only
# documentation (DOCX), not a tabular dataset, so only the Prolific sample
# is processed here. Row 0 of the data block is a Qualtrics preview/test
# response (Prolific ID "rgrgrg", not a real participant) and is dropped.

import os
import io

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://doi.org/10.1371/journal.pone.0254329.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return io.BytesIO(r.content)


def convert():
    buf = fetch()
    # Row 0 = variable codes (header), row 1 = full question text label,
    # row 2+ = data. Read with header=0 and skip the label row.
    df = pd.read_excel(buf, sheet_name="Sheet0", header=0, skiprows=[1])

    item_cols = [f"Q{i}" for i in range(1, 46)]

    d = df[["PROLIFIC_PID"] + item_cols].copy()
    d = d.rename(columns={"PROLIFIC_PID": "id"})

    # Drop the Qualtrics preview/test row.
    d = d[d["id"].astype(str).str.len() > 10].reset_index(drop=True)
    d = d.dropna(subset=["id"]).reset_index(drop=True)

    assert d["id"].nunique() == len(d), "id not unique"

    long = d.melt(id_vars=["id"], value_vars=item_cols,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[long["resp"].between(1, 5)].reset_index(drop=True)

    out_cols = ["id", "item", "resp"]
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    out_dir_abs = os.path.abspath(OUT_DIR)
    os.makedirs(out_dir_abs, exist_ok=True)
    out_name = "batistafoguet_2021_mlq.csv"
    out_path = os.path.join(out_dir_abs, out_name)
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
