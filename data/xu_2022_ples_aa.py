#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0272214
# DOI: 10.1371/journal.pone.0272214
# SI: S1 Data (10.1371/journal.pone.0272214.s002), XLSX
#
# "Development and validation of a PLE scale from academic administrative
# perspective (PLES-AA) in tertiary education: A pilot study in China."
# 16-item, 4-point Likert scale (4 items each across Policy, Program
# Design, Curriculum/Instruction, and Capacity dimensions).
#
# Retriage flagged this as a possible longitudinal/test-retest dataset
# (dup_id_item, N=196, ratio~1.0x). On inspection this is NOT a repeated-
# measures design: the raw "Participant #" column has exactly one
# accidental duplicate (two distinct rows both labeled 175, presumably a
# numbering slip during data entry) among 197 single-wave survey
# responses -- there is no wave/timepoint column anywhere in the file,
# and the paper's Methods describe a single cross-sectional application
# survey, not test-retest. Per datastandard.md ("If existing IDs are
# non-numeric strings... use the row index instead" / id must be unique
# per person), the safe fix is to use the row index as id rather than
# trust the reused Participant # value.
#
# No imputation language found anywhere in the paper's full text.

import os
import io
import re
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0272214.s002&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Sheet1")

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    item_cols = [c for c in df.columns if re.match(r"^\d\.\d", str(c))]
    assert len(item_cols) == 16, f"expected 16 items, found {len(item_cols)}"
    item_names = {c: f"item_{c.split('：')[0].split(' ')[0]}" for c in item_cols}
    df = df.rename(columns=item_names)
    item_col_names = list(item_names.values())

    long = df[["id"] + item_col_names].melt(
        id_vars=["id"], value_vars=item_col_names,
        var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[long["resp"].between(1, 4)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    out_cols = ["id", "item", "resp"]
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "xu_2022_ples_aa.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
