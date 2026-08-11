#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0266762
# DOI: 10.1371/journal.pone.0266762
# Supporting Information: https://doi.org/10.1371/journal.pone.0266762.s001
#
# S1 Data (SAV): 155 Spanish families, PICCOLO (Parenting Interactions with
# Children: Checklist of Observations Linked to Outcomes) observational
# rating of fathers playing with their child at home. 29 items across four
# domains (Affection 7, Responsiveness 7, Encouragement 7, Teaching 8),
# each scored 0/1/2 ("absent" / "rare, minor or emerging" / "clear,
# definitive, strong and frequent"). MEAN_* columns are the domain/total
# composites - excluded. Mothers are rated on the same instrument in
# separate PICC_*_M* columns - see rivero_2022_piccolo_mother.py for that
# half of the same source file.

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0266762.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "child_gender": "cov_child_gender",
    "age_months": "cov_child_age_months",
    "age_F": "cov_father_age",
    "working_status_F": "cov_father_working_status",
}
# Note: source also has an "educational_level_F" column, but it is 100%
# empty (0 non-null values) in the raw SAV file - dropped rather than
# shipped as an all-NaN covariate.


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))

    df = df.rename(columns={"code_id": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique"

    item_cols = [c for c in df.columns if re.match(r"^PICC_.*_F\d+$", c)]
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["item"] = long["item"].str.replace("PICC_", "", regex=False).str.replace(
        "_F", "_", regex=False).str.lower()
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 0) & (long["resp"] <= 2)]

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "rivero_2022_piccolo_father.csv"
    long.to_csv(out_path, index=False)
    print(f"rivero_2022_piccolo_father: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
