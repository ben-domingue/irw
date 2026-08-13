#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0270974
# DOI: 10.1371/journal.pone.0270974
#
# "Preliminary development of a multidimensional positive youth development
# scale for young rural and urban adolescents in China" (Wen, 2022)
#
# Two independently-recruited samples (no overlapping person IDs), each
# combining Beijing + Anhui respondents (see cov_region), given the same
# 26-item Positive Youth Development (PYD) scale (five subscales:
# Competence, Confidence, Character, Caring, Connection), 1-5 Likert.
# Same instrument, same items, same response scale -- collapsed into one
# file with `cov_study` (s1/s2) rather than two separate files, per
# ben-domingue's preference (2026-08-12) for merging same-instrument
# multi-sample data instead of splitting it, matching the precedent already
# used for powell_2018_empathy.py's Experiment 1/2 merge. S2 ids offset by
# +100000 to guarantee no collision with S1 (both samples' raw ids were
# already confirmed non-overlapping, offset applied defensively anyway).
# The paper's Data Availability files are only labeled "S1 Data"/"S2 Data"
# with no explicit rural/urban or phase-1/phase-2 correspondence confirmed
# in the Methods text, so `cov_study` is named after the SI item rather
# than guessing a rural/urban split.

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

S1_URL = "https://doi.org/10.1371/journal.pone.0270974.s001"
S2_URL = "https://doi.org/10.1371/journal.pone.0270974.s002"

ITEM_COLS = [
    "PYD_compe1", "PYD_compe2", "PYD_compe3", "PYD_compe4",
    "PYD_confi1", "PYD_confi2", "PYD_confi3", "PYD_confi4", "PYD_confi5",
    "PYD_confi6", "PYD_confi7",
    "PYD_character1", "PYD_character2", "PYD_character3", "PYD_character4",
    "PYD_care1", "PYD_care2", "PYD_care3", "PYD_care4", "PYD_care5",
    "PYD_connect1", "PYD_connect2", "PYD_connect3", "PYD_connect4",
    "PYD_connect5", "PYD_connect6",
]

REGION_MAP = {1.0: "beijing", 2.0: "anhui"}


def fetch_sav(url: str) -> pd.DataFrame:
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = OUT_DIR / "_tmp_wen2022.sav"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(r.content)
    df, _ = pyreadstat.read_sav(tmp)
    tmp.unlink()
    return df


def build_long(df: pd.DataFrame, study: str, id_offset: int) -> pd.DataFrame:
    df = df.copy()
    df = df.dropna(subset=["fid"]).reset_index(drop=True)
    assert df["fid"].nunique() == len(df), "fid not unique"

    df["id"] = df["fid"].astype(int) + id_offset
    df["cov_study"] = study
    df["cov_region"] = df["data"].map(REGION_MAP)
    df["cov_male"] = df["male"]
    df["cov_age"] = df["age"]

    cov_cols = ["cov_study", "cov_region", "cov_male", "cov_age"]
    item_cols = [c for c in ITEM_COLS if c in df.columns]

    long = df.melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["item"] = long["item"].str.replace("PYD_", "", regex=False)

    out_cols = ["id", "item", "resp"] + cov_cols
    return long[out_cols]


def convert():
    print("Downloading S1 Data …")
    raw1 = fetch_sav(S1_URL)
    d1 = build_long(raw1, "s1", id_offset=0)
    # fid values are household-style codes (observed up to ~470000 in S1),
    # not small sequential integers -- offset S2 past S1's actual max
    # rather than assuming a fixed round-number gap is enough.
    s2_offset = int(raw1["fid"].dropna().astype(int).max()) + 1
    print("Downloading S2 Data …")
    d2 = build_long(fetch_sav(S2_URL), "s2", id_offset=s2_offset)

    long = pd.concat([d1, d2], ignore_index=True)
    n_expected = d1["id"].nunique() + d2["id"].nunique()
    assert long["id"].nunique() == n_expected, "unexpected id overlap between S1 and S2"
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "wen_2022_pyd.csv"
    long.to_csv(out_path, index=False)
    print(f"wen_2022_pyd.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
