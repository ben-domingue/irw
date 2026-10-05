from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0241075
# DOI: 10.1371/journal.pone.0241075
# Ritzel et al. (2020), "Empirical evidence on factors influencing
# farmers' administrative burden: A structural equation modeling
# approach". S1 Data. CC BY 4.0. N=802. 13 raw item columns spanning four
# sub-batteries: administrative burden (y1-y3, y6-y9, 1-7), compliance
# costs (y4, 1-4; y5, 1-6), psychological costs (x2-x4, 1-7), knowledge/
# education (x1, 1-8) -- response ranges genuinely differ by item/
# construct, not a data error. The source's "CODE" column runs 1..802 and
# is unique: it is the respondent code, not a region. It was once shipped
# as cov_region (= id + 1, one value per respondent; irw#2842) and is now
# dropped. id stays the row index (0..801), i.e. CODE - 1.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0241075.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["y1", "y2", "y3", "y4", "y5", "y6", "y7", "y8", "y9", "x1", "x2", "x3", "x4"]


def convert(out_dir: Path = OUT_DIR):
    out_dir.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    assert df["CODE"].is_unique and (df["CODE"] == df.index + 1).all()
    df["id"] = df.index

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]
    long.to_csv(out_dir / "ritzel_2020_farmer_burden.csv", index=False)
    print(f"rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT_DIR)
