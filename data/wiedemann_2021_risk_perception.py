from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0253762
# DOI: 10.1371/journal.pone.0253762
# Wiedemann, Boerner & Freudenstein (2021), "Effects of communicating
# uncertainty descriptions in hazard identification, risk characterization,
# and risk protection". S1 Dataset (.s007, SAV, no caption -- confirmed via
# variable labels this is the raw respondent data; other SI files .s001-
# .s006 are PDF questionnaire/vignette text, not data). CC BY 4.0. N=344.
# This is one of two distinct instrument blocks in the file (see also
# wiedemann_2021_text_readability.py for the other): F01/F02/F03/F04/F06,
# a 5-item risk-communication perception battery (comprehensibility,
# clarity, doubts about qualification, perceived risk magnitude, fear),
# each a 7-point scale. F05/F07-F10 do not exist in the file (skipped
# numbering in the source instrument, not a processing artifact).
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0253762.s007")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["F01", "F02", "F03", "F04", "F06"]
COV_COLS = {
    "Studie": "cov_condition",
    "rityp": "cov_risk_type",
    "faktor1": "cov_factor1",
    "faktor2": "cov_factor2",
    "Geschlecht": "cov_gender",
    "Alter": "cov_age",
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={"FraNr": "id", **COV_COLS})
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df)

    cov_names = list(COV_COLS.values())
    long = df.melt(id_vars=["id"] + cov_names, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_names]
    long.to_csv(OUT_DIR / "wiedemann_2021_risk_perception.csv", index=False)
    print(f"rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
