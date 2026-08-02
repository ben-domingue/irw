from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0228961
# DOI: 10.1371/journal.pone.0228961
# Agogue et al. (2020), "Nudging individuals' creativity using social
# labeling". S1 File. CC BY 4.0. N=200. Self-perceived-creativity scale
# (SPCpre_1-6), 1-7. `SPCpre_M`/`SPCpre_BI` (derived) and `PKM` (a
# French free-text question) not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0228961.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Group": "cov_group", "Education": "cov_education", "Gender": "cov_gender", "Age": "cov_age"}
ITEM_COLS = [f"SPCpre_{i}" for i in range(1, 7)]


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
    out_path = OUT_DIR / "agogue_2020_self_perceived_creativity.csv"
    long.to_csv(out_path, index=False)
    print(f"agogue_2020_self_perceived_creativity: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
