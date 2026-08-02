from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0306702
# DOI: 10.1371/journal.pone.0306702
# Sandhu et al. (2024), "The role of project management office in the
# implementation of strategic plans in project-based organisations". S1
# Data. CC BY 4.0. N=303. 1-5 Likert throughout. 11 distinct column-coded
# blocks shipped under their raw Qualtrics codes (Q13/Q16/Q18/Q19/Q20/
# Q21/Q22/Q23/Q24/Q26/Q32) -- no item text or construct labels are in the
# file, so names are not inferred. Single-response/degenerate columns
# (Q1/Q2/Q10/Q15/Q17/Q25/Q28, all constant) and open-text columns
# (Q4_TEXT/Q12_TEXT) not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0306702.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "sandhu_2024_pmo_q13": [f"Q13_{i}" for i in range(1, 7)],
    "sandhu_2024_pmo_q16": [f"Q16_{i}" for i in range(1, 7)],
    "sandhu_2024_pmo_q18": [f"Q18_{i}" for i in range(1, 5)],
    "sandhu_2024_pmo_q19": [f"Q19_{i}" for i in range(1, 6)],
    "sandhu_2024_pmo_q20": [f"Q20_{i}" for i in range(1, 6)],
    "sandhu_2024_pmo_q21": [f"Q21_{i}" for i in range(1, 6)],
    "sandhu_2024_pmo_q22": [f"Q22_{i}" for i in range(1, 5)],
    "sandhu_2024_pmo_q23": [f"Q23_{i}" for i in range(1, 5)],
    "sandhu_2024_pmo_q24": [f"Q24_{i}" for i in range(1, 4)],
    "sandhu_2024_pmo_q26": [f"Q26_{i}" for i in range(1, 13)],
    "sandhu_2024_pmo_q32": [f"Q32_{i}" for i in range(1, 7)],
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
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
