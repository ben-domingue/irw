from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0273763
# DOI: 10.1371/journal.pone.0273763
# Arnulf et al. (2022), "Dispositional and ideological factor correlate
# of conspiracy thinking and beliefs". S1 File. CC BY 4.0. N up to 398.
# Two scales shipped: `CT2` (14-item conspiracy-thinking scale, 1-9,
# text-coded endpoints "Completely false"/"Completely True" recoded) and
# `GK` (12-item general-knowledge quiz, Correct/Incorrect recoded to
# 1/0). NOT shipped: `CT1` (the item text itself leaked into the
# response cells in this export -- unusable as-is), `SCATI` (70 items,
# but each response is a 2-letter forced-choice code (SF/MT/MF/ST style),
# nominal rather than ordinal -- doesn't fit the core standard), and all
# derived composite/cluster columns.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0273763.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Sex": "cov_sex", "Age": "cov_age"}
CT2_MAP = {"Completely false\n1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
           "Completely True\n9": 9}
GK_MAP = {"Correct": 1, "Incorrect": 0}
GK_ITEMS = ["GK1", "GK13", "GK25", "GK37", "GK49", "GK61", "GK5", "GK14", "GK26", "GK39", "GK50", "GK62"]
CT2_ITEMS = [f"CT2_{i}" for i in range(1, 15)]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df["id"] = range(1, len(df) + 1)
    return df.rename(columns=COV_MAP)


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ct2 = df.melt(id_vars=["id"] + cov_cols, value_vars=CT2_ITEMS, var_name="item", value_name="resp")
    ct2["resp"] = ct2["resp"].astype(str).map(CT2_MAP)
    ct2 = ct2.dropna(subset=["resp"]).reset_index(drop=True)
    ct2 = ct2[["id", "item", "resp"] + cov_cols]
    ct2.to_csv(OUT_DIR / "arnulf_2022_conspiracy_thinking.csv", index=False)
    print(f"arnulf_2022_conspiracy_thinking: rows={len(ct2)} ids={ct2['id'].nunique()} "
          f"items={ct2['item'].nunique()} resp={ct2['resp'].min():.0f}-{ct2['resp'].max():.0f}")

    gk = df.melt(id_vars=["id"] + cov_cols, value_vars=GK_ITEMS, var_name="item", value_name="resp")
    gk["resp"] = gk["resp"].astype(str).map(GK_MAP)
    gk = gk.dropna(subset=["resp"]).reset_index(drop=True)
    gk = gk[["id", "item", "resp"] + cov_cols]
    gk.to_csv(OUT_DIR / "arnulf_2022_general_knowledge.csv", index=False)
    print(f"arnulf_2022_general_knowledge: rows={len(gk)} ids={gk['id'].nunique()} "
          f"items={gk['item'].nunique()} resp={gk['resp'].min():.0f}-{gk['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
