#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0221323
# DOI: 10.1371/journal.pone.0221323
# Supporting Information: https://doi.org/10.1371/journal.pone.0221323.s002
#
# Automated triage flagged this as low-confidence id mapping; id is
# clean/unique (464/464). Raw file has the 19-item Copenhagen Burnout
# Inventory - Korean version (BT_I personal 6 items, BT_W work-related 7
# items, BT_C client-related 6 items -- the paper's focal instrument) and
# the CES-D-10 (10 items).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0221323.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_CBI = {"never(0%)": 0, "seldom(25%)": 1, "sometimes(50%)": 2, "often(75%)": 3,
           "alway(100%)": 4}
MAP_CESD = {"very rarely or less than once per day": 0,
            "sometimes or 1-2days during the past week": 1,
            "often or 3-4 days during the past week": 2,
            "almost always or 5-7days during the past week": 3}

COV_RENAME = {"marital": "cov_marital_status", "education": "cov_education",
              "age": "cov_age", "wk_hr": "cov_work_hours"}

CBI_COLS = ([f"BT_I_{i}" for i in range(1, 7)] + [f"BT_W_{i}" for i in range(1, 8)] +
            [f"BT_C_{i}" for i in range(1, 7)])
CESD_COLS = [f"cesd{i}" for i in range(1, 11)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


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
    df = df.rename(columns={"ID": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    melt_scale(df, cov_cols, CBI_COLS, MAP_CBI, "jeon_2019_cbi")
    melt_scale(df, cov_cols, CESD_COLS, MAP_CESD, "jeon_2019_cesd10")


if __name__ == "__main__":
    convert()
