"""
99 of the 100 IPIP Big Five Factor Markers, answered by 114,016 SAPA-Project
participants between 4 April 2006 and 18 August 2010.

Source: Condon, D. M., & Revelle, W. Selected personality data from the
        SAPA-Project: 04Apr2006 to 18Aug2010 [Data set]. Harvard Dataverse.
DOI: 10.7910/DVN/H9RQD6
Data: https://doi.org/10.7910/DVN/H9RQD6 (files
        "sapaTempICARData04apr2006thru18aug2010.RData" and
        "background info and demographic codes.txt")
License: CC0 1.0 (verified on the Dataverse record, latestVersion.license.name)
Item text: NOT shipped, and this is a partial-coverage case rather than an
        absent-text one. The items are the IPIP Big Five Factor Markers
        (Goldberg 1999), which are public domain, but the tie from SAPA's own
        `q_###` codes to the item wording is not in this deposit. The sibling
        annual deposits publish an `ItemInfo.csv`, and it covers only 23 of
        these 99 codes (it is the later 135-item bank). Shipping 23 of 99
        would leave 76 items with blank text, which the item-set gate
        forbids. Where the rest is: the deposit's own codebook names an
        `IPIPitemLists.rdata` as an accompanying file, but the deposit
        publishes only three files and that is not one of them; SAPA's item
        dictionaries also ship with the R `psych` package. Both are one hop
        off-source, so this is a later pass.

**This is a different window from the two SAPA tables IRW already holds**, and
the check was made before writing rather than after: `sapa-personality.R`
covers 2013-12-08 to 2014-07-26 (the 696-item pool) and
`condon_2024_sapa_personality.py` pools the seven annual releases from
2017-02-07 to 2024-01-12 (the 135-item bank). This deposit is 2006-2010 on the
IPIP-100, so neither the respondents nor the item set overlap them.

**Planned missingness is the design, not attrition.** SAPA administers a random
subset of the item bank to each participant: 5,505,442 of the 11,287,584
possible cells are answered, a median of 48 items per respondent. Every item is
answered by tens of thousands of people.

Response scale is the IPIP 6-point accuracy scale, documented in the deposit's
codebook: 1 very inaccurate, 2 moderately inaccurate, 3 slightly inaccurate,
4 slightly accurate, 5 moderately accurate, 6 very accurate. The observed
values are exactly 1-6.

`id` is the row index, not the deposit's `RID`. RID is described in the
codebook as "generated randomly for each participant" and carries no meaning;
the row index links a respondent across this table and has no preimage.

PII: none. The file holds `RID`, `gender`, `age` and 99 item columns; `age` is
a banded label ("18andUnder" .. "60andOver"), not a date of birth. The screen
below prints its denominator.

Output: one table, 5,505,442 responses -- 114,016 respondents, 99 items,
resp 1-6.
  * condon_2010_sapa_ipip
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd
import pyreadr

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "sapaTempICARData04apr2006thru18aug2010.RData")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

TABLE = "condon_2010_sapa_ipip"
PERMITTED = [1, 2, 3, 4, 5, 6]
COV_MAP = {"gender": "cov_gender", "age": "cov_age"}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert text_cols, "no string columns selected -- screen is not working"
    # Both string columns are banded demographic labels, neither an identifier.
    assert set(text_cols) <= {"gender", "age"}, text_cols


def main() -> None:
    obj = pyreadr.read_r(str(SRC))
    (name, df), = obj.items()
    print(f"loaded {name}: {df.shape}")
    pii_screen(df)
    assert len(df) == 114016, len(df)

    items = sorted((c for c in df.columns if re.fullmatch(r"q_\d+", c)),
                   key=lambda c: int(c.split("_")[1]))
    assert len(items) == 99, len(items)

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    accounted = set(COV_MAP) | set(covs) | set(items) | {"id"}
    leftover = [c for c in df.columns if c not in accounted]
    assert leftover == ["RID"], leftover
    print("skipped RID -- a randomly generated participant code with no "
          "meaning; id is the row index instead")

    long = df[["id"] + covs + items].melt(
        id_vars=["id"] + covs, var_name="item", value_name="resp")
    before = len(long)
    long = long[long["resp"].notna()]
    print(f"planned missingness: {len(long):,} answered of {before:,} possible "
          f"cells ({len(long) / before:.1%}); median per respondent "
          f"{int(df[items].notna().sum(axis=1).median())} items")

    long["resp"] = long["resp"].astype(int)
    outside = sorted(set(long["resp"].unique()) - set(PERMITTED))
    assert not outside, f"resp outside {PERMITTED}: {outside}"

    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=PERMITTED)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:170]}")
    long.to_csv(OUT / f"{TABLE}.csv", index=False)
    print(f"  -> {TABLE}: rows={len(long):,} ids={long['id'].nunique():,} "
          f"items={long['item'].nunique()} "
          f"resp={min(long['resp'])}-{max(long['resp'])}")


if __name__ == "__main__":
    main()
