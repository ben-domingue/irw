from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0139944
# DOI: 10.1371/journal.pone.0139944
# Hermans et al. (2015). Rasch-built Myotonic Dystrophy Type 1 (DM1)
# activity/participation item bank (r_ods001..r_ods144, R-ODS-style naming
# from the same research group's Rasch-built Overall Disability Scale
# methodology), N=312. This is the full raw item-bank response matrix used
# to reconstruct the final 25-item DM1-Activ C scale via Rasch analysis --
# shipping the raw item bank rather than only the 25 items the paper's
# Rasch analysis retained, since IRW wants raw responses, not the
# post-selection published scale. 0/1/2 response scale (item-level
# difficulty rating; direction/labels not given in the raw file, kept as
# collected per datastandard.md -- direction may vary across items).
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0139944.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "gender": "cov_gender",
    "agecat": "cov_agecat",
    "diagnosis": "cov_diagnosis",
    "studydegr": "cov_studydegr",
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"studynr": "id", **COV_MAP})
    return df


def convert():
    df = fetch()
    assert df["id"].nunique() == len(df)

    cov_cols = list(COV_MAP.values())
    item_cols = [c for c in df.columns if c.startswith("r_ods")]

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "hermans_2015_dm1_rods.csv"
    long.to_csv(out_path, index=False)
    print(f"hermans_2015_dm1_rods: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
