"""
Problematic TikTok use, depression, social anxiety, boredom proneness and
distress intolerance in Chinese adults (two waves, ~5 weeks apart).

Source: Yao, N., Chen, J., Huang, S., et al. "Depression and social anxiety in
        relation to problematic TikTok use severity: The mediating role of
        boredom proneness and distress intolerance."
DOI: 10.5281/zenodo.7726855
Data: https://zenodo.org/records/7726855 (data20221211.sav)
License: CC BY 4.0 (verified on the Zenodo record, metadata.license = cc-by-4.0)
Item text: not shipped — the .sav carries no variable labels at all
        (meta.column_names_to_labels is None for every item column); value
        labels exist only for Sex/Educate/UseTime and the four TikTok-activity
        items. Item stems would have to come from the published scales
        (problematic-use 10 items, PHQ-9, a 19-item social anxiety measure,
        8-item boredom proneness, 10-item distress intolerance), which is not
        "already in hand" per Step 3.5.

Output: six response tables, one per instrument. Waves 1 and 2 of the same
instrument go in one file with `wave`; item codes are harmonised so that
wave-2 column `Add2_3` ships as item `Add3`, same as wave 1.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data20221211.sav")
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

COV_MAP = {"Sex": "cov_sex", "Age": "cov_age", "Educate": "cov_educ"}

# instrument -> (wave-1 prefix, wave-2 prefix, n items, table name)
SCALES = [
    ("Add",  "Add2_",  10, "yao_2023_tiktok_problem_use"),
    ("Dep",  "Dep2_",   9, "yao_2023_depression"),
    ("Anx",  "Anx2_",  19, "yao_2023_social_anxiety"),
    ("Bore", "Bore2_",  8, "yao_2023_boredom_proneness"),
    ("DT",   "DT2_",   10, "yao_2023_distress_intolerance"),
]
# Four frequency-of-use items sharing one 1-5 never..very often scale,
# administered at wave 1 only.
ACTIVITY = ["WatchSV", "MakeSV", "WatchLS", "MakeLS"]

# Person-level composites (means across the items above) — not responses.
AGG = ["Addict1", "Depress1", "Anxiety1", "Boredom1", "DIT1",
       "Addict2", "Depress2", "Anxiety2", "Boredom2", "DIT2"]


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    # No string columns at all in this .sav: every column is numeric coded.
    assert not text_cols, f"unexpected free-text columns: {text_cols}"


def long_block(df: pd.DataFrame, cols: list[str], items: list[str],
               wave: int, covs: list[str]) -> pd.DataFrame:
    sub = df[["id"] + covs + cols].copy()
    sub = sub.rename(columns=dict(zip(cols, items)))
    out = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    out["wave"] = wave
    return out


def main() -> None:
    df, meta = pyreadstat.read_sav(str(SRC))
    print("raw shape", df.shape)
    pii_screen(df)

    df = df.rename(columns={"Num": "id"})
    df["id"] = df["id"].astype(int)
    assert df["id"].is_unique, "Num is not one row per person"
    for src, dst in COV_MAP.items():
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    used: set[str] = {"Num", "id"} | set(COV_MAP) | set(covs)
    written: set[str] = set()

    for p1, p2, n, table in SCALES:
        w1 = [f"{p1}{i}" for i in range(1, n + 1)]
        w2 = [f"{p2}{i}" for i in range(1, n + 1)]
        for c in w1 + w2:
            assert c in df.columns, c
        used.update(w1 + w2)
        long = pd.concat([
            long_block(df, w1, w1, 1, covs),
            long_block(df, w2, w1, 2, covs),
        ], ignore_index=True)
        write(long, table, OUT, written)

    for c in ACTIVITY:
        assert c in df.columns, c
    used.update(ACTIVITY)
    act = long_block(df, ACTIVITY, ACTIVITY, 1, covs)
    write(act, "yao_2023_tiktok_use_frequency", OUT, written)

    # Balance the books.
    skipped = {
        **{c: "person-level composite (mean of the item columns above)"
           for c in AGG},
        "UseTime": "banded daily-use duration, not an item on a shared scale",
        "dropout": "attrition flag; equivalent to wave-2 responses being "
                   "missing, which the long tables already carry",
    }
    used.update(skipped)
    leftover = [c for c in df.columns if c not in used]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in skipped.items():
        print(f"skipped column {c}: {why}")


def write(long: pd.DataFrame, table: str, out: Path, written: set[str]) -> None:
    assert table not in written, f"duplicate output name {table}"
    written.add(table)
    long = long.dropna(subset=["resp"]).copy()
    long["resp"] = long["resp"].astype(float)
    frac = long["resp"] % 1 != 0
    assert not frac.any(), "fractional Likert values (imputation?)"
    long["resp"] = long["resp"].astype(int)
    wave_cols = ["wave"] if long["wave"].nunique() > 1 else []
    cols = ["id", "item", "resp"] + wave_cols + [c for c in long.columns
                                                 if c.startswith("cov_")]
    long = long[cols].sort_values(["id"] + wave_cols + ["item"])
    path = out / f"{table}.csv"
    _checks = run_qc(long)
    _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
    assert not _fails, (table, _fails)
    for _c in _checks:
        if _c.status == "warn":
            print(f"  [qc warn] {table} {_c.name}: {_c.detail[:180]}")
    long.to_csv(path, index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
