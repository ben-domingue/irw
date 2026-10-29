"""
Cyberbullying victimisation, resilience and depression in 353 Saudi Arabian
university students.

Source: Wan Sulaiman, W. S. (2023). Excel Data: Cyberbullying, resilience and
        depression [Dataset]. figshare. The deposit's own description: "This
        new data in Excel file were from a study regarding cyberbullying
        victimization, resilience and depression among university students in
        Saudi Arabia ... The data were collected using questionnaire."
DOI: 10.6084/m9.figshare.23964495.v1
Data: https://doi.org/10.6084/m9.figshare.23964495.v1
        ("new data-Cyberbullying, resilience and depression.xlsx")
License: CC BY 4.0 (verified on the figshare record, license.name "CC BY 4.0")

THE SAME FILE IS DEPOSITED TWICE and must only be processed once. figshare
records `10.6084/m9.figshare.23964495.v1` ("new data-Cyberbullying, resilience
and depression.xlsx") and `10.6084/m9.figshare.23977905.v1` ("Excel Data:
Cyberbullying, resilience and depression") both carry a file of the same name,
the same 92,655 bytes and the same MD5, `063e8a222ddd9ca3b89cf56b4bce7a3a`.
Both surfaced as separate candidates in the same triage. This script reads one
of them; the other is recorded as a duplicate in
`automated_finding/leads/repos_leads_2026-10-28.csv` so it is not shipped again.

Item text: NOT shipped and NOT recoverable from here. The deposit is a bare
`.xlsx` -- a format with no variable or value label level at all, so neither
was missed -- its columns are `R1p`..`R23s`, `CB1`..`CB11` and `D1`..`D18`, and
there is no codebook, second sheet or questionnaire file. Where to look: the
figshare record cites no article (`resource_doi` is null) and the description
names no instrument, so a later pass has to find Wan Sulaiman's
cyberbullying/resilience/depression paper on this Saudi sample first.

The three constructs come from the deposit's own title and its computed scores,
but NO instrument is named for any of them, and this script does not guess one:

  * `CB1..CB11`, 1-5 -- cyberbullying victimisation, 11 items. The deposit
    computes `CB` as their mean.
  * `R1p..R23s`, 1-5 -- resilience, 23 items whose suffixes mark five
    subscales (p: 7 items, ex: 4, m: 5, eq: 3, s: 4), and the deposit computes
    `R_P`, `R_EX`, `R_M`, `R_EQ`, `R_S` and `Resilience` to match. A 23-item
    five-factor resilience measure is a recognisable shape but it was NOT
    identified -- there is no wording to search, and guessing the instrument
    would put a wrong name on the table and, worse, invite a wrong rights
    ruling later. The item codes keep the source names so the subscale
    structure is preserved for whoever does identify it.
  * `D1..D18`, 0-3 -- depression, 18 items. Also unidentified; 0-3 over 18
    items is the shape of several screeners and the deposit distinguishes none
    of them.

PII: none. The screen below prints its denominator. The only text column is
`ID`, a per-study serial ("R1", "R105"), which is checked to be that shape and
then replaced by the row index.

Output: three tables, 18,006 responses.
  * wan_sulaiman_2023_resilience    -- 23 items, resp 1-5
  * wan_sulaiman_2023_depression    -- 18 items, resp 0-3
  * wan_sulaiman_2023_cyberbullying -- 11 items, resp 1-5
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd

SRC = (Path(sys.argv[1]) if len(sys.argv) > 1
       else Path("new data-Cyberbullying, resilience and depression.xlsx"))
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

RESILIENCE = re.compile(r"^R\d+(p|ex|m|eq|s)$")
BLOCKS = {
    "wan_sulaiman_2023_resilience": (RESILIENCE, 23, [1, 2, 3, 4, 5]),
    "wan_sulaiman_2023_depression": (re.compile(r"^D\d+$"), 18, [0, 1, 2, 3]),
    "wan_sulaiman_2023_cyberbullying": (re.compile(r"^CB\d+$"), 11,
                                        [1, 2, 3, 4, 5]),
}

COV_MAP = {
    "Gender": "cov_gender",
    "University": "cov_university",
    "Year": "cov_year_of_study",
}

DROP = {
    "ID": "a per-study serial ('R1', 'R105'), replaced by the row index",
    "R_P": "depositor-computed resilience subscale mean",
    "R_EX": "depositor-computed resilience subscale mean",
    "R_M": "depositor-computed resilience subscale mean",
    "R_EQ": "depositor-computed resilience subscale mean",
    "R_S": "depositor-computed resilience subscale mean",
    "CB": "depositor-computed cyberbullying mean",
    "Resilience": "depositor-computed resilience total mean",
    "Depression": "depositor-computed depression mean",
}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    assert text_cols == ["ID"], text_cols
    serial = df["ID"].astype(str)
    assert serial.str.fullmatch(r"R\d{1,4}").all(), \
        sorted(set(serial[~serial.str.fullmatch(r'R\d{1,4}')]))[:5]
    print("the one text column is ID, every value of the form R<digits> -- a "
          "per-study serial, not an identifier of a person")


def main() -> None:
    df = pd.read_excel(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 353, len(df)

    cols = {}
    for table, (pat, n, _p) in BLOCKS.items():
        cs = [c for c in df.columns if pat.match(c) and c not in DROP]
        assert len(cs) == n, (table, len(cs), n, cs)
        cols[table] = cs
    # The resilience block's own numbering must run 1..23 exactly once, which
    # is what says the five suffixes partition one 23-item instrument rather
    # than marking five instruments that happen to share a prefix.
    nums = sorted(int(re.match(r"^R(\d+)", c).group(1))
                  for c in cols["wan_sulaiman_2023_resilience"])
    assert nums == list(range(1, 24)), nums
    suffixes = {}
    for c in cols["wan_sulaiman_2023_resilience"]:
        suffixes.setdefault(RESILIENCE.match(c).group(1), []).append(c)
    print("resilience: item numbers run 1..23 exactly once across five "
          "suffixes -- " + "; ".join(f"{k}: {len(v)} items"
                                     for k, v in sorted(suffixes.items())))

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = pd.to_numeric(df[src], errors="raise")
    covs = list(COV_MAP.values())

    accounted = (set(COV_MAP) | set(covs) | set(DROP) | {"id"}
                 | {c for cs in cols.values() for c in cs})
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in DROP.items():
        print(f"skipped column {c}: {why}")

    for table, (_pat, _n, permitted) in BLOCKS.items():
        cs = cols[table]
        codes = {c: c.lower() for c in cs}
        assert len(set(codes.values())) == len(cs), codes
        block = df[cs].apply(lambda s: pd.to_numeric(s, errors="raise"))
        long = pd.concat([df[["id"] + covs], block.rename(columns=codes)],
                         axis=1)
        long = long.melt(id_vars=["id"] + covs, var_name="item",
                         value_name="resp")
        before = long["resp"].notna().sum()
        long = long[long["resp"].isin(permitted)]
        if before != len(long):
            print(f"{table}: dropped {before - len(long)} cell(s) of {before} "
                  f"outside {permitted}")
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
