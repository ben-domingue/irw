from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0291207
# DOI: 10.1371/journal.pone.0291207
# Twis et al. (2024), "Coping self-efficacy and social support as
# predictors of adolescent sex trafficking exit: Results of a secondary
# analysis". S4 File. CC BY 4.0. N=95. Adverse-experience-type binary
# item set (10 items after dropping `CSAbuseScale`, constant at 0 in
# this sample): DV, physical abuse/neglect, bullying, dating violence,
# kidnapping, child pornography, theft, other violence, mass violence,
# labor trafficking.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0291207.s004")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["DVScale", "PhysAbNegScale", "BullyScale", "DatViolenceScale", "KidnapScale",
             "ChPornScale", "TheftScale", "OtherViolScale", "MassViolScale", "LaborTrafScale"]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"ID": "id"})


def convert():
    df = fetch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]
    out_path = OUT_DIR / "twis_2024_adverse_experience_types.csv"
    long.to_csv(out_path, index=False)
    print(f"twis_2024_adverse_experience_types: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
