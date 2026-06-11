#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/32090683
# DOI: 10.6084/m9.figshare.32090683.v1
# Download raw file: https://ndownloader.figshare.com/files/63988402 -> Raw dade.xlsx

import os
import re
import pandas as pd

BASE    = os.path.dirname(os.path.abspath(__file__))
RAW     = os.path.join(BASE, "Raw dade.xlsx")
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output", "cleaned")

SCALES = {
    "che_2026_social_support":          re.compile(r"^SS item\d+$"),
    "che_2026_upward_social_identity":  re.compile(r"^USI item\d+$"),
    "che_2026_upward_social_comparison":re.compile(r"^USC item\d+$"),
    "che_2026_regulatory_self_efficacy":re.compile(r"^RES item\d+$"),
    "che_2026_social_wellbeing":        re.compile(r"^SW item\d+$"),
}


def convert():
    df = pd.read_excel(RAW)
    df = df.rename(columns={"Participants ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    df["id"] = df["id"].astype(int)

    for out_name, pattern in SCALES.items():
        item_cols = [c for c in df.columns if pattern.match(str(c))]
        if not item_cols:
            print(f"  no columns matched for {out_name}")
            continue
        long = df.melt(id_vars=["id"], value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"]]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
