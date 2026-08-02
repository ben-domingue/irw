from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0240103
# DOI: 10.1371/journal.pone.0240103
# Shan et al. (2020), "A mix-method investigation on acculturative
# stress among Pakistani students in China". S1 File. CC BY 4.0. N=203.
# Text-coded 5-point Likert ("strongly disagree" ... "strongly agree")
# recoded to 1-5. Six column-prefix subscales, no item text in the file:
# PD (8i), HS (4i), PH (5i), F (4i), CS (3i), G (2i). "Misc1-6" columns
# excluded -- likely a separate, uncertain block.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0240103.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Age": "cov_age", "Gender": "cov_gender", "Level": "cov_level"}

LIKERT_MAP = {"strongly disagree": 1, "disagree": 2, "neutral": 3, "agree": 4, "strongly agree": 5}

SCALES = {
    "shan_2020_pd": [f"PD{i}" for i in range(1, 9)],
    "shan_2020_hs": [f"HS{i}" for i in range(1, 5)],
    "shan_2020_ph": [f"PH{i}" for i in range(1, 6)],
    "shan_2020_f": [f"F{i}" for i in range(1, 5)],
    "shan_2020_cs": [f"CS{i}" for i in range(1, 4)],
    "shan_2020_g": [f"G{i}" for i in range(1, 3)],
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "ID": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(str).str.lower().map(LIKERT_MAP)
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
