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
# #2095: SEF6_001 and SEF9_001 are not aggregates -- they are two further
# administered self-efficacy items (n=663, all five levels 1-5) exported under
# duplicated names. Keep them. SSF2_001/SSF2_002 are the same pattern (#2426).
KEEP_SUFFIXED = {"SEF6_001", "SEF9_001", "SSF2_001", "SSF2_002"}

# #2426: the .xlsx support block is three MSPSS subscales of four items each,
# but its headers mislabel two of them. In file order the columns are
#   SSF1 SSF2_001 SSF3 SSF4 | SS1 SSF2 SSF2_002 SS4 | SO1 SO2 SO3 SO4
# and over the 663 rows they correlate in exactly those three quartets:
# within-quartet r 0.54-0.68 (family), 0.56-0.69 (friends), 0.69-0.74
# (significant other), cross-quartet 0.28-0.58. So SSF2_001 is the fourth
# family item and SSF2 / SSF2_002, despite the SSF prefix, are the friends
# items the SS1/SS4 table was missing. Both the column position and the
# correlations say so. Only SSF1 (MSPSS item 4, "I get the emotional help and
# support I need from my family", v1 .sav label) and SO1-SO4 carry wording;
# item codes stay the deposit's column names, so an SSF-prefixed code sits in
# the friends table on purpose. Earlier versions put SSF2 in the family table
# and dropped SSF2_001/SSF2_002 as "aggregates".
# jeilani_2024_social_outcomes is the MSPSS Significant Other subscale (its
# four .sav labels are "special person" items, MSPSS 10, 5, 1, 2); the name is
# kept because its item text is published under it.
ITEM_TABLE = {"SSF2": "jeilani_2024_social_support",
              "SSF2_002": "jeilani_2024_social_support"}


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
        if AGGREGATE_PATTERN.search(str(col)) and col not in KEEP_SUFFIXED:
            continue
        pfx = get_prefix(col)
        if pfx and pfx in PREFIX_TO_NAME:
            out_name = ITEM_TABLE.get(col, PREFIX_TO_NAME[pfx])
            scale_cols.setdefault(out_name, []).append(col)

    for out_name, cols in scale_cols.items():
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
