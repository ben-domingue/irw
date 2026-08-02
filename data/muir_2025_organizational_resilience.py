from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0338728
# DOI: 10.1371/journal.pone.0338728
# Muir et al. (2025), "Investigating organizational resilience in a
# medicine and health sciences university in United Arab Emirates". S5
# File. CC BY 4.0. N=70. Two scales (full item labels kept), each
# text-coded: `opinions` (7 items, 5-11, "Strongly Disagree".."Strongly
# Agree" recoded 1-5) and `behaviours` (8 items, 12-19, "Never".."Always"
# frequency scale recoded 1-5). A handful of cells held combined
# multi-select values (e.g. "Agree, Strongly Agree") -- a checkbox-entry
# artifact, not a valid single response -- dropped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0338728.s005")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"1_current_age": "cov_age", "2_gender": "cov_gender", "3_role": "cov_role",
           "4_length_of_service": "cov_length_of_service"}
OPINION_MAP = {"Strongly Disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4, "Strongly Agree": 5}
BEHAVIOUR_MAP = {"Never": 1, "Rarely": 2, "Sometimes": 3, "Frequently": 4, "Always": 5}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "ID": "id"})


def _ship(df, out_name, item_cols, likert_map, cov_cols):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(likert_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    opinion_cols = [c for c in df.columns if c.startswith(tuple(f"{n}_" for n in range(5, 12)))]
    behaviour_cols = [c for c in df.columns if c.startswith(tuple(f"{n}_" for n in range(12, 20)))]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    _ship(df, "muir_2025_resilience_opinions", opinion_cols, OPINION_MAP, cov_cols)
    _ship(df, "muir_2025_resilience_behaviours", behaviour_cols, BEHAVIOUR_MAP, cov_cols)


if __name__ == "__main__":
    convert()
