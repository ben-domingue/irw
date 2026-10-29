"""
Three instruments answered by 329 US college students: the Intolerance of
Uncertainty Scale-12, the Smartphone Addiction Scale-Short Version and the
Social Phobia Inventory.

Source: Elhai, J. (2025). Intolerance of uncertainty mediates the relationship
        between social anxiety and problematic smartphone use severity in
        college students [Dataset]. Mendeley Data.
DOI: 10.17632/sp3h5k27xk.1
Data: https://data.mendeley.com/datasets/sp3h5k27xk (AlavinikooData.xlsx,
        sheet "Repository")
License: CC BY 4.0 (verified on the DataCite record's rightsList, "Creative
        Commons Attribution 4.0 International")
Item text: NOT shipped here, and each of the three is decided differently --
        the deposit itself names all three instruments in its description, so
        there is no identification work left, only rights:
          * `sas1..sas10` -- the Smartphone Addiction Scale-Short Version. Its
            items are published VERBATIM by the originators under CC BY:
            Kwon, Kim, Cho & Yang (2013), PLoS ONE 8(12):e83558, licence
            "cc by" per Europe PMC, items in its Table 1. This batch wrote the
            SAS-SV's first register row as `ship` on that basis, so this table
            is extractable in a later pass; it is not done here because the
            article's Table 1 is the 33-item content-validity pool and which
            ten became the short version has to be read off the paper rather
            than guessed.
          * `iu1..iu12` -- the Intolerance of Uncertainty Scale-12. The
            register already carries the 27-item IUS as `block`, and a short
            form of a blocked longer form is itself blocked (2026-10-17 ruling
            on the BFI-10). A row recording that derivation went in with this
            batch.
          * `spin1..spin17` -- the Social Phobia Inventory. No register row and
            no originator terms located; recorded as owed rather than guessed.

The three blocks are three tables because they are three separate published
instruments on three different response scales (1-5, 1-6, 0-4), not subscales
of one battery.

`id` is the row index, not the deposit's own column. The deposit describes its
`id` as "an identification variable that we used in our project, consecutively
numbering participants", but the values are seven digits (8615187, 8615191) --
i.e. survey-platform response ids rather than a 1..329 counter -- so the row
index replaces it.

PII: none. Every column is numeric, and apart from the id there is no
identifier, name, date, free-text or geographic column. The screen below prints
its denominator.

Output: three tables, 12,668 responses.
  * elhai_2025_social_phobia           -- 17 items, resp 0-4
  * elhai_2025_intolerance_uncertainty -- 12 items, resp 1-5
  * elhai_2025_smartphone_addiction    -- 10 items, resp 1-6
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("AlavinikooData.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

SHEET = "Repository"

# Each block's permitted set is the published instrument's own, not the
# observed values: the IUS-12 is 1-5, the SAS-SV 1-6, the SPIN 0-4.
BLOCKS = {
    "elhai_2025_intolerance_uncertainty": (
        [f"iu{i}" for i in range(1, 13)], [1, 2, 3, 4, 5]),
    "elhai_2025_smartphone_addiction": (
        [f"sas{i}" for i in range(1, 11)], [1, 2, 3, 4, 5, 6]),
    "elhai_2025_social_phobia": (
        [f"spin{i}" for i in range(1, 18)], [0, 1, 2, 3, 4]),
}

COV_MAP = {"age": "cov_age", "sex": "cov_sex"}

DROP = {
    "id": "a seven-digit survey-platform response id, replaced by the row index",
    "iu_total": "depositor-computed IUS-12 total",
    "sas_total": "depositor-computed SAS-SV total",
    "spin_total": "depositor-computed SPIN total",
}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; dtypes present: "
          f"{sorted({str(t) for t in df.dtypes})}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected text column(s): {text_cols}"


def main() -> None:
    df = pd.read_excel(SRC, sheet_name=SHEET)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 329, len(df)

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    accounted = (set(COV_MAP) | set(covs) | set(DROP) | {"id"}
                 | {c for cols, _p in BLOCKS.values() for c in cols})
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in DROP.items():
        print(f"skipped column {c}: {why}")

    for table, (cols, permitted) in BLOCKS.items():
        assert all(c in df.columns for c in cols), (table, cols)
        long = df[["id"] + covs + cols].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp")
        before = long["resp"].notna().sum()
        long = long[long["resp"].isin(permitted)]
        assert before == len(long), \
            f"{table}: {before - len(long)} cell(s) outside {permitted}"
        write(long, table, covs, permitted)


def write(long: pd.DataFrame, table: str, covs: list, permitted: list) -> None:
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
