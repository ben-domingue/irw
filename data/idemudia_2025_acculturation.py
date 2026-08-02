from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0310351
# DOI: 10.1371/journal.pone.0310351
# Idemudia et al. (2025), "Cross-cultural validation of acculturation
# measures: Expanding the East Asian acculturation framework for global
# applicability". S1 Data. CC BY 4.0. N=329. 7 column-prefix-coded raw
# scales (no item text in the file, Qualtrics-style block codes), each
# with its own distinct response range confirmed at the column level:
# D101 (36i, 1-5), E201 (29i, 1-7), S101 (12i, 1-7), S201 (4i, 1-5), S301
# (6i, 1-5), T101 (16i, 1-4), T201 (12i, 1-6). All blocks had scattered
# unique-looking fractional values (e.g. 2.4, 2.666667, 3.2) on otherwise
# strictly integer items -- a mean/interpolation-imputation pattern for
# missing responses, not genuine raw data -- filtered to integers only.
# The file's large tail of named derived composite columns
# (Perceived_discrimination/GHQ_TOTAL/GAD_total/PHQ_total/etc.) not
# shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0310351.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "idemudia_2025_d101": [f"D101_{i:02d}" for i in range(1, 37)],
    "idemudia_2025_e201": [f"E201_{i:02d}" for i in range(1, 30)],
    "idemudia_2025_s101": [f"S101_{i:02d}" for i in range(1, 13)],
    "idemudia_2025_s201": [f"S201_{i:02d}" for i in range(1, 5)],
    "idemudia_2025_s301": [f"S301_{i:02d}" for i in range(1, 7)],
    "idemudia_2025_t101": [f"T101_{i:02d}" for i in range(1, 17)],
    "idemudia_2025_t201": [f"T201_{i:02d}" for i in range(1, 13)],
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    df["id"] = range(1, len(df) + 1)
    return df


def convert():
    df = fetch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        item_cols = [c for c in item_cols if c in df.columns]
        long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[long["resp"] % 1 == 0]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"]]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
