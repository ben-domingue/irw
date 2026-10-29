"""
Intercultural sensitivity and five-factor personality in 1,218 Turkish
preservice teachers.

Source: Aksin, A. (2023). Intercultural Sensitivity DataSet [Dataset].
        Mendeley Data, V1. "This study aims at examining the relationships
        between the five-factor personality traits of preservice teachers and
        their intercultural sensitivity."
DOI: 10.17632/yxpj8h384j.1
Data: https://data.mendeley.com/datasets/yxpj8h384j (IS.sav)
License: CC BY 4.0 (verified on the Mendeley Data record)
Item text: NOT shipped. BOTH label levels were checked and both are empty:
        `column_names_to_labels` is blank for every one of the 64 variables and
        `variable_value_labels` carries exactly one entry, for the covariate
        `bölüm` (department). So the file documents nothing about either block's
        wording. Where the text actually is: the KDÖ block is the Turkish
        adaptation of Chen & Starosta's (2000) Intercultural Sensitivity Scale
        and the BFKÖ block a 30-item Turkish five-factor inventory; recovering
        either means finding the adaptation paper, and a translated adaptation
        then raises the rights question itemtext_standard.md's 2026-09-08 ruling
        covers. That is a paper hunt plus a register ruling, not a cheap-gate
        extraction.

Two things about this file had to be established rather than assumed, and both
are checked in the code below:

1. **The `R`-suffixed columns are ALREADY reverse-scored**, so `resp` runs one
   direction throughout and the table is not `resp_ambiguous`. Evidence: every
   one of the 23 KDÖ items, the ten R-suffixed ones included, correlates
   POSITIVELY with the block total (lowest 0.253, every R item between 0.339 and
   0.587). If the R columns held raw responses awaiting reversal, they would
   correlate negatively.

2. **`BFKÖ3` is a leftover UNREVERSED duplicate of `BFKÖ3R`, not a 31st item,
   and is dropped.** The block is numbered 1-30 but ships 31 columns, with two
   called "3". `BFKÖ3 == 8 - BFKÖ3R` on all 1,217 rows where both are integers,
   exactly; and `BFKÖ3` is the single column in the block that correlates
   negatively with the block total. Keeping both would ship one item twice, once
   backwards.

Imputed cells are dropped. 419 of the 77,952 cells (0.5%) hold non-integer
values on 1-5 and 1-7 integer scales, spread over 54 columns -- a fractional
value in a Likert column is an imputation until proven otherwise, and these are
not a single column mean (they differ cell by cell), so they are a model-based
fill. Every non-integer cell is dropped rather than rounded; the integer cells
are the observed responses.

PII: none. The screen below prints its denominator. The file has no string
column at all; `Yaş` is an age in years (3 of its cells are themselves imputed
and dropped from the covariate), there is no name, email, date of birth, phone,
identifier or geographic code.

Output: two tables, 63,757 responses.
  * aksin_2023_intercultural_sensitivity -- 23 items, resp 1-5
  * aksin_2023_big_five                  -- 30 items, resp 1-7
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("IS.sav")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

COV_MAP = {
    "Cinsiyet": "cov_gender",
    "Yaş": "cov_age",
    "Sınıf": "cov_year_of_study",
    "bölüm": "cov_department",
}

# Block prefix -> (output table, item count after the duplicate is dropped).
BLOCKS = {
    "KDÖ": ("aksin_2023_intercultural_sensitivity", 23),
    "BFKÖ": ("aksin_2023_big_five", 30),
}

# The unreversed duplicate established in the docstring.
DUPLICATE = "BFKÖ3"

# Deposit-computed totals, dropped.
TOTALS = ["UYUMLULUK", "DISADONUK", "SORUMLULUK", "DUYGUSALDENGE",
          "DENEYIMACIKLIK", "KDÖ_TOPLAM"]


def code(col: str) -> str:
    """Item code from the source column name, reversibly: lowercase and
    transliterate the Turkish Ö, keeping the R that marks a reverse-scored
    column. KDÖ12R -> kdo12r, BFKÖ3R -> bfko3r. Never a positional index.
    """
    return col.replace("Ö", "O").replace("ö", "o").lower()


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    for banned in ("ad", "isim", "name", "email", "mail", "tel", "tc",
                   "adres", "address", "dogum", "birth"):
        bad = [c for c in df.columns if c.lower() == banned]
        assert not bad, f"possible identifier column: {bad}"


def main() -> None:
    df, meta = pyreadstat.read_sav(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 1218, len(df)
    print(f"variable labels present: "
          f"{sum(1 for c in df.columns if (meta.column_names_to_labels.get(c) or '').strip())}"
          f"; value-labelled variables: {sorted(meta.variable_value_labels)}")

    blocks = {}
    for prefix, (table, n) in BLOCKS.items():
        cols = [c for c in df.columns
                if c.startswith(prefix) and c not in TOTALS
                and c != DUPLICATE]
        assert len(cols) == n, (prefix, len(cols), n, cols)
        blocks[prefix] = cols

    # 1. R-suffixed columns are already reverse-scored.
    for prefix, cols in blocks.items():
        ints = df[cols].where(df[cols] % 1 == 0)
        total = ints.sum(axis=1)
        rs = {c: ints[c].corr(total) for c in cols}
        worst = min(rs.values())
        neg = [c for c, r in rs.items() if r <= 0]
        assert not neg, (f"{prefix}: these columns correlate negatively with "
                         f"the block total, so the block mixes scoring "
                         f"directions: {neg}")
        print(f"{prefix}: all {len(cols)} items correlate positively with the "
              f"block total (lowest {worst:.3f}), including the "
              f"{sum(c.endswith('R') for c in cols)} R-suffixed ones -- the "
              f"block is already reverse-scored")

    # 2. The duplicate is the unreversed copy of BFKÖ3R.
    both = (df["BFKÖ3"] % 1 == 0) & (df["BFKÖ3R"] % 1 == 0)
    assert ((8 - df.loc[both, "BFKÖ3R"]) == df.loc[both, "BFKÖ3"]).all()
    print(f"skipped column BFKÖ3: equals 8 - BFKÖ3R on all {both.sum()} rows "
          "where both are integers, i.e. the unreversed duplicate of the same "
          "item, not a 31st item")
    for c in TOTALS:
        print(f"skipped column {c}: deposit-computed scale or subscale total")

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        col = df[src]
        df[dst] = col.where(col % 1 == 0)   # drop imputed covariate cells too
    covs = list(COV_MAP.values())

    accounted = (set(COV_MAP) | set(covs) | set(TOTALS) | {DUPLICATE, "id"}
                 | {c for cols in blocks.values() for c in cols})
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"

    for prefix, cols in blocks.items():
        table, _n = BLOCKS[prefix]
        codes = {c: code(c) for c in cols}
        assert len(set(codes.values())) == len(cols), codes
        long = df[["id"] + covs + cols].rename(columns=codes)
        long = long.melt(id_vars=["id"] + covs, var_name="item",
                         value_name="resp")
        before = long["resp"].notna().sum()
        long = long[long["resp"].notna() & (long["resp"] % 1 == 0)]
        print(f"{table}: dropped {before - len(long)} imputed (non-integer) "
              f"cell(s) of {before}")
        write(long, table, covs)


def write(long: pd.DataFrame, table: str, covs: list) -> None:
    long = long.copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long)
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
