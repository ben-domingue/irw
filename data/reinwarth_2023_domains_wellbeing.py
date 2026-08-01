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
# Same German representative-sample file as reinwarth_2023_loneliness.py
# (loneliness3/phq4 already shipped from there). Three more instruments
# from the same survey, confirmed via the file's own German variable
# labels (meta.variable_value_labels):
#   q11 (8 items, 1-5 "Nicht wichtig".."Extrem wichtig"): importance
#     rating of 8 life domains (friends, leisure, health, income, job,
#     housing, family, partnership).
#   q12 (8 items, 1-5 "Unzufrieden".."Sehr zufrieden"): satisfaction
#     rating of the same 8 domains.
#   q18 (6 items, 1-4 uniform frequency scale "Meistens".."ueberhaupt
#     nicht"): a short psychological-symptoms battery (tension, anxious
#     anticipation, worrying thoughts, feeling happy [reverse-worded],
#     feeling slowed down, lost interest in appearance) -- content
#     resembles HADS-A/D items but the uniform per-item response format
#     doesn't match HADS's item-specific wording, so it's shipped under a
#     descriptive name rather than a named instrument.
# q13 ("FLZ-" prefixed, described in TODO.md as the FLZ life-satisfaction
# questionnaire) was NOT shipped: its value range (-12 to +20 per column)
# confirms it's the FLZ's own weighted importance x satisfaction
# composite index, not a raw item response -- same q11/q12 domains,
# already covered as raw items above. All four batteries share a -1
# "Keine Angabe" (no answer) sentinel, dropped as missing.
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


def ship(df: pd.DataFrame, cov_cols: list[str], prefix: str, n_items: int, out_name: str):
    item_cols = [f"{prefix}_{i}" for i in range(1, n_items + 1)]
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[long["resp"] != -1]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()
    df = df.rename(columns=COV_MAP)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    assert df["id"].nunique() == len(df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ship(df, cov_cols, "q11", 8, "reinwarth_2023_domain_importance")
    ship(df, cov_cols, "q12", 8, "reinwarth_2023_domain_satisfaction")
    ship(df, cov_cols, "q18", 6, "reinwarth_2023_psych_symptoms")


if __name__ == "__main__":
    convert()
