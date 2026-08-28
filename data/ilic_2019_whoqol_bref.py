"""WHOQOL-BREF, Serbian medical-student sample.

Source: Ilic, Irena (2019), Zenodo 10.5281/zenodo.3404237, CC BY 4.0 --
"Psychometric properties of the World Health Organization's Quality of Life
(WHOQOL-BREF) questionnaire". 760 respondents, 26 WHOQOL-BREF items on the
instrument's 1-5 scale.

The deposit ships TWO .sav files, `WHOdef.sav r.sav 2.sav` and
`engWHOdef.sav r.sav 2.sav`. They are the same data: identical on all 29
shared columns, differing only in the name of the year variable (`godina` vs
its English rendering `studyyear`). Only one is read -- treating them as two
samples would double 760 respondents into a fictitious 1,520.

Three columns are dropped as derived: `who3cor`, `who4cor` and `who26cor` are
the reverse-scored recodes of items 3, 4 and 26, which are the WHOQOL-BREF's
three negatively-worded items. The raw responses ship; a monotone recode of a
shipped item is not a separate item.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

RECORD = 3404237
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "ilic_2019_whoqol_bref"

DERIVED = ["who3cor", "who4cor", "who26cor"]
YEAR_COLS = ["godina", "studyyear"]


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    savs = [x for x in rec["files"] if x["key"].lower().endswith(".sav")]
    # The two files are the same data; take the one whose year column is named
    # in the source language, and ignore the English-renamed duplicate.
    f = sorted(savs, key=lambda x: x["key"].lower().startswith("eng"))[0]
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    src = fetch_raw(path)
    try:
        df, _meta = pyreadstat.read_sav(src, apply_value_formats=False)
    except Exception:
        df, _meta = pyreadstat.read_sav(src, apply_value_formats=False,
                                        encoding="latin1")

    items = [c for c in df.columns
             if re.match(r"^who\d+$", str(c)) and c not in DERIVED]
    assert len(items) == 26, f"expected 26 WHOQOL-BREF items, found {len(items)}"

    year = [c for c in YEAR_COLS if c in df.columns]
    accounted = set(items) | set(DERIVED) | set(year)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns={c: "cov_study_year" for c in year})
    covs = ["cov_study_year"] if year else []
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    long = (df.melt(id_vars=["id"] + covs, value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)

    # One cell of `who1` holds a 6 on a 1-5 scale. The item's own SPSS value
    # labels define exactly five levels ('Jako lose' .. 'Odlicno'), no other
    # item exceeds 5, and it is a single observation out of 755 -- a
    # data-entry error, not a different response format. Dropped rather than
    # clamped, so the table never asserts a response the instrument cannot
    # produce.
    bad = ~long["resp"].between(1, 5)
    if bad.any():
        print(f"  dropping {int(bad.sum())} out-of-range cell(s): "
              f"{sorted(long.loc[bad, 'item'].unique())}")
        long = long[~bad]

    long = long[["id", "item", "resp"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 26
    assert long["resp"].between(1, 5).all()

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
