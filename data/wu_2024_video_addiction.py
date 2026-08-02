from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0312597
# DOI: 10.1371/journal.pone.0312597
# Wu et al. (2024), "The relationship between proactive personality and
# college students' short-form video addiction: A chain mediation model
# of resilience and self-control". S1 Data. CC BY 4.0. N=560.
# Four scale blocks (column-prefix-delimited, no item text available):
# A1-A11 (11 items, 1-7 -- proactive personality), B1-B6 (6 items, 1-5 --
# resilience), C1-C7 (7 items, 1-5 -- self-control), D1-D14 (14 items,
# 1-5 -- short-form video addiction). Construct names inferred from the
# paper title/order, not confirmed against item text.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0312597.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "wu_2024_proactive_personality": [f"A{i}" for i in range(1, 12)],
    "wu_2024_resilience": [f"B{i}" for i in range(1, 7)],
    "wu_2024_self_control": [f"C{i}" for i in range(1, 8)],
    "wu_2024_video_addiction": [f"D{i}" for i in range(1, 15)],
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), header=1)
    df = df.rename(columns={"Unnamed: 0": "id"})
    return df


def convert():
    df = fetch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"]]
        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
