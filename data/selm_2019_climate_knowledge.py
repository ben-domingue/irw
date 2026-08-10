from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0210149
# DOI: 10.1371/journal.pone.0210149
# Selm, Peterson, Hess, Beck & McHale (2019), "Educational attainment
# predicts negative perceptions women have of their own climate change
# knowledge". S1 File (.xlsx). CC BY 4.0. N=199 survey respondents.
# 3 items, 5-point Likert-style scales:
#   Q14_drought: personal experience of drought
#   Q15_disaster: personal experience of a weather-related disaster
#   Q36_know: self-rated knowledge of climate change
# Not a validated multi-item published scale, but 3 distinct items
# administered together in one questionnaire block -- passes the
# no-single-item-scale rule.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0210149.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = {
    "Q46_gender": "cov_gender",
    "Q47_age": "cov_age",
    "Q48_race": "cov_race",
    "Q49_education": "cov_education",
}
ITEM_COLS = ["Q14_drought", "Q15_disaster", "Q36_know"]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
        tmp.write(r.content)
        tmp.flush()
        df = pd.read_excel(tmp.name)

    df = df.rename(columns={"survey#": "id", **COV_COLS})
    for c in ITEM_COLS + list(COV_COLS.values()):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    cov_cols = list(COV_COLS.values())
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    out_name = "selm_2019_climate_knowledge"
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
