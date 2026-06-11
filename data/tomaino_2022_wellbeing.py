#!/usr/bin/env python3
# Source: https://osf.io/zypjv/
# DOI: none (OSF project)
# Blended group intervention study; Italian university students.
# 6 scales: ULS-6 (loneliness), MSPSS (social support), GAD-7 (anxiety),
#           PHQ-9 (depression), SWL (life satisfaction), MLQ (meaning in life)

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "tomaino_2022_loneliness":        [f"ULS-6_{i}" for i in range(1, 7)],
    "tomaino_2022_social_support":    [f"MSPSS_{i}" for i in range(1, 13)],
    "tomaino_2022_anxiety":           [f"GAD-7_{i}" for i in range(1, 9)],
    "tomaino_2022_depression":        [f"PHQ-9_{i}" for i in range(1, 11)],
    "tomaino_2022_life_satisfaction": [f"SWL_{i}" for i in range(1, 6)],
    "tomaino_2022_meaning_in_life":   [f"MLQ_{i}" for i in range(1, 11)],
}

COV_MAP = {
    "participant ": "id",
    "gender": "cov_gender",
    "age": "cov_age",
    "group": "cov_group",
    "nationality": "cov_nationality",
}


def convert():
    r = requests.get("https://api.osf.io/v2/nodes/zypjv/files/osfstorage/",
                     headers=UA, timeout=30)
    for f in r.json().get("data", []):
        if f["attributes"]["name"].endswith(".xlsx"):
            r2 = requests.get(f["links"]["download"], headers=UA, timeout=60)
            df = pd.read_excel(io.BytesIO(r2.content))
            break

    df = df.rename(columns={k: v for k, v in COV_MAP.items() if k in df.columns})
    # IDs are text like '1b', '2b' — use row index instead
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

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
        # MSPSS is scored 1-7; a single 0 is a data entry error → treat as NA
        if out_name == "tomaino_2022_social_support":
            long.loc[long["resp"] == 0, "resp"] = float("nan")
            long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
