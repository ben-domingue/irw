#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0263027
# DOI: 10.1371/journal.pone.0263027
# Supporting Information: https://doi.org/10.1371/journal.pone.0263027.s001
#
# Automated triage flagged this as low-confidence id mapping; `id` is
# actually clean and unique (1358/1358). Raw PHQ-9 (9 items) and GAD-7 (7
# items) present and clean. Raw file also has `phone` -- real PII
# (1358/1358 non-null phone numbers) -- dropped entirely. CIS-R domain
# severity scores (Somaticsymptoms..Socialimpairment) are themselves
# derived from an interview algorithm rather than direct single-item
# responses, and *_Total/*_groups/Diagnostic_groups/MIXED_D_A/GAD/DE
# columns are aggregates/classifications -- none of these used.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0263027.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"age": "cov_age", "qgender": "cov_gender", "qfield": "cov_field_of_study"}

PHQ_COLS = [f"PHQ9_{i}" for i in range(1, 10)]
GAD_COLS = [f"GAD7_{i}" for i in range(1, 8)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns=COV_RENAME)
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    melt_scale(df, cov_cols, PHQ_COLS, "pranckeviciene_2022_phq9")
    melt_scale(df, cov_cols, GAD_COLS, "pranckeviciene_2022_gad7")


if __name__ == "__main__":
    convert()
