#!/usr/bin/env python3
# Source: https://osf.io/3adcj/
# Psychometric validation of a simplified 9-item ERQ (ERQ-CA-9) in Mexican adults.
# Also includes GAD-2 (gad1-gad2) and PHQ-2 (phq1-phq2) screeners.
# Language: Spanish; N≈397.

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "Folio": "id",
    "edad": "cov_age",
    "sexo": "cov_sex",
    "genero": "cov_gender",
    "lgtb": "cov_lgtb",
    "estado": "cov_state",
    "suic": "cov_suicidality",
    "estudios": "cov_education",
}

SCALES = {
    "valencia_2023_erq":  [f"erq{i}" for i in range(1, 11)],
    "valencia_2023_gad2": ["gad1", "gad2"],
    "valencia_2023_phq2": ["phq1", "phq2"],
}


def convert():
    r = requests.get("https://api.osf.io/v2/nodes/3adcj/files/osfstorage/",
                     headers=UA, timeout=30)
    dl_url = None
    for f in r.json().get("data", []):
        if "Data.csv" in f["attributes"]["name"]:
            dl_url = f["links"]["download"]
            break
    r2 = requests.get(dl_url, headers=UA, timeout=60)
    df = pd.read_csv(io.StringIO(r2.text))

    df = df.rename(columns={k: v for k, v in COV_MAP.items() if k in df.columns})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)

    cov_cols = [v for v in COV_MAP.values() if v != "id" and v in df.columns]

    for out_name, item_cols in SCALES.items():
        present = [c for c in item_cols if c in df.columns]
        if not present:
            print(f"SKIP {out_name}: no columns found")
            continue
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=present,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
