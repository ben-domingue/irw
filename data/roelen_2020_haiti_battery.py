#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243457
# DOI: 10.1371/journal.pone.0243457
# Supporting Information: https://doi.org/10.1371/journal.pone.0243457.s002
#
# Automated triage flagged this as low-confidence id mapping. The paper is
# specifically about validating the Rosenberg Self-Esteem Scale (q_407-
# q_416, 10 items) in rural Haiti; the raw file also has a Kessler-6
# psychological distress scale (q_401-q_406) and, separately, a 17-item
# binary Household Dietary Diversity checklist (q_305-q_321, "did the
# household eat food group X yesterday") -- a genuine coherent item set,
# though not psychometric mental-health data. Item text confirmed via
# Stata variable labels (pyreadstat), not guessed from question codes.
# The bulk of this ~240-column household survey (demographics, Poverty
# Probability Index, program-treatment fields) is heterogeneous survey
# data, not used.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0243457.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_K6 = {"None (0 day)": 0, "A little (1-9 days)": 1, "Some (10-19 days)": 2,
          "Most (20-29 days)": 3, "All (30 days)": 4}
MAP_RSES = {"Strongly disagree": 1, "Disagree": 2, "Agree": 3, "Strongly agree": 4}
MAP_YESNO = {"No": 0, "Yes": 1}

COV_RENAME = {"treatmentgroup": "treat", "location": "cov_location"}

K6_COLS = [f"q_{i}" for i in range(401, 407)]
RSES_COLS = [f"q_{i}" for i in range(407, 417)]
DDS_COLS = [f"q_{i}" for i in range(305, 322)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_stata(io.BytesIO(r.content))


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str],
               value_map: dict, out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(value_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns={"hhid_unique": "id", **COV_RENAME})
    df["treat"] = pd.to_numeric(df["treat"], errors="coerce")
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    melt_scale(df, cov_cols, K6_COLS, MAP_K6, "roelen_2020_k6")
    melt_scale(df, cov_cols, RSES_COLS, MAP_RSES, "roelen_2020_rses")
    melt_scale(df, cov_cols, DDS_COLS, MAP_YESNO, "roelen_2020_dietary_diversity")


if __name__ == "__main__":
    convert()
