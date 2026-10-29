"""
The Short Dark Triad and a food-frequency battery, answered by 444 German-
speaking adults (study 2 of a paper on personality and dietary choices).

Source: Sariyska, R., Markett, S., Lachmann, B., & Montag, C. (2019). What Does
        Our Personality Say About Our Dietary Choices? Insights on the
        Associations Between Dietary Habits, Primary Emotional Systems and the
        Dark Triad of Personality. Frontiers in Psychology, 10, 2591.
DOI: 10.3389/fpsyg.2019.02591
Data: https://doi.org/10.3389/fpsyg.2019.02591.s001 (Data_Sheet_1, sheet "Raw
        data", header on row 3 -- rows 1-2 are a title, which is why the
        triage flagged this `recoverable_format`)
License: CC BY 4.0 (the article is CC BY per Europe PMC's core record, license
        "cc by"; the supplementary data sheet carries the article's licence)
Item text: ONE of the two tables ships, and the deposit is the reason it can --
        the workbook's second sheet, "Variable description", is a real codebook
        giving every variable's full wording and every response anchor.
          * `sariyska_2019_food_frequency` -- SHIPPED. The ten items are the
            study's own food-frequency questions (honey, fruits, pork, eggs,
            pasta/noodles, red meat, fish/sea food, vegetables, potatoes,
            poultry) under one shared stem, so they are study-authored material
            under the deposit's CC BY.
          * `sariyska_2019_dark_triad` -- HELD. The 27 items are the Short Dark
            Triad (SD3; Jones & Paulhus 2014) reproduced verbatim, and the SD3
            had NO row in itemtext/instrument_rights_register.csv. Silence does
            not ship (ben-domingue 2026-10-15), so this batch writes the row
            with verdict `hold`. The deposit's CC BY covers the depositors' own
            material, not a third-party instrument reproduced inside it.

The EBQ block is NOT one instrument, and the split follows the codebook rather
than the prefix. `EBQ_01` ("Do you in any way adopt a vegetarian diet?", four
named diet categories) and `EBQ_02` ("If so, what is the main reason for you
not to consume meat?", six named reasons) are single nominal questions on
different answer sets, and `EBQ_02` is asked only of the respondents `EBQ_01`
filters in -- its 0 is the not-applicable code, which the codebook does not
list among its six values. Both ship as covariates. `EBQ_03`..`EBQ_12` are the
ten food-frequency items: one shared stem, one 1-7 never-to-six-times-or-more
scale, and that is the table.

PII: none. Every column is numeric, the file has no identifier column at all
(`id` is the row index), and no name, date, free-text or geographic column. The
screen below prints its denominator.

Output: two tables, 16,428 responses -- 444 respondents, no missing data.
  * sariyska_2019_dark_triad      -- 27 items, resp 1-5
  * sariyska_2019_food_frequency  -- 10 items, resp 1-7
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Data_Sheet_1.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

SHEET = "Raw data"
HEADER_ROW = 2          # 0-based; rows 1-2 of the sheet are a title

# The permitted response set of each block is not inferred from the observed
# values -- it is read off the workbook's "Variable description" sheet, which
# names every anchor: 1 "Disagree strongly" .. 5 "Agree strongly" for the SD3,
# and 1 "never" .. 7 "six times or more" for the food-frequency items. That is
# a complete documented set, so it is passed to run_qc as `permitted_values`,
# which is what distinguishes "a rarely used extreme" from "a different scale"
# on the three SD3 items nobody answered 5 to.
BLOCKS = {
    "sariyska_2019_dark_triad": ([f"SD3_{i:02d}" for i in range(1, 28)],
                                 [1, 2, 3, 4, 5]),
    "sariyska_2019_food_frequency": ([f"EBQ_{i:02d}" for i in range(3, 13)],
                                     [1, 2, 3, 4, 5, 6, 7]),
}

COV_MAP = {
    "Sex": "cov_sex",
    "Age": "cov_age",
    "Education": "cov_education",
    "EBQ_01": "cov_vegetarian_diet",
    "EBQ_02": "cov_meat_avoidance_reason",
}

# EBQ_02's codebook lists six reasons, 1-6; its 0 is the not-applicable code
# for respondents the EBQ_01 filter did not route to the question.
NOT_APPLICABLE = {"cov_meat_avoidance_reason": 0}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; dtypes present: "
          f"{sorted({str(t) for t in df.dtypes})}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected text column(s): {text_cols}"


def main() -> None:
    df = pd.read_excel(SRC, sheet_name=SHEET, header=HEADER_ROW)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 444, len(df)

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        col = df[src]
        if dst in NOT_APPLICABLE:
            col = col.replace(NOT_APPLICABLE[dst], pd.NA)
            print(f"{dst}: {int((df[src] == NOT_APPLICABLE[dst]).sum())} "
                  f"not-applicable cell(s) nulled -- the codebook lists six "
                  f"reasons (1-6) and this question is only asked of the "
                  f"respondents EBQ_01 filters in")
        df[dst] = col
    covs = list(COV_MAP.values())

    accounted = (set(COV_MAP) | set(covs) | {"id"}
                 | {c for cols, _p in BLOCKS.values() for c in cols})
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"

    for table, (cols, permitted) in BLOCKS.items():
        assert all(c in df.columns for c in cols), (table, cols)
        codes = {c: c.lower() for c in cols}
        assert len(set(codes.values())) == len(cols), codes
        long = df[["id"] + covs + cols].rename(columns=codes)
        long = long.melt(id_vars=["id"] + covs, var_name="item",
                         value_name="resp")
        before = long["resp"].notna().sum()
        long = long[long["resp"].isin(permitted)]
        assert before == len(long), \
            f"{table}: {before - len(long)} cell(s) outside {permitted}"
        write(long, table, covs, permitted)


def write(long: pd.DataFrame, table: str, covs: list,
          permitted: list) -> None:
    long = long.copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=permitted)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:200]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
