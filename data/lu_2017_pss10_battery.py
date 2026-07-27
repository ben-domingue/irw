#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0189543
# DOI: 10.1371/journal.pone.0189543
# Supporting Information: https://doi.org/10.1371/journal.pone.0189543.s001 (retest, N=129)
#                          https://doi.org/10.1371/journal.pone.0189543.s002 (main test, N=1296)
#
# The article has 2 Supporting Information files: S2 is the main sample
# (N=1296) and S1 is a test-retest reliability subsample (N=129) -- all 129
# S1 "No." ids are a subset of S2's, confirmed by exact overlap check, so
# this is a genuine 2-wave design (wave=1 main test, wave=2 retest), not
# two independent datasets. The automated triage only found S1 (n=129) --
# S2's much larger main sample, and the wave structure between them, were
# both missed. Raw files bundle 3 scales: PHQ-9 (9 items; the PHQ_F
# functional-impairment item and PHQ9/GAD7 TOTAL columns are excluded --
# different response scale / aggregate respectively), GAD-7 (7 items),
# PSS-10 (10 items). A "Name" column exists but is entirely empty in both
# files (verified via .notna() count, not by viewing values) -- dropped.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

S1_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0189543.s001")
S2_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0189543.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "lu_2017_phq9": [f"PHQ_{i}" for i in range(1, 10)],
    "lu_2017_gad7": [f"GAD_{i}" for i in range(1, 8)],
    "lu_2017_pss10": [f"PSS_{i}" for i in range(1, 11)],
}


def fetch(url: str, wave: int) -> pd.DataFrame:
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"No.": "id", "Sex": "cov_sex"})
    df["wave"] = wave
    return df


def melt_scale(df: pd.DataFrame, item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id", "wave", "cov_sex"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    # PSS-10 is scored 0-4; a single -1 (1 of 14250 rows, on PSS_5) is a
    # data-entry error, not a real response category -- drop it.
    long.loc[long["resp"] < 0, "resp"] = float("nan")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave", "cov_sex"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()} waves={sorted(long['wave'].unique())}")


def convert():
    main = fetch(S2_URL, wave=1)
    retest = fetch(S1_URL, wave=2)
    combined = pd.concat([main, retest], ignore_index=True)
    assert set(retest["id"]) <= set(main["id"])

    for out_name, item_cols in SCALES.items():
        melt_scale(combined, item_cols, out_name)


if __name__ == "__main__":
    convert()
