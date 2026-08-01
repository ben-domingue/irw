from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0230331
# DOI: 10.1371/journal.pone.0230331
# Brederecke, Scott, de Zwaan et al. (2020), "Psychometric properties of
# the German version of the Self-Image Scale (SIS)". S1 Dataset. CC BY
# 4.0. N=1367, German general-population sample.
#
# Two instruments -> two output files:
#   brederecke_2020_sis: Self-Image Scale, 11 items, 1-5.
#   brederecke_2020_phq4: PHQ-4, 4 items, 0-3.
# SIS_Self/SIS_Partner and PHQ_4/PHQ_2/GAD_2 in the same file are
# composite (sub)totals, not shipped.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0230331.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Sex": "cov_sex", "Age": "cov_age", "Nationality": "cov_nationality"}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def ship(df, cov_cols, item_cols, out_name):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch().rename(columns={"ID": "id", **COV_MAP})
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sis_cols = [f"SIS{i}" for i in range(1, 12) if f"SIS{i}" in df.columns]
    ship(df, cov_cols, sis_cols, "brederecke_2020_sis")

    phq_cols = [f"PHQ4_{i}" for i in range(1, 5) if f"PHQ4_{i}" in df.columns]
    ship(df, cov_cols, phq_cols, "brederecke_2020_phq4")


if __name__ == "__main__":
    convert()
