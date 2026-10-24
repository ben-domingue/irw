"""Coarsen `cov_zip` to a 3-digit prefix in friedman_2018_risks_{discrimination,government}.

    python3 friedman_2018_zip3.py OUT_DIR [--check-only]

Two problems in one column, and one change fixes both.

**Disclosure.** The column holds full 5-digit US ZIP codes: 2,634 distinct
values over 3,110 respondents, so ZIP ALONE makes 72.0% of them unique. The
tables publish it beside `cov_age`, `cov_gender`, `cov_race`, `cov_party`,
`cov_hispanic`, `cov_income`, `cov_education` and `cov_state`, in a survey about
perceived discrimination and inequality. Coarsening to the ZIP3 prefix takes
2,634 distinct geographies to 675 and ZIP-alone uniqueness from 72.0% to 5.6%
(median k = 3), which is the same coarsening HIPAA's Safe Harbour applies to
geography, and it leaves the variable usable for regional analysis.

It does NOT make the tables k-anonymous and nothing short of dropping
covariates would: `zip3 + age + gender + race + party` is still 89.3% unique,
and so is `state + age + gender + race + party` at 41.0% -- that residual is a
property of a 3,110-person survey carrying seven demographics, not of the ZIP.
This script fixes the part that is fixable and cheap; the rest is a question
about what the table should publish at all.

**Correctness, independently.** `cov_zip` is served as an integer, so every ZIP
beginning with 0 lost its leading zero: 248 of 3,110 respondents' codes are
published 3 or 4 digits long, and a Massachusetts 02139 reads as 2139. Taking a
prefix of an integer would propagate that error, so the value is zero-padded to
five characters FIRST and the prefix taken from the padded string. `cov_zip3` is
therefore a 3-character string, not a number, and is emitted as one.

WHY THIS IS A REPAIR AND NOT A REBUILD

`data/friedman_2018_risks.do` needs `Risk_Data_Base.dta`, which is not in this
repository, and Stata. So the tables are rebuilt from the PUBLISHED copy, which
is sound here because the change is a pure function of a published column: no
source value is needed to compute a prefix of it. Every other column is carried
through byte-for-byte. The `.do` is patched in the same commit so a future
from-source run produces the same thing rather than reverting this.

`--check-only` reads the live tables and prints the uniqueness arithmetic
without writing anything.
"""
import sys
import json
import urllib.request

import pandas as pd

DATASET = "item_response_warehouse_2"
TABLES = ("friedman_2018_risks_discrimination", "friedman_2018_risks_government")
API = "https://redivis.com/api/v1/tables"


def fetch(table):
    """Whole table, from the published release. 18,660 rows each."""
    url = f"{API}/datapages.{DATASET}.{table}/rows?maxResults=300000"
    with urllib.request.urlopen(url, timeout=600) as r:
        rows = [json.loads(l) for l in r.read().decode().splitlines() if l.strip()]
    df = pd.DataFrame(rows)
    if "cov_zip" not in df.columns:
        raise SystemExit(f"{table}: no cov_zip column -- already repaired?")
    return df


def zip3(series):
    """5-char zero-padded ZIP -> its 3-character prefix, as a string.

    Pad before slicing: the column arrives as an integer and 248 of these have
    lost a leading zero, so slicing the unpadded value would take the wrong
    three digits for every New England and north-eastern respondent.
    """
    s = pd.to_numeric(series, errors="coerce").astype("Int64")
    padded = s.astype("string").str.zfill(5)
    return padded.str[:3].where(s.notna())


def uniqueness(df):
    """k=1 rates on the quasi-identifiers, one row per respondent."""
    p = df.drop_duplicates("id")
    out = {}
    for label, cols in (("zip5", ["cov_zip"]), ("zip3", ["_zip3"]),
                        ("zip5+age+gender", ["cov_zip", "cov_age", "cov_gender"]),
                        ("zip3+age+gender", ["_zip3", "cov_age", "cov_gender"]),
                        ("zip3+age+gender+race+party",
                         ["_zip3", "cov_age", "cov_gender", "cov_race", "cov_party"])):
        if not all(c in p.columns for c in cols):
            continue
        g = p.groupby(cols, dropna=False).size()
        out[label] = ((g == 1).sum(), len(p), int(g.median()))
    return out


def main(argv):
    check_only = "--check-only" in argv
    rest = [a for a in argv if not a.startswith("--")]
    if not check_only and not rest:
        raise SystemExit(__doc__.splitlines()[2].strip())
    out_dir = rest[0] if rest else None

    for table in TABLES:
        df = fetch(table)
        df["_zip3"] = zip3(df["cov_zip"])
        lost = (df.drop_duplicates("id")["cov_zip"].astype(str).str.len() < 5).sum()
        print(f"\n=== {table}: {len(df):,} rows, "
              f"{df['id'].nunique():,} respondents, "
              f"{lost:,} respondents whose published ZIP lost a leading zero")
        for label, (u, n, med) in uniqueness(df).items():
            print(f"    {label:28s} k=1 for {u:5,} of {n:,} = {u / n:5.1%}  median k={med}")
        if check_only:
            continue

        # Replace in place, keeping column order: cov_zip3 sits where cov_zip was.
        cols = [("cov_zip3" if c == "cov_zip" else c) for c in df.columns if c != "_zip3"]
        df = df.rename(columns={"cov_zip": "cov_zip3"})
        df["cov_zip3"] = df["_zip3"]
        df = df[cols]
        assert "cov_zip" not in df.columns
        assert df["cov_zip3"].dropna().str.len().eq(3).all(), "a cov_zip3 value is not 3 chars"
        path = f"{out_dir.rstrip('/')}/{table}.csv"
        df.to_csv(path, index=False)
        print(f"    wrote {path}  ({len(df):,} rows, {len(df.columns)} columns)")


if __name__ == "__main__":
    main(sys.argv[1:])
