from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0229354
# DOI: 10.1371/journal.pone.0229354
# Jablonska et al. (2020), "Artificial neural networks for predicting
# social comparison effects among female Instagram users". S2 Dataset.
# CC BY 4.0. N=974. Text-coded 7-point Likert ("Strongly disagree" ...
# "Strongly agree") recoded to 1-7. The 54-item battery splits cleanly by
# content into 7 validated/named scales: Instagram addiction (10i),
# profile grooming (3i), upward social comparison (6i), downward social
# comparison (6i), Rosenberg Self-Esteem Scale (10i), HADS-style anxiety/
# depression items (14i), Satisfaction With Life Scale (5i).
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0229354.s006")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

LIKERT_MAP = {
    "Strongly disagree": 1, "Disagree": 2, "Rather disagree": 3,
    "Neither agree or disagree": 4, "Rather agree": 5, "Agree": 6, "Strongly agree": 7,
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df["id"] = range(1, len(df) + 1)
    return df


def _cols(df, start, end):
    items = [c for c in df.columns if c.split(".")[0].isdigit()]
    items = sorted(items, key=lambda c: int(c.split(".")[0]))
    return [c for c in items if start <= int(c.split(".")[0]) <= end]


def _ship(df, out_name, item_cols):
    long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp_text")
    long["resp"] = long["resp_text"].map(LIKERT_MAP)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    _ship(df, "jablonska_2020_instagram_addiction", _cols(df, 1, 10))
    _ship(df, "jablonska_2020_profile_grooming", _cols(df, 11, 13))
    _ship(df, "jablonska_2020_upward_comparison", _cols(df, 14, 19))
    _ship(df, "jablonska_2020_downward_comparison", _cols(df, 20, 25))
    _ship(df, "jablonska_2020_rses", _cols(df, 26, 35))
    _ship(df, "jablonska_2020_hads", _cols(df, 36, 49))
    _ship(df, "jablonska_2020_swls", _cols(df, 50, 54))


if __name__ == "__main__":
    convert()
