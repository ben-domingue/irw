from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0208438
# DOI: 10.1371/journal.pone.0208438
# Wesselmann et al. (2018), "Does perceived ostracism contribute to
# mental health concerns among veterans who have been deployed?". S1
# File. CC BY 4.0. N=129 (no usable id column in the file -- row index
# used). 9 column-prefix raw-item scales: drri (12i), social support
# (15i), PCL (PTSD Checklist, 20i), trait anxiety (7i), state anxiety
# (6i), need-to-belong-style needs (20i), distress (5i), ostracism (10i),
# multidimensional perceived support (msp, 14i). "*R"-suffixed columns
# are pre-computed reverse-coded duplicates of already-included items,
# not shipped; nor are the derived composite totals (concern/support/
# ptsd/traitanx/stateanx/basicneeds/distress/chronic/milsupport).
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0208438.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "wesselmann_2018_drri": [f"drri{i}" for i in range(1, 13)],
    "wesselmann_2018_social_support": [f"social{i}" for i in range(1, 16)],
    "wesselmann_2018_pcl": [f"pcl{i}" for i in range(1, 21)],
    "wesselmann_2018_trait_anxiety": [f"trait{i}" for i in range(1, 8)],
    "wesselmann_2018_state_anxiety": [f"state{i}" for i in range(1, 7)],
    "wesselmann_2018_needs": [f"need{i}" for i in range(1, 21)],
    "wesselmann_2018_distress": [f"dis{i}" for i in range(1, 6)],
    "wesselmann_2018_ostracism": [f"ost{i}" for i in range(1, 11)],
    "wesselmann_2018_msp": [f"msp{i}" for i in range(1, 15)],
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df["id"] = range(1, len(df) + 1)
    return df


def convert():
    df = fetch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"]]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
