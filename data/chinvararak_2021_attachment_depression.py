#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0255995
# DOI: 10.1371/journal.pone.0255995
# Supporting Information: https://doi.org/10.1371/journal.pone.0255995.s001
#
# Thai depressed patients, N=180, 5 raw-item scales:
#   bdi   -- Beck Depression Inventory-II (21 items), already numeric 0-3.
#   phq15 -- PHQ-15 somatic symptom severity (15 items), 3-point Thai text
#            (not bothered / bothered a little / bothered a lot), mapped
#            0/1/2.
#   ylseq -- Young Life Stress Events Questionnaire (43 items), binary
#            Thai yes/no ("has/doesn't have" the life event), mapped 1/0.
#   ssq   -- Social Support Questionnaire (16 items, groups ssq1x/2x/3x),
#            5-point Thai text (least..most), mapped 1-5.
#   ecr   -- Experiences in Close Relationships (18 items, the paper's
#            focal attachment instrument), already numeric 1-7.
# Every scale's full Thai category set was enumerated across all its
# items before building the map (not assumed from one column). SumBDI,
# DepressionSeverityCat, AnxietyScore/Cat, AvoidanceScore/Cat, and
# AttachmentCat1/2 are derived aggregates, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0255995.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"sex": "cov_sex", "age": "cov_age", "status": "cov_marital_status",
              "education": "cov_education", "occupation": "cov_occupation"}

MAP_PHQ = {"ไม่รบกวน": 0, "รบกวนเล็กน้อย": 1, "รบกวนมาก": 2}
MAP_YLSEQ = {"ไม่มี": 0, "มี": 1}
MAP_SSQ = {"น้อยที่สุด": 1, "น้อย": 2, "ปานกลาง": 3, "มาก": 4, "มากที่สุด": 5}

BDI_COLS = [f"bdi{i}" for i in range(1, 22)]
PHQ_COLS = [f"phq{i}" for i in range(1, 16)]
YLSEQ_COLS = [f"ylseq{i}" for i in range(1, 44)]
SSQ_COLS = [f"ssq{a}{b}" for a, n in [(1, 7), (2, 4), (3, 5)] for b in range(1, n + 1)]
ECR_COLS = [f"ecr{i}" for i in range(1, 19)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns=COV_RENAME)


def melt_mapped(df, cov_cols, item_cols, value_map, out_name):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(value_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    save(long, cov_cols, out_name)


def melt_numeric(df, cov_cols, item_cols, out_name):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
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
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    melt_numeric(df, cov_cols, BDI_COLS, "chinvararak_2021_bdi")
    melt_mapped(df, cov_cols, PHQ_COLS, MAP_PHQ, "chinvararak_2021_phq15")
    melt_mapped(df, cov_cols, YLSEQ_COLS, MAP_YLSEQ, "chinvararak_2021_ylseq")
    melt_mapped(df, cov_cols, SSQ_COLS, MAP_SSQ, "chinvararak_2021_ssq")
    melt_numeric(df, cov_cols, ECR_COLS, "chinvararak_2021_ecr")


if __name__ == "__main__":
    convert()
