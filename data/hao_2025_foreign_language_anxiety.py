#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/30397234
# DOI: 10.6084/m9.figshare.30397234.v1
# Academic resilience + foreign language anxiety + self-efficacy in Chinese students.
# ER1-4: Emotional Regulation resilience (4 items, 1-5)
# MR1-7: Metacognitive Regulation resilience (7 items, 1-5)
# SR1-8: Social Regulation resilience (8 items, 1-5)
# SE1-6: Self-Efficacy (6 items, 1-5)
# AT1-8: Foreign Language Anxiety (8 items incl. 2 reverse-scored; 1-5)

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "hao_2025_emotional_regulation":     [f"ER{i}" for i in range(1, 5)],
    "hao_2025_metacognitive_regulation": [f"MR{i}" for i in range(1, 8)],
    "hao_2025_social_regulation":        [f"SR{i}" for i in range(1, 9)],
    "hao_2025_self_efficacy":            [f"SE{i}" for i in range(1, 7)],
    "hao_2025_foreign_language_anxiety": None,  # AT columns — handled below
}

COV_MAP = {"NAME": "id", "SEX": "cov_sex", "AGE": "cov_age", "REG": "cov_region"}


def convert():
    r = requests.get("https://api.figshare.com/v2/articles/30397234/files",
                     headers=UA, timeout=15)
    for f in r.json():
        if f["name"].endswith(".xlsx"):
            r2 = requests.get(f["download_url"], headers=UA, timeout=60)
            df = pd.read_excel(io.BytesIO(r2.content))
            break

    df = df.rename(columns={k: v for k, v in COV_MAP.items() if k in df.columns})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)

    cov_cols = [v for v in COV_MAP.values() if v != "id" and v in df.columns]

    # AT cols: any col starting with AT (includes reverse-scored AT4反, AT5反)
    at_cols = [c for c in df.columns if str(c).startswith("AT")]
    SCALES["hao_2025_foreign_language_anxiety"] = at_cols

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
