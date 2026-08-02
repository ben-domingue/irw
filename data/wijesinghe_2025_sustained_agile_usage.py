from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0316538
# DOI: 10.1371/journal.pone.0316538
# Wijesinghe et al. (2025), "Does management support drive sustained
# agile usage? a serial mediation model and cIPMA perspective". S1 Data.
# CC BY 4.0. N=391. Only the SAU (Sustained Agile Usage) block is
# shipped -- 8 items, 1-5, matching the paper's headline construct by
# name. The file's ~10 other 1-5 blocks (ATLS/ATCE/ATESG/ATCCC/Res/Rob/
# Per/Sel/Cap/Con/Ali/AT/MS) are cryptically 2-5-letter-coded with no
# item text and mostly only 1-2 items each -- not shipped without the
# paper's instrument key (several are single items, which would violate
# the no-single-item-scale rule regardless).
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0316538.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Age": "cov_age", "Gender": "cov_gender", "Agile Experience": "cov_agile_experience",
           "Company Size": "cov_company_size", "Team Size": "cov_team_size"}
ITEM_COLS = [f"SAU0{i}" for i in range(1, 9)]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "Response Number": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "wijesinghe_2025_sustained_agile_usage.csv"
    long.to_csv(out_path, index=False)
    print(f"wijesinghe_2025_sustained_agile_usage: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
