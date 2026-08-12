#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10569180 (PeerJ)
# DOI: 10.7717/peerj.16035
# License: CC BY 4.0
#
# "The Early Childhood Oral Health Impact Scale (ECOHIS): psychometric
# properties and application on preschoolers" (Silva, 2023, PeerJ). Raw
# file (peerj-11-16035-s001.xlsx) has the 13 raw ECOHIS items
# (ECOHIS1-13, values 0-5) alongside several derived composite/scoring
# columns (SCORE, ESRED, escoreF1, escoreF2) which are excluded here --
# these are what triggered the original triage's >50-unique-value
# aggregate_continuous flag when melted together with the raw items.

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

FILE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10569180/supplementaryFiles"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEMS = [f"ECOHIS{i}" for i in range(1, 14)]
COV_MAP = {
    "ID": "id", "agechild": "cov_age_child", "sex": "cov_sex",
    "agemother": "cov_age_mother", "civilstatus": "cov_civil_status",
    "work": "cov_work",
}


def _fetch_raw() -> pd.DataFrame:
    import io
    import zipfile
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    xlsx_name = [n for n in zf.namelist() if n.endswith("s001.xlsx")][0]
    return pd.read_excel(io.BytesIO(zf.read(xlsx_name)))


def convert():
    df = _fetch_raw()
    df = df.rename(columns=COV_MAP)
    assert df["id"].nunique() == len(df), "id not unique"
    cov_cols = list(COV_MAP.values())[1:]

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                    var_name="item", value_name="resp")
    long["item"] = long["item"].str.lower()
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 0) & (long["resp"] <= 5)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "silva_2023_ecohis"
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
