#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/26820745
# DOI: 10.6084/m9.figshare.26820745.v4
# Academic stress, psychological wellbeing, social support, and self-efficacy
# in university students. Each scale identified by column prefix.

import os
import io
import re
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = ["Gender", "Age", "University", "Year"]

# Map column prefix -> output name (only pure item columns, not subscale aggregates)
PREFIX_TO_NAME = {
    "AS":  "jeilani_2024_academic_stress",
    "PWB": "jeilani_2024_psychological_wellbeing",
    "SEF": "jeilani_2024_self_efficacy",
    "SS":  "jeilani_2024_social_support",
    "SSF": "jeilani_2024_social_support_family",
    "SO":  "jeilani_2024_social_outcomes",
    "SA":  "jeilani_2024_social_anxiety",
    "EM":  "jeilani_2024_emotional",
    "PG":  "jeilani_2024_personal_growth",
    "PRO": "jeilani_2024_proactivity",
    "PL":  "jeilani_2024_purpose_in_life",
    "BL":  "jeilani_2024_belonging",
}

# Exclude columns that are subscale aggregates (contain underscore suffix like _001, _002)
AGGREGATE_PATTERN = re.compile(r'_0\d{2}$')


def get_prefix(col):
    m = re.match(r'^([A-Z]+)', str(col))
    return m.group(1) if m else None


def convert():
    r = requests.get("https://api.figshare.com/v2/articles/26820745/files",
                     headers=UA, timeout=15)
    for f in r.json():
        if f["name"].endswith(".xlsx"):
            r2 = requests.get(f["download_url"], headers=UA, timeout=60)
            df = pd.read_excel(io.BytesIO(r2.content))
            break

    df = df.rename(columns={"ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)

    cov_present = [c for c in COV_COLS if c in df.columns]
    cov_rename = {c: f"cov_{c.lower()}" for c in cov_present}
    df = df.rename(columns=cov_rename)
    cov_out = list(cov_rename.values())

    # Group item columns by prefix, excluding aggregate suffixes
    scale_cols = {}
    for col in df.columns:
        if col in ["id"] + cov_out:
            continue
        if AGGREGATE_PATTERN.search(str(col)):
            continue
        pfx = get_prefix(col)
        if pfx and pfx in PREFIX_TO_NAME:
            scale_cols.setdefault(pfx, []).append(col)

    for pfx, cols in scale_cols.items():
        out_name = PREFIX_TO_NAME[pfx]
        long = df.melt(id_vars=["id"] + cov_out, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_out]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
