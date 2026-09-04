#!/usr/bin/env python3
"""Christensen, Kenett, Aste, Silvia & Kwapil (2018), Behavior Research Methods --
Wisconsin Schizotypy Scales-Short Forms (WSS-SF), two independent samples.

Source: https://osf.io/c6rqy/
Article: https://link.springer.com/article/10.3758/s13428-018-1032-9
DOI: 10.3758/s13428-018-1032-9
License: CC0 1.0 Universal (stated on the OSF node, checked 2026-09-04)
Issue: #307

Four subscales, 15 dichotomous (0/1) items each, 60 items per respondent:

    py  Physical Anhedonia
    pb  Perceptual Aberration
    mi  Magical Ideation
    sa  Social Anhedonia

**The subscale mapping is not guessed.** The short-form prefixes are not the
ones the full-length Chapman scales use, so they were resolved against the
companion long-form file rather than from the abbreviations.
`share_2171n_WSS-SF.sav` carries variable labels on its four total-score
columns -- `ph_tot` "PhyAnh total", `bi_tot` "PerAb total", `mi_tot` "Magic
total", `sa_tot` "SocAnh total" -- which fixes `ph`=Physical Anhedonia and
`bi`=Perceptual Aberration in the long-form file; every short-form `py*`
column then matches a `ph*` column and every `pb*` column a `bi*` column,
value for value (see below). Hence py->ph (Physical Anhedonia) and pb->bi
(Perceptual Aberration).

Two tables ship, one per sample:

  christensen_2018_wsssf_2171   2,171 respondents, with cov_sex and cov_ethnic
  christensen_2018_wsssf_5831   5,831 respondents, no covariates

**The 2,171 sample's covariates are attached by row position, and that is
safe here but only because it is checked.** `WSS-SF_2171.csv` ships the 60
item columns and *nothing else* -- no subject number, no key of any kind --
so there is no column to merge on; the covariates live in a separate file,
`share_2171n_WSS-SF.csv`, which has `subjnumb`, `sex`, `ethnic` and the
full-length scales. Equal row counts alone would not establish that the two
files are in the same order, so `_assert_row_alignment` proves it instead:
each of the 60 short-form columns is a verbatim copy of one full-length
column, so if the files agreed in length but not in order, no short-form
column would match any long-form column. All 60 match, and each matches
exactly one, across all 2,171 rows. The check runs on every build; if a
future revision of either file reorders rows, it fails loudly rather than
silently pairing respondents with other people's demographics.

`subjnumb` is used as `id` and is verified unique (2,171 distinct, no nulls).
`sex` and `ethnic` are numeric codes in the CSV; the codings are recovered
from the value labels in the matching `.sav` (sex 1=male 2=female; ethnic
1=caucasian 2=Afr-Am 3=Hispanic 4=Asian 5=Nat Am 6=other) and applied, so the
shipped covariates are strings rather than bare integers. 6 respondents have
no sex and 79 no ethnic; those stay null.

The 5,831 sample has no identifiers in its file either, so `id` is the row
index. Note for anyone revisiting this: `WSS-SF_5831.csv` is a permutation of
the 5,831 complete cases of `share_6137n_WSS-SF.csv` (same 60 items, identical
multiset of response patterns, exact count match), and that companion file
*does* carry sex and ethnic. Covariates are not recovered here because the
permutation cannot be inverted -- 837 of the rows share a response pattern
with at least one other row, so a content-based join is ambiguous for them.
Rebuilding this table from `share_6137n_WSS-SF.csv` directly would sidestep
that and gain both covariates; it would also change the row order.

Subscale membership is an attribute of the item, not of the person, so it
ships as `itemcov_subscale` (datastandard.md, "Item-level covariates").

Item text: not shipped. The deposit carries no item stems -- only five
variable labels in the whole `.sav`, and those are the id and the four total
scores -- and the article does not reproduce the items. The wording is in the
WSS-SF development paper (Winterstein et al.) and the original Chapman scales.

Input files, from https://osf.io/c6rqy/ (folder `Data`):
    WSS-SF_2171.csv           https://osf.io/download/xg3hs/
    share_2171n_WSS-SF.csv    https://osf.io/download/r2xdf/
    share_2171n_WSS-SF.sav    https://osf.io/download/27s93/   (value labels only)
    WSS-SF_5831.csv           https://osf.io/download/xw47t/
Place them in `data/christensen_2018_wsssf_raw/` before running.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
ARCHIVE = BASE / "christensen_2018_wsssf_raw"
OUT = BASE / "christensen_2018_wsssf"


SUBSCALES = {
    "mi": "Magical Ideation",
    "py": "Physical Anhedonia",
    "pb": "Perceptual Aberration",
    "sa": "Social Anhedonia",
}

# Short-form prefix -> the prefix the same subscale uses in the full-length
# companion file. Established from the .sav total-score variable labels; see
# the module docstring.
LONG_FORM_PREFIX = {"py": "ph", "pb": "bi", "mi": "mi", "sa": "sa"}

ITEM_ORDER = (
    [f"mi{i:02d}" for i in range(1, 16)] +
    [f"py{i:02d}" for i in range(1, 16)] +
    [f"pb{i:02d}" for i in range(1, 16)] +
    [f"sa{i:02d}" for i in range(1, 16)]
)

SEX = {1: "male", 2: "female"}
ETHNIC = {1: "caucasian", 2: "Afr-Am", 3: "Hispanic",
          4: "Asian", 5: "Nat Am", 6: "other"}


def _melt_items(wide: pd.DataFrame, id_vars: list[str]) -> pd.DataFrame:
    long = wide.melt(id_vars=id_vars, value_vars=ITEM_ORDER,
                     var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"].unique()) <= {0, 1}, \
        f"items are dichotomous; saw {sorted(long['resp'].unique())}"
    long["itemcov_subscale"] = long["item"].str[:2].map(SUBSCALES)
    assert long["itemcov_subscale"].notna().all(), "unmapped item prefix"
    return long


def _assert_row_alignment(items: pd.DataFrame, companion: pd.DataFrame) -> None:
    """Prove the two files list the same respondents in the same order.

    Each short-form item column is a verbatim copy of one full-length column
    in the companion file, so a shared row order means every short-form column
    matches exactly one long-form column across all rows. Nothing weaker than
    this is available: the item file carries no key to merge on.
    """
    for col in ITEM_ORDER:
        prefix = LONG_FORM_PREFIX[col[:2]]
        candidates = [c for c in companion.columns
                      if c.startswith(prefix) and c[len(prefix):].isdigit()]
        hits = [c for c in candidates
                if (companion[c].values == items[col].values).all()]
        if len(hits) != 1:
            raise RuntimeError(
                f"row alignment check failed for {col}: matched {len(hits)} "
                f"full-length columns ({hits}), expected exactly 1. The two "
                f"files are no longer in the same row order -- do not attach "
                f"covariates by position."
            )


def _report(path: Path, long: pd.DataFrame) -> None:
    cov = [c for c in long.columns if c.startswith("cov_")]
    extra = "".join(f", {c}={sorted(long[c].dropna().unique())}" for c in cov)
    print(f"{path.name}: rows={len(long):,}, ids={long['id'].nunique()}, "
          f"items={long['item'].nunique()}, "
          f"resp_range=[{long['resp'].min()},{long['resp'].max()}]{extra}")


def build_5831() -> None:
    df = pd.read_csv(ARCHIVE / "WSS-SF_5831.csv")
    df["id"] = [f"s5831_{i:04d}" for i in range(1, len(df) + 1)]
    long = _melt_items(df, ["id"])
    long = long[["id", "item", "resp", "itemcov_subscale"]]
    long = long.sort_values(["id", "item"], kind="stable").reset_index(drop=True)
    path = OUT / "christensen_2018_wsssf_5831.csv"
    long.to_csv(path, index=False)
    _report(path, long)


def build_2171() -> None:
    items = pd.read_csv(ARCHIVE / "WSS-SF_2171.csv")
    companion = pd.read_csv(ARCHIVE / "share_2171n_WSS-SF.csv",
                            encoding="utf-8-sig", na_values=[" ", ""])
    if len(items) != len(companion):
        raise RuntimeError(
            f"row mismatch: items={len(items)} companion={len(companion)}")
    _assert_row_alignment(items, companion)

    demo = companion[["subjnumb", "sex", "ethnic"]].rename(
        columns={"subjnumb": "id", "sex": "cov_sex", "ethnic": "cov_ethnic"})
    assert demo["id"].notna().all(), "subjnumb has nulls; cannot be used as id"
    assert demo["id"].nunique() == len(demo), \
        f"subjnumb is not unique: {demo['id'].nunique()} distinct of {len(demo)}"
    demo["cov_sex"] = demo["cov_sex"].map(SEX)
    demo["cov_ethnic"] = demo["cov_ethnic"].map(ETHNIC)

    wide = pd.concat([demo.reset_index(drop=True),
                      items.reset_index(drop=True)], axis=1)
    long = _melt_items(wide, ["id", "cov_sex", "cov_ethnic"])
    long = long[["id", "item", "resp", "cov_sex", "cov_ethnic",
                 "itemcov_subscale"]]
    long = long.sort_values(["id", "item"], kind="stable").reset_index(drop=True)
    path = OUT / "christensen_2018_wsssf_2171.csv"
    long.to_csv(path, index=False)
    _report(path, long)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    build_5831()
    build_2171()


if __name__ == "__main__":
    main()
