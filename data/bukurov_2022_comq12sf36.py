#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0274513
# DOI: 10.1371/journal.pone.0274513
#
# "Can short PROMs support valid factor-based sub-scores? Example of
# COMQ-12 in chronic otitis media" (Bukurov et al., 2022)
#
# S5 Appendix (SAV) is the raw "minimum data set" for the analysis, N=246.
# It contains raw item-level responses to two instruments:
#   - COMQ-12 (Consonant-vowel test... actually Chronic Otitis Media
#     Questionnaire-12), 12 items, administered at two visits/phases
#     (V1 = phase 1 baseline, V2 = retest subsample, n~60). Raw response
#     range 0-5.
#   - SF-36, 36 items, V1 only. Different item blocks use different raw
#     response ranges by design (SF-36's own mixed 2/3/5/6-point item
#     formats), consistent with the standard SF-36 scoring manual, not a
#     data error (same pattern already confirmed clean for
#     amarilla_2020_barthel's mixed per-item maxima).
#
# All other columns (scaled/derived/factor-score/CFA/bifactor columns,
# demographics, hearing threshold aPTA/BPTA measures) are composites or
# clinical covariates, not raw item responses, and are excluded from
# resp. COMQ-12 V1 and V2 are stacked as wave=1/2 (repeated administration
# of the identical 12-item instrument on the same people, per
# datastandard.md's wave column).

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = "https://doi.org/10.1371/journal.pone.0274513.s005"

COMQ_ITEMS = [f"Q{i}COMQ12" for i in range(1, 13)]
SF36_ITEMS = [f"Q{i}SF36_V1" for i in range(1, 37)]

COV_MAP = {
    "Age": "cov_age",
    "Gender": "cov_gender",
    "Levelofeducation": "cov_education",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(DATA_URL, headers=UA, timeout=60)
    r.raise_for_status()
    from io import BytesIO
    return pd.read_spss(BytesIO(r.content))


def build_comq12(df: pd.DataFrame):
    cov_cols = list(COV_MAP.values())
    frames = []
    for wave, suffix in [(1, "_V1"), (2, "_V2")]:
        item_cols = [f"{c}{suffix}" for c in COMQ_ITEMS]
        item_cols = [c for c in item_cols if c in df.columns]
        sub = df[["id"] + cov_cols + item_cols].copy()
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["item"] = long["item"].str.replace(suffix, "", regex=False)
        long["wave"] = wave
        frames.append(long)
    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp", "wave"] + cov_cols
    long = long[out_cols].sort_values(["id", "wave", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "bukurov_2022_comq12.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def build_sf36(df: pd.DataFrame):
    cov_cols = list(COV_MAP.values())
    item_cols = [c for c in SF36_ITEMS if c in df.columns]
    sub = df[["id"] + cov_cols + item_cols].copy()
    long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                     var_name="item", value_name="resp")
    long["item"] = long["item"].str.replace("_V1", "", regex=False)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "bukurov_2022_sf36.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    print("Downloading S5 Appendix …")
    raw = fetch_data()
    raw = raw.rename(columns=COV_MAP)
    raw = raw.rename(columns={"Serialnumber": "id"})
    raw["id"] = pd.to_numeric(raw["id"], errors="coerce")
    raw = raw.dropna(subset=["id"]).reset_index(drop=True)
    assert raw["id"].nunique() == len(raw), "id not unique"

    build_comq12(raw)
    build_sf36(raw)


if __name__ == "__main__":
    convert()
