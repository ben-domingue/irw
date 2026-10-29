"""
Morality, self-efficacy, achievement goals, passion and doping attitudes in 196
Brazilian individual-sport athletes.

Source: Codonhato, R. (2025). Doping attitudes in Brazilian athletes dataset
        [Dataset]. figshare. The deposit's own description: "This study
        examined the relationships between morality, self-efficacy,
        achievement goals, passion, and doping attitudes among 196 Brazilian
        athletes from individual sports."
DOI: 10.6084/m9.figshare.29959520.v1
Data: https://doi.org/10.6084/m9.figshare.29959520.v1 ("data.xlsx")
License: CC BY 4.0 (verified on the figshare record, license.name "CC BY 4.0")
Item text: NOT shipped. The deposit is a bare `.xlsx` -- a format with no
        variable or value label level at all, so neither was missed -- its item
        columns are `PS1..MR13`, and it ships no codebook. The five CONSTRUCTS
        are named (below) but no published instrument is, so there is nothing
        to check a rights register against. One lead for a later pass: the
        17-item 1-6 doping block is the shape of the Performance Enhancement
        Attitude Scale (PEAS, Petróczi), which is worth confirming before
        anything is extracted, because that would make it a third-party
        instrument rather than study-authored. Where the rest is: the record
        cites no article (`resource_doi` is null), so Codonhato's paper on this
        196-athlete sample has to be found first.

**The five tables are the deposit's OWN five constructs, matched to its own
subscale totals -- not an inference from the column prefixes.** The description
names exactly five things, and the file carries a computed total for each one,
which is what ties them to the blocks:

| block | items | scale | construct | the deposit's own total(s) |
|---|---|---|---|---|
| `DP` | 17 | 1-6 | doping attitudes | `DOP` |
| `OM` | 16 | 1-5 | achievement goals | `ORTASK`, `OREGO` (task, ego) |
| `MR` | 13 | 1-5 | morality | `TRAP`, `ANTIDESP`, `VITJUS` |
| `PS` | 12 | 1-5 | passion | `PH`, `PO` (harmonious, obsessive) |
| `AE` |  9 | 1-5 | self-efficacy | `AUTOEF` |

The Portuguese total names are what make the mapping readable: `AUTOEF` is
autoeficácia, `ORTASK`/`OREGO` task and ego orientation, `PH`/`PO` paixão
harmoniosa and obsessiva -- and 12 passion items splitting 6/6 is the Passion
Scale's own shape. Item codes keep the source names so a user can take the
subscales from the prefix.

`DATASET` (1 or 2) distinguishes two samples and ships as `cov_dataset`, which
is the "same instrument across samples" rule already satisfied: the deposit
delivers them as one file over one id space, so they stay one file.

PII: none. Every column is numeric, there is no identifier, name, date,
free-text or geographic column, and no missing data anywhere. The screen below
prints its denominator.

Output: five tables, 13,132 responses -- 196 athletes, no missing data.
  * codonhato_2025_doping_attitudes  -- 17 items, resp 1-6
  * codonhato_2025_achievement_goals -- 16 items, resp 1-5
  * codonhato_2025_morality          -- 13 items, resp 1-5
  * codonhato_2025_passion           -- 12 items, resp 1-5
  * codonhato_2025_self_efficacy     --  9 items, resp 1-5
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

# table -> (prefix, item count, permitted set, the deposit's own total columns)
BLOCKS = {
    "codonhato_2025_doping_attitudes": ("DP", 17, [1, 2, 3, 4, 5, 6], ["DOP"]),
    "codonhato_2025_achievement_goals": ("OM", 16, [1, 2, 3, 4, 5],
                                         ["ORTASK", "OREGO"]),
    "codonhato_2025_morality": ("MR", 13, [1, 2, 3, 4, 5],
                                ["TRAP", "ANTIDESP", "VITJUS"]),
    "codonhato_2025_passion": ("PS", 12, [1, 2, 3, 4, 5], ["PH", "PO"]),
    "codonhato_2025_self_efficacy": ("AE", 9, [1, 2, 3, 4, 5], ["AUTOEF"]),
}

COV_MAP = {
    "Idade": "cov_age",
    "Sexo": "cov_sex",
    "Modalidade": "cov_sport",
    "Experiencia": "cov_experience_months",
    "TreinamentoHSem": "cov_training_hours_per_week",
    "Salario": "cov_paid_athlete",
    "Nivel": "cov_competitive_level",
    "DATASET": "cov_dataset",
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
    assert len(df) == 196, len(df)

    cols = {}
    totals = []
    for table, (prefix, n, _p, tots) in BLOCKS.items():
        cs = [f"{prefix}{i}" for i in range(1, n + 1)]
        assert all(c in df.columns for c in cs), (table, cs)
        cols[table] = cs
        for t in tots:
            assert t in df.columns, t
        totals += tots
        print(f"{table}: {prefix}1..{prefix}{n}, {n} items; the deposit's own "
              f"total(s) for this construct: {', '.join(tots)}")

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    accounted = (set(COV_MAP) | set(covs) | set(totals) | {"id"}
                 | {c for cs in cols.values() for c in cs})
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    print(f"skipped {len(totals)} depositor-computed subscale total(s): "
          f"{totals}")

    for table, cs in cols.items():
        permitted = BLOCKS[table][2]
        codes = {c: c.lower() for c in cs}
        assert len(set(codes.values())) == len(cs), codes
        long = df[["id"] + covs + cs].rename(columns=codes)
        long = long.melt(id_vars=["id"] + covs, var_name="item",
                         value_name="resp")
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
