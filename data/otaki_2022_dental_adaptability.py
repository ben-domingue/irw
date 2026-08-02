from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0270420
# DOI: 10.1371/journal.pone.0270420
# Otaki et al. (2022), "Self-reported adaptability among postgraduate
# dental learners and their instructors: Accelerated change induced by
# COVID-19". S1 File. CC BY 4.0. N=18 (small). 4-item adaptability scale
# (full item text kept), text-coded 5-point Likert recoded 1-5 (only
# "Agree"/"Strongly agree" observed in this small sample -- still mapped
# on the standard 5-point scale). The file's 4 open-ended reflection
# questions not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0270420.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

LIKERT_MAP = {"Strongly disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4, "Strongly agree": 5}
ITEM_COLS = [
    "I was able to effectively cope with the higher technological demands of distance learning.",
    "I was able to manage my time and efforts to cope with the transition to distance learning.",
    "I was able to monitor and evaluate my performance, and if need be- intervene, to cope with the transition to distance learning.",
    "I sought help, if needed, from students, colleagues, University staff, and/ or family members to cope with the transition to distance learning.",
]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch().rename(columns={"ID": "id"})
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(LIKERT_MAP)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]
    out_path = OUT_DIR / "otaki_2022_dental_adaptability.csv"
    long.to_csv(out_path, index=False)
    print(f"otaki_2022_dental_adaptability: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
