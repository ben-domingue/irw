#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0227958
# DOI: 10.1371/journal.pone.0227958
# Supporting Information: https://doi.org/10.1371/journal.pone.0227958.s004
#
# Automated triage flagged this as low-confidence id mapping; id is
# clean/unique (403/403). Raw file has PSS-10 and RSES-10, both clean.
# A third 10-item block (closinglegs401..shouting410, about mistreatment
# during childbirth -- the paper's actual focal topic) takes values 1-10
# with a distribution that looks categorical (e.g. provider/location type)
# rather than ordinal severity -- not confidently interpretable as an
# ordinal item response, so not included here.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0227958.s004")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_PSS = {"Never": 0, "Almost Never": 1, "Sometimes": 2, "Fairly Often": 3, "Very Often": 4}
MAP_RSES = {"Strongly Disagree": 1, "Disagree": 2, "Agree": 3, "Strongly Agree": 4}

COV_RENAME = {"age101": "cov_age", "gender102": "cov_gender", "ethnicity104": "cov_ethnicity",
              "education107": "cov_education"}

PSS_COLS = ["upset201", "unablecontrol202", "stressed203", "confident204",
            "goingyourway205", "notcope206", "controlirritations207", "ontop208",
            "angered209", "difficulties210"]
RSES_COLS = ["satisfied301", "nogood302", "goodqualities303", "dowell304", "noproud305",
             "usefull306", "worth307", "morerespect308", "failure309", "positiveattitude310"]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str],
               value_map: dict, out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(value_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns={"ID": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    melt_scale(df, cov_cols, PSS_COLS, MAP_PSS, "bakker_2020_pss10")
    melt_scale(df, cov_cols, RSES_COLS, MAP_RSES, "bakker_2020_rses")


if __name__ == "__main__":
    convert()
