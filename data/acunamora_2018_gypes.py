from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0201007
# DOI: 10.1371/journal.pone.0201007
# Acuna Mora et al. (2018), "Patient empowerment in young persons with
# chronic conditions: Psychometric properties of the Gothenburg Young
# Persons Empowerment Scale (GYPES)". S3 File. CC BY 4.0. N=403.
# 15-item GYPES scale, 1-5; 999 is a widely-used missing/not-applicable
# sentinel (131/404 responses on item 1 alone) -- filtered.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0201007.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Sex": "cov_sex", "Age": "cov_age", "Education": "cov_education"}
ITEM_COLS = [f"gypes{i}" for i in range(1, 16)]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "respondentnummer": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[long["resp"] != 999]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "acunamora_2018_gypes.csv"
    long.to_csv(out_path, index=False)
    print(f"acunamora_2018_gypes: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
