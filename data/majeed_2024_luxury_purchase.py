from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0295514
# DOI: 10.1371/journal.pone.0295514
# Majeed et al. (2024), "Determining online consumer's luxury purchase
# intention: The influence of antecedent factors and the moderating role
# of brand awareness, perceived risk, and web atmospherics". S1 Table.
# CC BY 4.0. N=267. 30-item luxury-purchase-intention battery (full item
# text kept as labels), text-coded 5-point Likert recoded 1-5.
# "Proficiency on the internet" (a different 4-point skill-rating item)
# not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0295514.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

LIKERT_MAP = {"Strongly Disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4, "Strongly agree": 5}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df["id"] = range(1, len(df) + 1)
    return df


def convert():
    df = fetch()
    item_cols = [c for c in df.columns if c not in ("Proficiency on the internet", "id")]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(LIKERT_MAP)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]
    out_path = OUT_DIR / "majeed_2024_luxury_purchase.csv"
    long.to_csv(out_path, index=False)
    print(f"majeed_2024_luxury_purchase: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
