"""
Spatial Visualization Ability test: 30 dichotomously scored items
administered to 760 schoolchildren aged 7-16.

Source: Datta, S. (2021). Spatial Visualization Ability test data [Dataset].
        Mendeley Data.
DOI: 10.17632/mp49tfzx4w
Data: https://data.mendeley.com/datasets/mp49tfzx4w (SV_DATA.xlsx)
License: CC BY 4.0 (verified on the Mendeley record, data_licence.short_name =
        "CC BY 4.0")
Item text: not shipped -- a spatial visualization item IS a figure (the
        respondent picks the matching rotated/folded shape), so there is no
        stem to transcribe; the workbook carries codes SVR_1..SVR_30 only and
        no codebook. Both label levels are absent, not unchecked: the file is
        .xlsx, so there are no variable or value labels at all.

Output: one table, 30 items, resp 0/1 (incorrect/correct).
SET_1..SET_4 are the four subtest sums and SVT_TOTAL the test total -- both
person-level composites of the item columns, so neither is shipped.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("SV_DATA.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

TABLE = "datta_2021_spatial_visualization"
ITEMS = [f"SVR_{i}" for i in range(1, 31)]


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    # Numeric throughout: a sequential ID, age in years, the 30 scored items
    # and the composites. No names, no school, no date of birth.
    assert not text_cols, f"unexpected text columns: {text_cols}"


def main() -> None:
    df = pd.read_excel(SRC, sheet_name="Sheet1")
    print("raw shape", df.shape)
    pii_screen(df)

    assert df["ID"].is_unique, "ID is not one row per child"
    df = df.rename(columns={"ID": "id"})
    df["cov_age"] = df["AGE"]

    for c in ITEMS:
        assert c in df.columns, c

    # Balance the books.
    skipped = {
        "AGE": "shipped as cov_age",
        "Unnamed: 32": "empty spacer column between the items and the "
                       "subtest sums (0 non-null values)",
        "SET_1": "subtest-1 sum, a person-level composite of the item columns",
        "SET_2": "subtest-2 sum, a person-level composite of the item columns",
        "SET_3": "subtest-3 sum, a person-level composite of the item columns",
        "SET_4": "subtest-4 sum, a person-level composite of the item columns",
        "SVT_TOTAL": "test total, a person-level composite of the item columns",
    }
    assert df["Unnamed: 32"].notna().sum() == 0, "spacer column is not empty"
    used = set(ITEMS) | {"id", "cov_age"} | set(skipped)
    leftover = [c for c in df.columns if c not in used]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in skipped.items():
        print(f"skipped column {c}: {why}")

    long = df[["id", "cov_age"] + ITEMS].melt(
        id_vars=["id", "cov_age"], var_name="item", value_name="resp")
    write(long, TABLE, OUT)


def write(long: pd.DataFrame, table: str, out: Path) -> None:
    long = long.dropna(subset=["resp"]).copy()
    long["resp"] = long["resp"].astype(float)
    assert not (long["resp"] % 1 != 0).any(), "fractional scores"
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"].unique()) <= {0, 1}, sorted(long["resp"].unique())
    cols = ["id", "item", "resp"] + [c for c in long.columns
                                     if c.startswith("cov_")]
    long = long[cols].sort_values(["id", "item"])
    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:200]}")
    long.to_csv(out / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
