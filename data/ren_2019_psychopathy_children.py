#!/usr/bin/env python3
# Source: https://frontiersin.figshare.com/articles/dataset/11283215
# DOI: 10.3389/fpsyg.2019.02550.s001
# Download raw file: https://ndownloader.figshare.com/files/19972844
# Four psychopathy-related scales for Chinese children:
#   YPIC  (18 items, 1-4): Youth Psychopathic Inventory — Child version
#   CPTI  (28 items, 1-4): Callous-Unemotional and Psychopathic Traits Inventory
#   SDQ   (25 items, 1-3): Strengths and Difficulties Questionnaire
#   SCPV  (12 items, 1-5): Social Competence Scale, Parent Version (CPPRG 1995).
#         SCPV1 does not behave like the rest of the block: it is the only item
#         whose responses stay within 1-4, its median r with the other SCPV items
#         is 0.15 (theirs 0.32-0.54), and it tracks CPTI2 (r 0.77) and SDQ1 (0.70).
#         It ships, with a data note (irw#2425).
# Missing value codes: 999/99/9 used as sentinels — filtered per scale max.
#
# This script is the only builder of these tables. A second script,
# ren2019_psychopathy_children.py, built the same four tables as ren2019_*; those
# were exact duplicates and are retired (irw#2425). Its figshare download
# replaces this script's old local-xlsx read, so the build can be rerun anywhere.

import io
import os

import pandas as pd
import requests

BASE    = os.path.dirname(os.path.abspath(__file__))
RAW_URL = "https://ndownloader.figshare.com/files/19972844"
UA      = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
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
    os.makedirs(OUT_DIR, exist_ok=True)
    r = requests.get(RAW_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    df["id"] = df["id"].astype(int)

    cov_rename = {k: v for k, v in COV_COLS.items() if k in df.columns}
    df = df.rename(columns=cov_rename)
    cov_present = [v for v in COV_COLS.values() if v in df.columns]
    # 99/999 are missing-value codes in the covariates too (cov_income uses 99);
    # the live tables have carried them as missing since an earlier repair.
    for c in cov_present:
        df[c] = pd.to_numeric(df[c], errors="coerce").mask(lambda x: x.isin([99, 999])).astype("Int64")

    for prefix, valid_max, out_name in SCALES:
        item_cols = [c for c in df.columns if str(c).startswith(prefix)]
        if not item_cols:
            continue
        long = df.melt(id_vars=["id"] + cov_present, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[(long["resp"] >= 1) & (long["resp"] <= valid_max)]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_present]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
