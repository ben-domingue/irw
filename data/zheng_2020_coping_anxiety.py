"""
The Simplified Coping Style Questionnaire and the HADS, answered by 646 Chinese
female undergraduates -- TWO of the deposit's three instruments, because the
third is stored on a scale the article itself contradicts.

Source: Zheng, Z., Han, W., Li, Y., Wang, D., Gu, S., & Wang, F. (2020). The
        Mediating Effect of Coping Style in the Relationship Between Depression
        and Disordered Eating Among Chinese Female Undergraduates. Frontiers in
        Psychology, 10, 3011.
DOI: 10.3389/fpsyg.2019.03011
Data: https://doi.org/10.3389/fpsyg.2019.03011.s001 (Data_Sheet_1; the triage
        flagged this `recoverable_format`)
License: CC BY 4.0 (verified on the Crossref record for the article, license
        URL creativecommons.org/licenses/by/4.0/, content-version "vor"; the
        supplementary data sheet carries the article's licence)
Item text: NOT shipped. The `.xlsx` has no label level at all -- the column
        names are bare mnemonics (`SCSQ1`, `HADS1`) -- and the deposit ships no
        codebook, so both levels were checked and neither exists. The two
        instruments are third-party (the SCSQ, Xie 1998; the HADS, Zigmond &
        Snaith 1983) and neither had a register row to consult for wording that
        is not in hand anyway. Where to look: the article names both
        instruments but does not reproduce their items.

**The 64-item EDI block does NOT ship, and the article is what rules it out.**
The file stores `EDI1`..`EDI64` as 0-3, with 24,435 of its 41,344 cells (59%)
equal to 0. The article's own Measures section says the EDI's "response options
scored 0-5". A block whose source describes a six-point administration and
whose file holds four values has been transformed -- this is the EDI's standard
collapse, where the three non-symptomatic responses all become 0 -- and the
administered response is not recoverable from it. That is the same defect found
in `uzdil_2023_soc13` this batch, caught there by the file's own value labels
and here by the article's text.

The two blocks that DO ship were checked the same way and pass:
  * `SCSQ1`..`SCSQ20`: the article says "Scores 0 (never) to 3 (always)", and
    the file holds 0-3. Native.
  * `HADS1`..`HADS14`: the article does not state the scale, but the HADS is
    administered 0-3 universally and the file holds 0-3. Consistent.

**Four single out-of-range cells are data-entry errors, and each costs one
respondent one table.** `SCSQ2` and `SCSQ12` each have exactly one cell at 4
against a 0-3 scale, `HADS14` one at 4, and `EDI64` one at 7. Four different
respondents, one stray cell each, every other cell of those rows in range --
isolated to a single cell in a single item, which is a data-entry error and not
a second scale (a second scale would show across many respondents). Each
affected respondent is dropped from the table containing the stray cell, not
merely the cell, on the same reasoning as `aspell_2019_*`: a row that is wrong
once is not trusted elsewhere in that block.

**`cluster_id` is the school and it is very unbalanced -- deliberately kept
anyway.** The eight schools hold 381, 152, 67, 32, 11, 1, 1 and 1 students.
Three singleton clusters contribute nothing to a multilevel fit, but they are
what the deposit says, and dropping or merging them would be inventing a design
the source does not have. The imbalance is recorded here and in the dictionary
row so a user meets it in the documentation rather than in their output. The
column holds bare codes 0-7 with no school names anywhere in the file, so
nothing identifying travels with it.

`hometown` is dropped: it is a binary urban/rural origin code, i.e. a
geographic code, under the 2026-10-20 ruling.

Dropped as derived: `DT`, `BD`, `bulimia`, `perfectionism`, `ID`, `MF`, `IA`,
`inefficiency` and `EDItotal` are the EDI's eight subscale scores and its
total; `SCSQadaptivecoping`, `SCSQmaladaptivecoping`, `totalcoping`,
`HADSAtotal` and `HADSDtotal` are scores; `Zadaptivecoping`,
`Zmaladaptivecoping` and `ZscoreDepression` are their z-transformations; and
`DTgroup`, `HADSanxietygroup` and `HADSdepressiongroup` are cutpoint bandings.

PII: none. Every column is numeric, there is no identifier (`id` is the row
index), and no name, date, free-text or school-name column; the screen below
prints its denominator.

Output: two tables, 21,910 responses -- 646 respondents, 34 items.
  * zheng_2020_scsq -- 20 items, resp 0-3
  * zheng_2020_hads -- 14 items, resp 0-3
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Data_Sheet_1.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

PERMITTED = [0, 1, 2, 3]

BLOCKS = {
    "zheng_2020_scsq": ("SCSQ", 20),
    "zheng_2020_hads": ("HADS", 14),
}
# Not shipped. The count is asserted so that a change in the file is noticed.
EDI_N = 64

COV_MAP = {
    "age": "cov_age",
    "grade": "cov_grade",
    "majors": "cov_major",
}

DROP = {
    "hometown": "a binary urban/rural origin code -- a geographic code, "
                "dropped under the 2026-10-20 ruling",
    "DT": "EDI subscale score (drive for thinness)",
    "BD": "EDI subscale score (body dissatisfaction)",
    "bulimia": "EDI subscale score",
    "perfectionism": "EDI subscale score",
    "ID": "EDI subscale score (interoceptive deficits)",
    "MF": "EDI subscale score (maturity fears)",
    "IA": "EDI subscale score (interpersonal distrust/awareness)",
    "inefficiency": "EDI subscale score",
    "EDItotal": "EDI total score",
    "SCSQadaptivecoping": "SCSQ positive-coping score",
    "SCSQmaladaptivecoping": "SCSQ negative-coping score",
    "totalcoping": "SCSQ composite",
    "HADSAtotal": "HADS anxiety score",
    "HADSDtotal": "HADS depression score",
    "Zadaptivecoping": "z-transformed subscale score",
    "Zmaladaptivecoping": "z-transformed subscale score",
    "ZscoreDepression": "z-transformed subscale score",
    "DTgroup": "cutpoint banding of a score",
    "HADSanxietygroup": "cutpoint banding of a score",
    "HADSdepressiongroup": "cutpoint banding of a score",
}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; dtypes present: "
          f"{sorted({str(t) for t in df.dtypes})}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected text column(s): {text_cols}"


def main() -> None:
    df = pd.read_excel(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 646, len(df)

    edi = [f"EDI{i}" for i in range(1, EDI_N + 1)]
    assert all(c in df.columns for c in edi), "the EDI block moved"
    cells = int(df[edi].notna().sum().sum())
    zeros = int((df[edi] == 0).sum().sum())
    print(f"NOT SHIPPING the EDI block ({EDI_N} items): the file holds "
          f"{sorted(int(v) for v in pd.unique(df[edi].values.ravel()))} with "
          f"{zeros} of {cells} cells ({100 * zeros / cells:.0f}%) equal to 0, "
          "but the ARTICLE says the EDI's 'response options scored 0-5'. Six "
          "administered points stored as four means the block is the EDI's "
          "standard 0-3 collapse, and the administered response is not "
          "recoverable. See the module docstring.")

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    df["cluster_id"] = df["school"].astype(int)
    sizes = df["cluster_id"].value_counts().sort_index()
    print(f"cluster_id is the school: {df['cluster_id'].nunique()} clusters, "
          f"sizes {list(sizes)} -- VERY unbalanced, including three "
          "singletons, kept as the deposit has them rather than merged")

    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    item_cols = {}
    for table, (prefix, n) in BLOCKS.items():
        cols = [f"{prefix}{i}" for i in range(1, n + 1)]
        assert all(c in df.columns for c in cols), (table, cols)
        item_cols[table] = cols

    accounted = (set(COV_MAP) | set(covs) | set(DROP) | set(edi)
                 | {"id", "cluster_id", "school"})
    accounted |= {c for cs in item_cols.values() for c in cs}
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in DROP.items():
        print(f"skipped column {c}: {why}")

    for table, cols in item_cols.items():
        write(df, table, cols, covs)


def write(df: pd.DataFrame, table: str, cols: list, covs: list) -> None:
    vals = df[cols].to_numpy(dtype=float)
    oob = ~pd.isna(vals) & ~pd.Series(vals.ravel()).isin(PERMITTED).to_numpy(
        ).reshape(vals.shape)
    tainted = oob.any(axis=1)
    if tainted.any():
        where = {cols[j]: int(vals[i, j])
                 for i, j in zip(*oob.nonzero())}
        print(f"{table}: {int(oob.sum())} out-of-range cell(s) {where} in "
              f"{int(tainted.sum())} respondent(s) -- a single stray cell in "
              "one item each, i.e. data-entry error; those respondents are "
              "dropped from this table")

    keep = df.loc[~tainted, ["id", "cluster_id"] + covs + cols]
    long = keep.melt(id_vars=["id", "cluster_id"] + covs, var_name="item",
                     value_name="resp")
    long = long.dropna(subset=["resp"])
    outside = ~long["resp"].isin(PERMITTED)
    assert not outside.any(), (table, sorted(long.loc[outside, "resp"].unique()))

    long["item"] = [c.lower() for c in long["item"]]
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "cluster_id"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=PERMITTED)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"  -> {table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
