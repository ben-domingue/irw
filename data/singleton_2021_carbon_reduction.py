from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0255445
# DOI: 10.1371/journal.pone.0255445
# Singleton et al. (2021), "Do legislated carbon reduction targets
# influence pro-environmental behaviours in public hospital pharmacy
# departments? Using mixed methods to compare Australia and the UK". S5
# File. CC BY 4.0. N=106. 15-item pro-environmental-behavior scale
# (Q1-Q15), 1-5. `NEP_Tot`/`Env_Concern`/`Self_Concord` (derived
# composite scores) not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0255445.s013")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Country": "cov_country", "Gender": "cov_gender", "Role_Binary": "cov_role"}
ITEM_COLS = [f"Q{i}" for i in range(1, 16)]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "ID": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "singleton_2021_carbon_reduction.csv"
    long.to_csv(out_path, index=False)
    print(f"singleton_2021_carbon_reduction: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
