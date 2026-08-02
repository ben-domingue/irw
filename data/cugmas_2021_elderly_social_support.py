from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0247993
# DOI: 10.1371/journal.pone.0247993
# Cugmas et al. (2021), "The social support networks of elderly people
# in Slovenia during the Covid-19 pandemic". S1 Data. CC BY 4.0. N=605.
# Network-composition item set: count of network members of each named
# relationship type (partner/child/grandchild/other relative/friend/
# neighbour/other) in the respondent's support network. `totalSS`/
# `socializing`/`emotional`/`insturmental` (derived composite scores) not
# shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0247993.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"gndr": "cov_gender", "starank": "cov_age_rank", "edu": "cov_education",
           "martial": "cov_marital_status", "region": "cov_region"}
ITEM_COLS = ["partner", "child", "grandchild", "other_relative", "friend", "neighbour", "other"]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "ID": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "cugmas_2021_elderly_social_support.csv"
    long.to_csv(out_path, index=False)
    print(f"cugmas_2021_elderly_social_support: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
