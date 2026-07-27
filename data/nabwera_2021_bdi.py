#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0247554
# DOI: 10.1371/journal.pone.0247554
# Supporting Information: https://doi.org/10.1371/journal.pone.0247554.s002
#
# Raw file is a large menstrual-hygiene-management survey (~90 mostly
# single-question WASH/practice items, not a coherent multi-item scale)
# that also embeds the Beck Depression Inventory-II (20 items, columns
# named for each BDI-II symptom) among school-going adolescents in rural
# Gambia. Only the BDI-II block is genuine multi-item psychometric data;
# '85sdepscore' is the derived total (aggregate, excluded) and the WASH
# survey items are excluded as not a validated instrument.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0247554.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "3nAge": "cov_age",
    "4cGrade": "cov_grade",
    "7cReligion": "cov_religion",
}

BDI_COLS = ["66cSad", "67cPessimism", "68cPFailure", "69cLossPleasure",
            "70cGuiltF", "71cPunishment", "72cDislike", "73cCriticise",
            "74cSuicidal", "75cCry", "76cAgitation", "77cLossInterest",
            "78cIndecisiveness", "79cWorth", "80cEnergy", "81cSleep",
            "82cIrritability", "83cAppetite", "84cConcentration", "85cTired"]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch_data()
    df = df.rename(columns={"cSubjectID": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=BDI_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "nabwera_2021_bdi.csv", index=False)
    print(f"nabwera_2021_bdi.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
