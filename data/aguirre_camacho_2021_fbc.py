from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0249562
# DOI: 10.1371/journal.pone.0249562
# Short Health Anxiety Inventory (18 items) and Champion Breast Cancer
# Fear Scale (8 items). A retest subsample (n=78) completed the Champion
# scale a second time ("ChampB*" columns) -- kept as wave=1 for that
# subsample rather than a separate file, per datastandard.md's
# longitudinal rules (not every id needs every wave).
# The paper's own text confirms EM-algorithm imputation was applied to
# missing values (~1.3% of cells) in this same file before analysis --
# imputed cells surface as non-integer values on these otherwise
# integer-only Likert scales, so any non-integer resp is dropped as
# imputed rather than kept, per datastandard.md's imputation check.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0249562.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "Age": "cov_age",
    "LivingW": "cov_living_with",
    "StudyWork": "cov_study_or_work",
    "PHealth": "cov_physical_health",
    "FBCGroups": "cov_risk_group",
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    df = fetch()
    df = df.rename(columns={"ID": "id"})
    df = df.rename(columns=COV_MAP)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    assert df["id"].nunique() == len(df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    hanx_cols = [f"HAnx{i}" for i in range(1, 19)]
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=hanx_cols,
                   var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[long["resp"] == long["resp"].round()]
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "aguirre_camacho_2021_shai.csv"
    long.to_csv(out_path, index=False)
    print(f"aguirre_camacho_2021_shai: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")

    champ_cols = [f"Champ{i}" for i in range(1, 9)]
    champb_cols = [f"ChampB{i}" for i in range(1, 9)]
    long0 = df.melt(id_vars=["id"] + cov_cols, value_vars=champ_cols,
                    var_name="item", value_name="resp")
    long0["item"] = long0["item"].str.replace("Champ", "item", regex=False)
    long0["wave"] = 0
    long1 = df.melt(id_vars=["id"] + cov_cols, value_vars=champb_cols,
                    var_name="item", value_name="resp")
    long1["item"] = long1["item"].str.replace("ChampB", "item", regex=False)
    long1["wave"] = 1
    long = pd.concat([long0, long1], ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[long["resp"] == long["resp"].round()]
    long = long[["id", "item", "resp", "wave"] + cov_cols]
    out_path = OUT_DIR / "aguirre_camacho_2021_champion.csv"
    long.to_csv(out_path, index=False)
    print(f"aguirre_camacho_2021_champion: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
