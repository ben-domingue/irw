"""Gao et al. (2022), PLOS ONE -- perceived stress and stress responses during COVID-19.

Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0279071
DOI: 10.1371/journal.pone.0279071
Data: S1 Dataset (journal.pone.0279071.s001, .xlsx)
License: CC BY 4.0

A Chinese online survey run during a 2022 lockdown. The S1 Dataset is the raw
survey export: 1,087 submitted questionnaires (the paper analyses 873 after its
own validity screening, which the deposit does not mark, so all submissions are
kept here) with the four instruments stored as consecutive blocks of columns
whose headers are the Chinese item stems.

Tables written
--------------
gao_2022_pss10                 10 Perceived Stress Scale items,        1-5
gao_2022_stress_response       28 Stress Response Questionnaire items, 1-5
gao_2022_scsq                  20 Simplified Coping Style items,       1-4
gao_2022_emotional_resilience  11 Emotional Resilience items,          1-6

The paper documents these scales as 0-4 / 1-5 / 0-3 / 0-6; the export stores
1-5 / 1-5 / 1-4 / 1-6 respectively, i.e. the same categories with 1-based
codes. Raw codes are kept as `resp` rather than shifted.

Item naming: source headers are the full Chinese item stems (the first column
of each block also carries the questionnaire's instruction text). They are
mapped to positional identifiers within each instrument -- PSS_1..PSS_10 etc. --
which match the numbering embedded in the stems themselves ("1.", "2.", ...),
so item text can be joined back later.

Covariates: `所用时间` is whole-survey completion time, not a per-item response
time, so it is exported as cov_completion_time_s rather than `rt`. One age cell
holds 19620621 (a birth date typed into the age field); it is dropped as a
data-entry error rather than carried into cov_age.
"""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

DOI = "10.1371/journal.pone.0279071"
SRC = ("https://journals.plos.org/plosone/article/file"
       "?id=10.1371/journal.pone.0279071.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# Source column blocks, by position. The header text is Chinese, so the layout
# is asserted against the questionnaire markers rather than matched by name.
COV_POS = {2: "cov_completion_time_s", 3: "cov_gender", 4: "cov_age",
           5: "cov_lockdown", 6: "cov_occupation", 7: "cov_economic_worry"}
ID_POS, DATE_POS = 0, 1

# (out_name, prefix, first_col, n_items, valid_range, questionnaire marker)
SCALES = [
    ("gao_2022_pss10", "PSS", 8, 10, (1, 5), "问卷一"),
    ("gao_2022_stress_response", "SRQ", 18, 28, (1, 5), "问卷二"),
    ("gao_2022_scsq", "SCSQ", 46, 20, (1, 4), "问卷三"),
    ("gao_2022_emotional_resilience", "ERQ", 66, 11, (1, 6), "问卷四"),
]

AGE_BOUNDS = (15, 100)


def fetch() -> pd.DataFrame:
    r = requests.get(SRC, headers=UA, timeout=300)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def build_frame(raw: pd.DataFrame) -> pd.DataFrame:
    if raw.shape[1] != 77:
        raise ValueError(f"expected 77 source columns, got {raw.shape[1]}")
    for _, _, first, _, _, marker in SCALES:
        if marker not in str(raw.columns[first]):
            raise ValueError(f"column {first} is not the start of {marker}")

    df = pd.DataFrame({"id": pd.to_numeric(raw.iloc[:, ID_POS], errors="coerce")})
    if df["id"].nunique() != len(df) or df["id"].isna().any():
        raise ValueError("source 序号 column is not a unique respondent id")

    # Submission timestamp -> Unix seconds.
    stamps = pd.to_datetime(raw.iloc[:, DATE_POS], errors="coerce")
    df["date"] = ((stamps - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")).astype("Int64")

    for pos, name in COV_POS.items():
        col = raw.iloc[:, pos]
        if name == "cov_completion_time_s":
            col = col.astype(str).str.extract(r"(\d+)")[0]
        df[name] = pd.to_numeric(col, errors="coerce")

    lo, hi = AGE_BOUNDS
    df.loc[~df["cov_age"].between(lo, hi), "cov_age"] = pd.NA

    for _, prefix, first, n, _, _ in SCALES:
        for i in range(n):
            df[f"{prefix}_{i + 1}"] = pd.to_numeric(
                raw.iloc[:, first + i], errors="coerce")
    return df


def make_scale(df: pd.DataFrame, prefix: str, n: int,
               bounds: tuple[int, int]) -> pd.DataFrame:
    items = [f"{prefix}_{i + 1}" for i in range(n)]
    cov_cols = list(COV_POS.values())
    long = df[["id", "date"] + cov_cols + items].melt(
        id_vars=["id", "date"] + cov_cols,
        value_vars=items,
        var_name="item",
        value_name="resp",
    )
    long = long.dropna(subset=["resp"])
    lo, hi = bounds
    long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
    long["resp"] = long["resp"].astype(int)
    long["id"] = long["id"].astype(int)
    order = ["id", "item", "resp", "date"] + cov_cols
    return (long[order]
            .sort_values(["id", "item"])
            .reset_index(drop=True))


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = build_frame(fetch())
    for name, prefix, _, n, bounds, _ in SCALES:
        long = make_scale(df, prefix, n, bounds)
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
