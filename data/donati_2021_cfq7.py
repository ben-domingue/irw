#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0246434
# DOI: 10.1371/journal.pone.0246434
# Supporting Information: https://doi.org/10.1371/journal.pone.0246434.s003
#
# Cognitive Fusion Questionnaire-7 (CFQ-7, the paper's focal instrument),
# clinical + non-clinical samples pooled (Population 1/2). ID is unique
# within Population 2 but has one collision within Population 1 (id 23,
# two rows with genuinely different item responses -- a duplicate-code
# data-entry issue, not an exact duplicate); Population-ID composite used
# as id, with a suffix to disambiguate that one collision. CFQ_THETA (IRT
# score), CAQ_TOT, SWLS, BDI are aggregates, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0246434.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"CFQ{i}" for i in range(1, 8)]

# Population 1 is the NON-clinical sample and Population 2 the clinical one.
# This file shipped them the other way round and the inversion reached published
# data (#1964). The SPSS file labels neither, so the mapping is asserted below
# against three things the paper states, rather than assumed:
#
#   n              258 non-clinical / 107 clinical (Participants; Fig 1; Table 3)
#   CFQ-7 total    non-clinical M = 25.50, SD = 8.55; clinical M = 32.38,
#                  SD = 7.23 -- "the latter showing significantly higher" CF,
#                  which is the whole point of the instrument
#   battery        CAQ_TOT, SWLS and BDI are complete for Population 1 and
#                  entirely absent for Population 2, because Table 2's
#                  correlations were computed "in the non-clinical sample"
#
# https://doi.org/10.1371/journal.pone.0246434
POPULATION_LABELS = {1.0: "non_clinical", 2.0: "clinical"}

# The paper's own numbers, to two decimals. A source revision that renumbered
# Population, or a future edit to POPULATION_LABELS, has to fail here.
EXPECTED = {
    "non_clinical": {"n": 258, "mean": 25.50, "sd": 8.55},
    "clinical":     {"n": 107, "mean": 32.38, "sd": 7.23},
}
NON_CLINICAL_ONLY = ["CAQ_TOT", "SWLS", "BDI"]


def check_population_labels(df: pd.DataFrame) -> None:
    """Refuse to write a file whose cov_population does not match the paper."""
    total = df[ITEM_COLS].sum(axis=1)
    for label, want in EXPECTED.items():
        grp = df["cov_population"] == label
        got = {"n": int(grp.sum()),
               "mean": round(float(total[grp].mean()), 2),
               "sd": round(float(total[grp].std()), 2)}
        assert got == want, f"cov_population={label}: expected {want}, got {got}"
    non_clin = df["cov_population"] == "non_clinical"
    for col in NON_CLINICAL_ONLY:
        assert df.loc[non_clin, col].notna().all(), f"{col} incomplete in non_clinical"
        assert df.loc[~non_clin, col].isna().all(), f"{col} present in clinical"


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df["cov_population"] = df["Population"].map(POPULATION_LABELS)
    df["id"] = (df["Population"].astype(int).astype(str) + "-" +
                df["ID"].astype(int).astype(str))
    dup_n = df.groupby("id").cumcount()
    df["id"] = df["id"] + dup_n.map({0: "", 1: "-b"}).fillna("")
    return df


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    check_population_labels(df)

    long = df.melt(id_vars=["id", "cov_population"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "cov_population"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "donati_2021_cfq7.csv", index=False)
    print(f"donati_2021_cfq7.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
