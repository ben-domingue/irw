from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0279701
# DOI: 10.1371/journal.pone.0279701
# German representative population survey. Two clean, clearly-labeled
# instruments shipped here: a 3-item loneliness scale (q16_1-3, German
# variable labels confirm "feeling that others' company is missing" /
# "feeling left out" / "feeling socially isolated" -- the well-known
# UCLA-3/de Jong Gierveld-style brief loneliness measure) and PHQ-4
# (q17_1-4, the ultra-brief PHQ-2+GAD-2 combination, confirmed by the
# file's own phq_2/gad_2 composite variable labels). The file also
# contains an 8-domain importance/satisfaction battery (q11/q12) and the
# validated FLZ life-satisfaction questionnaire (q13, German-specific
# instrument) plus an unidentified 6-item block (q18) -- not shipped this
# pass; would need per-domain label translation (q11/q12/q13) or
# instrument identification (q18) beyond what this pass had time for.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0279701.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "s1": "cov_gender",
    "alter": "cov_age",
    "s4": "cov_marital_status",
    "education": "cov_education",
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    df = fetch()
    df = df.rename(columns=COV_MAP)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    assert df["id"].nunique() == len(df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    lone_cols = [f"q16_{i}" for i in range(1, 4)]
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=lone_cols,
                   var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "reinwarth_2023_loneliness3.csv"
    long.to_csv(out_path, index=False)
    print(f"reinwarth_2023_loneliness3: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")

    phq_cols = [f"q17_{i}" for i in range(1, 5)]
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=phq_cols,
                   var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "reinwarth_2023_phq4.csv"
    long.to_csv(out_path, index=False)
    print(f"reinwarth_2023_phq4: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
