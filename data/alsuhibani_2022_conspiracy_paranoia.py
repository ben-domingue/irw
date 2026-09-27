#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0259053
# DOI: 10.1371/journal.pone.0259053
# Supporting Information: Study 1 https://doi.org/10.1371/journal.pone.0259053.s002
#                         Study 2 https://doi.org/10.1371/journal.pone.0259053.s003
#                         Study 3 https://doi.org/10.1371/journal.pone.0259053.s004
#
# Three independent samples. The paper's own Methods text confirms three
# instruments were administered identically across studies, so those are
# combined into single cross-study files (each study's id is offset by
# 100000*study_number to keep the combined id space unique):
#   - Locus of Control (MLCS, 24 items) -- explicitly "identical" across
#     Studies 1, 2, and 3.
#   - Self-Esteem Rating Scale (SERS, 20 items) -- explicitly used in
#     "Studies 2 and 3" (not administered in Study 1).
#   - Generic Conspiracist Beliefs Scale (GCBS) -- Study 3 used the 15-item
#     GCBS without the two additional items Study 2 carried. #2435: the two
#     studies do NOT share column positions. Study 2's variable labels put a
#     Princess Diana item at GCBS7 and another at GCBS16, canonical items 7-14
#     at GCBS8-15 and canonical item 15 at GCBS17. So Study 2 is mapped by
#     item, not position: GCBS1-6 -> 01-06, GCBS8-15 -> 07-14, GCBS17 -> 15.
#     The two Diana items (GCBS7, GCBS16 -- the "contradictory conspiracy
#     theories" probe, not in Study 3) are the Study-2-only extra file.
# PADS differs in both item count (10 vs 8) and scale range (0-4 vs 1-5)
# between Study 1 and Study 2 -- no confirmed item correspondence in the
# text, so these stay as separate per-study files. Consp (Study 1), the
# Revised Paranoia scale (Study 3), NPI (Study 3), and ECRS (Study 3) each
# appear in only one study and also stay as-is.
# CRT items, response-timing columns (First_Click/Last_Click/Page_Submit/
# Click_Count), and pre-computed subscale totals are excluded throughout.
# convert_categoricals=False avoids pd.read_spss's inconsistent value-label
# handling seen elsewhere in this batch.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SI_URLS = {
    1: "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0259053.s002",
    2: "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0259053.s003",
    3: "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0259053.s004",
}
ID_COL = {1: "id", 2: "ID", 3: "ID"}
COV_RENAME = {1: {"Q1": "cov_age", "SEX": "cov_sex"},
              2: {"AGE": "cov_age", "SEX": "cov_sex"},
              3: {"AGE": "cov_age", "SEX": "cov_sex"}}
STUDY_OFFSET = 100000


def load(study):
    r = requests.get(SI_URLS[study], headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content), convert_categoricals=False)


def prep_id(df, study):
    df = df.rename(columns={ID_COL[study]: "id", **COV_RENAME[study]})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    if df["id"].nunique() != len(df):
        df = df.drop(columns=["id"]).reset_index(drop=True)
        df.insert(0, "id", df.index + 1)
    df["id"] = df["id"] + STUDY_OFFSET * study
    return df


def write_scale(df, study, item_cols, out_name, valid_range=None):
    df = prep_id(df, study)
    cov_cols = list(COV_RENAME[study].values())
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    if valid_range:
        long = long[(long["resp"] >= valid_range[0]) & (long["resp"] <= valid_range[1])]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    save(long, out_name)


def write_merged_scale(parts, out_name):
    """parts: list of (df, study, {source_col: common_item_name})"""
    frames = []
    all_cov_cols = set()
    for df, study, rename in parts:
        df = prep_id(df, study)
        cov_cols = list(COV_RENAME[study].values())
        all_cov_cols.update(cov_cols)
        item_cols = list(rename.keys())
        sub = df[["id"] + cov_cols + item_cols].rename(columns=rename)
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=list(rename.values()),
                         var_name="item", value_name="resp")
        frames.append(long)
    cov_cols = sorted(all_cov_cols)
    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    for c in cov_cols:
        if c not in long.columns:
            long[c] = pd.NA
    long = long[["id", "item", "resp"] + cov_cols]
    save(long, out_name)


def save(long, out_name):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    s1 = load(1)
    s2 = load(2)
    s3 = load(3)

    write_scale(s1, 1, [f"PADS{i}" for i in range(1, 11)],
                "alsuhibani_2022_pads_s1", valid_range=(0, 4))
    write_scale(s1, 1, [f"Consp{i}" for i in range(1, 6)],
                "alsuhibani_2022_consp_s1", valid_range=(1, 11))
    write_scale(s2, 2, [f"PADS{i}" for i in range(1, 9)],
                "alsuhibani_2022_pads_s2", valid_range=(1, 5))
    write_scale(s2, 2, ["GCBS7", "GCBS16"],  # the two Diana items (#2435)
                "alsuhibani_2022_gcbs_extra_s2", valid_range=(1, 5))
    write_scale(s3, 3, [f"PARNOIA{i}" for i in range(1, 9)],
                "alsuhibani_2022_paranoia_s3", valid_range=(1, 5))
    write_scale(s3, 3, [f"NPI{i:02d}" for i in range(1, 14)],
                "alsuhibani_2022_npi_s3", valid_range=(0, 1))
    ecrs_cols = [f"ECRS{i:02d}R" if i in (1, 3, 5, 7, 11) else f"ECRS{i:02d}"
                 for i in range(1, 13)]
    write_scale(s3, 3, ecrs_cols, "alsuhibani_2022_ecrs_s3", valid_range=(1, 7))

    # Cross-study merges (confirmed identical instruments -- see header note)
    write_merged_scale(
        [(s1, 1, {f"LOC{i:02d}": f"LOC_{i:02d}" for i in range(1, 25)}),
         (s2, 2, {f"LOC{i}": f"LOC_{i:02d}" for i in range(1, 25)}),
         (s3, 3, {f"LOC{i:02d}": f"LOC_{i:02d}" for i in range(1, 25)})],
        "alsuhibani_2022_loc")

    write_merged_scale(
        [(s2, 2, {f"SERS{i}": f"SERS_{i:02d}" for i in range(1, 21)}),
         (s3, 3, {f"SERS{i:02d}": f"SERS_{i:02d}" for i in range(1, 21)})],
        "alsuhibani_2022_sers")

    write_merged_scale(
        [(s2, 2, {**{f"GCBS{i}": f"GCBS_{i:02d}" for i in range(1, 7)},
                  **{f"GCBS{i}": f"GCBS_{i - 1:02d}" for i in range(8, 16)},
                  "GCBS17": "GCBS_15"}),  # by item, not position (#2435)
         (s3, 3, {f"GCBS{i:02d}": f"GCBS_{i:02d}" for i in range(1, 16)})],
        "alsuhibani_2022_gcbs")


if __name__ == "__main__":
    convert()
