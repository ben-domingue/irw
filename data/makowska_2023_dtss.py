#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0287223
# DOI: 10.1371/journal.pone.0287223
# Supporting Information: https://doi.org/10.1371/journal.pone.0287223.s003
#
# Article has 2 SI files (S1 N=229, S2 N=558); this script uses S2, the
# larger sample with the same PSS-4 (4 items) and Digital Transformation
# Stress Scale (PDTS, 6 items) item sets. Items are Polish text-coded
# ("1. Nigdy" .. "5. Zawsze" = Never..Always) -- leading integer extracted.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0287223.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Gender": "cov_gender",
    "Birth_year": "cov_birth_year",
    "Edu_Degree": "cov_education",
    "Seniority": "cov_seniority",
    "Job_Position": "cov_job_position",
    "Remotly_work": "cov_remote_work",
}

SCALES = {
    "makowska_2023_pss4": ["PSS1", "PSS2", "PSS3", "PSS4"],
    "makowska_2023_pdts": [f"PDTS{i}" for i in range(1, 7)],
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(str).str.extract(r"(\d+)").astype(float)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns={"No": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    for out_name, item_cols in SCALES.items():
        melt_scale(df, cov_cols, item_cols, out_name)


if __name__ == "__main__":
    convert()
