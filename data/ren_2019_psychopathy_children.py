#!/usr/bin/env python3
# Source: https://frontiersin.figshare.com/articles/dataset/11283215
# DOI: 10.3389/fpsyg.2019.02550.s001
# Download raw file: https://ndownloader.figshare.com/files/19972844
# Four psychopathy-related scales for Chinese children:
#   YPIC  (18 items, 1-4): Youth Psychopathic Inventory — Child version
#   CPTI  (28 items, 1-4): Callous-Unemotional and Psychopathic Traits Inventory
#   SDQ   (25 items, 1-3): Strengths and Difficulties Questionnaire
#   SCPV  (12 items, 1-5): Self-reported Child Psychopathy Version
# Missing value codes: 999/99/9 used as sentinels — filtered per scale max.

import os
import pandas as pd

BASE    = os.path.dirname(os.path.abspath(__file__))
RAW     = os.path.join(BASE, "Data_Sheet_1_Factor Structure and Measurement Invariance of Youth "
                             "Psychopathic Traits Inventory-Child Version in Chinese Children.xlsx")
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output", "cleaned")

COV_COLS = {"gender": "cov_gender", "age": "cov_age",
            "EDUCATION": "cov_education", "INCOME": "cov_income"}

# (scale_prefix, valid_max, output_name)
SCALES = [
    ("YPIC",  4,  "ren_2019_ypic"),
    ("CPTI",  4,  "ren_2019_cpti"),
    ("SDQ",   3,  "ren_2019_sdq"),
    ("SCPV",  5,  "ren_2019_scpv"),
]


def convert():
    df = pd.read_excel(RAW)
    df = df.rename(columns={"ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    df["id"] = df["id"].astype(int)

    cov_rename = {k: v for k, v in COV_COLS.items() if k in df.columns}
    df = df.rename(columns=cov_rename)
    cov_present = [v for v in COV_COLS.values() if v in df.columns]

    for prefix, valid_max, out_name in SCALES:
        item_cols = [c for c in df.columns if str(c).startswith(prefix)]
        if not item_cols:
            continue
        long = df.melt(id_vars=["id"] + cov_present, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[(long["resp"] >= 1) & (long["resp"] <= valid_max)]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_present]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
