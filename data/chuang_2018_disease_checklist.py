from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0194178
# DOI: 10.1371/journal.pone.0194178
# Chuang et al. (2018), "Effectiveness of Story-Centred Care Intervention
# Program in older persons living in long-term care facilities: A
# randomized, longitudinal study". S3 File. CC BY 4.0. N=60.
# Not the paper's main outcome scale (not in this file) -- an 11-item
# binary chronic-disease checklist (has/doesn't-have each condition),
# id/item/resp shape. `disease3` (constant 0, no variation in this
# sample) dropped. `total disease`/`distype` (derived) not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0194178.s005")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"sex": "cov_sex", "age": "cov_age", "group": "cov_group"}
ITEM_COLS = [f"disease{i}" for i in range(1, 11) if i != 3] + ["diease11"]
ITEM_RENAME = {"diease11": "disease11"}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "number": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["item"] = long["item"].replace(ITEM_RENAME)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "chuang_2018_disease_checklist.csv"
    long.to_csv(out_path, index=False)
    print(f"chuang_2018_disease_checklist: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
