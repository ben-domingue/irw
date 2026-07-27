#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0146050
# DOI: 10.1371/journal.pone.0146050
# Supporting Information: https://doi.org/10.1371/journal.pone.0146050.s001 (Study 1),
#                          https://doi.org/10.1371/journal.pone.0146050.s003 (Study 3)
#
# Study 1 (N=104, English): Power scale (8i), Authenticity Scale (Wood et
# al.) 3 subscales -- authentic living (4i), accepting external influence
# (4i), self-alienation (4i) -- Rosenberg Self-Esteem (10i), relationship
# satisfaction (7i). All numeric 1-5.
# Study 3 (N=210, Chinese): Rosenberg (10i), social desirability (5i),
# power (8i), authenticity (12i, combined). Exported as 5-point Chinese
# agree/disagree text for se/p/a (mapped after confirming the 3 scales
# share one identical 5-category set); social desirability items are
# binary but partially SPSS-label-corrupted (each item shows only {0.0,
# "非常不符合"} instead of a clean binary pair) -- treated as 0/1 by
# relative state (only two values exist per item), same pattern as
# gomez_2020_mpq's corrupted MPQ labels.
#
# No shared id/format between studies (different item sets, different
# languages), so kept as fully separate tables -- not melted together or
# treated as replication waves of the same instrument. Study 2 (S2, ambig
# uous Q3_1-21/po item blocks with no codebook match) intentionally
# skipped. Power/authenticity/relationship_satis/Self_esteem/Z*/interac-
# tion columns in Study 1, and self_esteem/power/authenticity/social_de-
# sirability/Total_relationship in Study 3, are aggregates, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URLS = {
    "s1": ("https://journals.plos.org/plosone/article/file"
           "?type=supplementary&id=10.1371/journal.pone.0146050.s001"),
    "s3": ("https://journals.plos.org/plosone/article/file"
           "?type=supplementary&id=10.1371/journal.pone.0146050.s003"),
}
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

S1_RENAME = {
    "Power1": "power1", "P2": "power2", "P3": "power3", "P4": "power4",
    "P5": "power5", "P6": "power6", "P7": "power7", "P8": "power8",
    "A_Living1": "authliving1", "A_Living2": "authliving2",
    "A_Living3": "authliving3", "A_L4": "authliving4",
    "A_aliennation1": "authalien1", "A_a2": "authalien2",
    "A_a3": "authalien3", "A_a4": "authalien4",
    "A_other1": "authexternal1", "A_o2": "authexternal2",
    "A_o3": "authexternal3", "A_o4": "authexternal4",
    "Relationship1": "relationship1", "R2": "relationship2", "R3": "relationship3",
    "R4": "relationship4", "R5": "relationship5", "R6": "relationship6", "R7": "relationship7",
}
S1_SCALES = {
    "wang_2016_study1_power": [f"power{i}" for i in range(1, 9)],
    "wang_2016_study1_authliving": [f"authliving{i}" for i in range(1, 5)],
    "wang_2016_study1_authalien": [f"authalien{i}" for i in range(1, 5)],
    "wang_2016_study1_authexternal": [f"authexternal{i}" for i in range(1, 5)],
    "wang_2016_study1_se": [f"se{i}" for i in range(1, 11)],
    "wang_2016_study1_relationship": [f"relationship{i}" for i in range(1, 8)],
}

MAP_CN5 = {"非常不符合": 1, "有些不符合": 2, "不能确定": 3, "有些符合": 4, "完全符合": 5}
MAP_SD = {0.0: 0, "非常不符合": 1}
S3_SCALES_MAPPED = {
    "wang_2016_study3_se": [f"se{i}" for i in range(1, 11)],
    "wang_2016_study3_power": [f"p{i}" for i in range(1, 9)],
    "wang_2016_study3_auth": [f"a{i}" for i in range(1, 13)],
}


def fetch(key: str) -> pd.DataFrame:
    r = requests.get(SI_URLS[key], headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


def melt_numeric(df, cov_cols, item_cols, out_name):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    save(long, cov_cols, out_name)


def melt_mapped(df, cov_cols, item_cols, value_map, out_name):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(value_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    save(long, cov_cols, out_name)


def save(long, cov_cols, out_name):
    long = long[["id", "item", "resp"] + cov_cols]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df1 = fetch("s1").rename(columns={"code": "id", "gender": "cov_sex", "age": "cov_age", **S1_RENAME})
    assert df1["id"].nunique() == len(df1)
    cov1 = ["cov_sex", "cov_age"]
    for out_name, item_cols in S1_SCALES.items():
        melt_numeric(df1, cov1, item_cols, out_name)

    df3 = fetch("s3")
    df3["id"] = df3.index
    df3 = df3.rename(columns={"age": "cov_age"})
    cov3 = ["cov_age"]
    for out_name, item_cols in S3_SCALES_MAPPED.items():
        melt_mapped(df3, cov3, item_cols, MAP_CN5, out_name)
    melt_mapped(df3, cov3, [f"sd{i}" for i in range(1, 6)], MAP_SD, "wang_2016_study3_social_desirability")


if __name__ == "__main__":
    convert()
