#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0277875
# DOI: 10.1371/journal.pone.0277875
# Supporting Information: https://doi.org/10.1371/journal.pone.0277875.s003
#
# The article has 4 Supporting Information files. S1/S4 contain only the
# derived Maslach Burnout Inventory subscale TOTALS (emotional exhaustion,
# depersonalization, personal accomplishment) plus a categorical burnout
# flag -- aggregates, not usable as items. S2/S3 contain the actual 22 raw
# item-level MBI responses (q1-q22); this script uses S3 (the .sav version,
# same content as S2's .xlsx).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0277875.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "age": "cov_age_group",
    "acyear": "cov_academic_year_group",
    "pt_turn": "cov_patient_turnover_group",
    "duty_hour": "cov_duty_hour_group",
    "Sex": "cov_sex",
    "Emplo_type": "cov_employment_type",
    "Degree": "cov_degree",
    "duty_place": "cov_duty_place",
    "dut_type": "cov_duty_type",
}

ITEM_COLS = [f"q{i}" for i in range(1, 23)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


def convert():
    df = fetch_data()
    df = df.rename(columns={"id": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype(int)
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "rashid_2022_mbi.csv"
    long.to_csv(out_path, index=False)
    print(f"rashid_2022_mbi.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
