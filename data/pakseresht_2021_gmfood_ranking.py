from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0252580
# DOI: 10.1371/journal.pone.0252580
# Pakseresht et al. (2021), "Genetically modified food and consumer risk
# responsibility: The effect of regulatory design and risk type on
# cognitive information processing". S6 File. CC BY 4.0. N=535.
# Only the clean, unambiguous 4-item risk-dimension ranking task is
# shipped here: respondents rank Environmental/Health/Economic/Ethical
# risk dimensions of GM food, 1-4 (1=highest concern). The file's other
# columns (per-scenario sub1-4 ratings keyed by a randomized "dimension"
# assignment, and Res_P/F/I/R/C responsibility-allocation items with
# inconsistent max scales) need the source paper to interpret the
# scenario-assignment design safely and are not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0252580.s006")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_MAP = {"Env_rank": "environmental", "Hea_rank": "health",
            "Eco_rank": "economic", "Eth_rank": "ethical"}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch().rename(columns={"ID": "id"})
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"], value_vars=list(ITEM_MAP.keys()),
                    var_name="item", value_name="resp")
    long["item"] = long["item"].map(ITEM_MAP)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]
    out_path = OUT_DIR / "pakseresht_2021_gmfood_risk_ranking.csv"
    long.to_csv(out_path, index=False)
    print(f"pakseresht_2021_gmfood_risk_ranking: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
