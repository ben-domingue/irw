from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0283850
# DOI: 10.1371/journal.pone.0283850
# Makai et al. (2023), "Perceived university support and environment as
# a factor of entrepreneurial intention: Evidence from Western
# Transdanubia Region". S1 File. CC BY 4.0. N=144. 37-item
# entrepreneurial-intention/university-support battery (full item text
# kept as labels), text-coded 5-point Likert recoded 1-5.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0283850.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Gender": "cov_gender", "Birth": "cov_birth_year", "Faculty ": "cov_faculty"}
LIKERT_MAP = {"Absolutely disagree": 1, "Rather disagree": 2, "Indifferent to me": 3,
              "Rather agree": 4, "Strongly agree": 5}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns=COV_MAP)
    df["id"] = range(1, len(df) + 1)
    return df


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    non_item_cols = set(cov_cols) | {"id", "Classification", "Finance ", "Grad year"}
    item_cols = [c for c in df.columns if c not in non_item_cols]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(LIKERT_MAP)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "makai_2023_entrepreneurial_transdanubia.csv"
    long.to_csv(out_path, index=False)
    print(f"makai_2023_entrepreneurial_transdanubia: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
