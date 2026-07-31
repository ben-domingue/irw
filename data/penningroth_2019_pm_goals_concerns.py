from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0216888
# DOI: 10.1371/journal.pone.0216888
# Real-life prospective memory (PM) task recall study. Each participant
# free-recalled up to 5 real-life PM tasks; each task was then
# content-coded into 15 goal categories and 15 concern categories (binary
# 1 = at least one of the participant's PM tasks fell in this category, 0
# = none did). Coding scheme, category abbreviations, and column meanings
# come directly from the raw file's own "META-DATA" sheet, not inferred.
# percPMgr/percPMcr (% of a participant's PM tasks that were goal-/
# concern-related) are derived composites, not raw items -- excluded.
# grpYvsO (the 2-group young-vs-older split actually used in this study's
# analyses) is kept as a covariate alongside AgeGroup (the original
# 3-subgroup age coding, per the META-DATA sheet: "codes for the three
# subgroups for age ... with separate codes for two young groups, which
# were combined in this study").
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0216888.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "AgeGroup": "cov_age_group",
    "Gender": "cov_gender",
    "Health": "cov_health",
    "grpYvsO": "cov_group_young_vs_older",
}

GOAL_COLS = ["anyprfg", "anyprpg", "anyyheag", "anyoheag", "anykidg", "anymarg",
             "anyedug", "anytravg", "anyleisg", "anyretig", "anywarg",
             "anyworlg", "anyfrndg", "anyselfg", "anyothrg"]
CONCERN_COLS = ["anyprfc", "anyprpc", "anyyheac", "anyoheac", "anykidc", "anymarc",
                "anyeduc", "anytravc", "anyleisc", "anyretic", "anywarc",
                "anyworlc", "anyfrndc", "anyselfc", "anyothrc"]


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="DATASET")
    return df.rename(columns={"SN": "id", **COV_MAP})


def _write(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_MAP.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    _write(df, cov_cols, GOAL_COLS, "penningroth_2019_pm_goals")
    _write(df, cov_cols, CONCERN_COLS, "penningroth_2019_pm_concerns")


if __name__ == "__main__":
    convert()
