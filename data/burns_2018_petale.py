from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0203435
# DOI: 10.1371/journal.pone.0203435
# Father and mother are separate respondents reporting on their own
# relationship (DAS-4) and psychological symptoms (BSI-18) -- shipped as
# four separate tables (one per instrument x respondent), id = the shared
# PETALE family/participant ID ("PT").
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0203435.s007")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "burns_2018_das4_father": r"DAS[1-4]_f$",
    "burns_2018_das4_mother": r"DAS[1-4]_m$",
    "burns_2018_bsi18_father": r"bsi\d+_f$",
    "burns_2018_bsi18_mother": r"bsi\d+_m$",
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    df = fetch()
    df = df.rename(columns={"PT": "id"})
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for out_name, pattern in SCALES.items():
        pat = re.compile(pattern)
        item_cols = [c for c in df.columns if pat.fullmatch(c)]
        long = df.melt(id_vars=["id"], value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"]]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
