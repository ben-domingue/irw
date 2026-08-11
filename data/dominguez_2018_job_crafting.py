#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0197276
# DOI: 10.1371/journal.pone.0197276
# SI: S1 File (10.1371/journal.pone.0197276.s001), XLSX
#
# Sheet layout: row0 = scale name/response-scale text (merged),
# row1 = subscale label, row2 = column header ("Item N" / "Subtotal" /
# "Total ..."), data starts row3. Four scales in one file: Job Crafting
# Scale (JCS, 1-5), Work Engagement (UWES, 0-6), Maslach Burnout
# Inventory (MBI, 0-6), Intention To Leave (ITL, 1-5). Subtotal/total
# aggregate columns are excluded.

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0197276.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# (output name, list of column indices, valid_max)
SCALES = {
    "dominguez_2018_jcs": ([6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 19, 20, 21,
                             22, 23, 25, 26, 27, 28, 29], 5),
    "dominguez_2018_uwes": (list(range(32, 49)), 6),
    "dominguez_2018_mbi": (list(range(56, 78)), 6),
    "dominguez_2018_itl": ([85, 86, 87], 5),
}

COV_COLS = {
    1: "cov_age",
    2: "cov_institution",
    3: "cov_gender",
    4: "cov_institution_type",
    5: "cov_residency_level",
}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=120)
    r.raise_for_status()
    raw = pd.read_excel(io.BytesIO(r.content), sheet_name="Hoja1", header=None)
    data = raw.iloc[3:].reset_index(drop=True)
    data.columns = range(raw.shape[1])

    data = data.rename(columns=COV_COLS)
    data.insert(0, "id", range(1, len(data) + 1))
    cov_cols = list(COV_COLS.values())
    for c in cov_cols:
        data[c] = pd.to_numeric(data[c], errors="coerce")

    os.makedirs(OUT_DIR, exist_ok=True)
    for out_name, (item_cols, valid_max) in SCALES.items():
        item_cols = [c for c in item_cols]
        cols = ["id"] + cov_cols + item_cols
        sub = data[cols].copy()
        item_names = {c: f"item_{i+1}" for i, c in enumerate(item_cols)}
        sub = sub.rename(columns=item_names)
        item_col_names = list(item_names.values())

        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_col_names,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        # isolated data-entry error check: drop values outside documented scale
        long = long[(long["resp"] >= 0) & (long["resp"] <= valid_max)]
        long["resp"] = long["resp"].astype(int)

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"{out_name}.csv"
        long.to_csv(os.path.join(OUT_DIR, fname), index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
