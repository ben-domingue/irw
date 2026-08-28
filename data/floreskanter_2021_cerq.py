"""Cognitive Emotion Regulation Questionnaire (CERQ), Argentinean sample.

Source: Flores Kanter & Medrano (2021), Mendeley Data 10.17632/48y8tkf5wh,
CC BY 4.0 -- data behind "Internal Structure of the CERQ: CFA and ESEM Analysis
in a Large Argentinean Sample". Single file `Data_Mendeley.sav`, 6,887
respondents x 36 columns, all of them CERQ items on the instrument's 1-5
frequency scale ("almost never" to "almost always").

The file is entirely items: no demographics, no composites, no identifier.
`id` is therefore the row index -- one row per respondent, matching the 6,887
cases the paper reports. The 36 items are the full CERQ (nine four-item
subscales); they ship as one table because they are one instrument
administered with one response format, and the subscale structure is exactly
what the source paper is testing rather than a property of the data.
"""
import os

import pandas as pd
import pyreadstat
import requests

DOI = "10.17632/48y8tkf5wh"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "floreskanter_2021_cerq"


def fetch_raw(path=None):
    """Read the .sav, downloading from Mendeley unless a local copy is given.

    Uses `/public-api/datasets/{key}` (the endpoint the IRW pipeline's own
    resolver uses), which returns the *latest* version's files. Selecting by
    extension rather than by filename is deliberate: this deposit renamed its
    .sav between versions, so a pinned name breaks on the next revision.
    """
    if path and os.path.exists(path):
        return path
    key = DOI.split("/")[-1]
    data = requests.get(f"https://data.mendeley.com/public-api/datasets/{key}",
                        timeout=120).json()
    sav = [f for f in data.get("files", [])
           if f.get("filename", "").lower().endswith(".sav")]
    assert len(sav) == 1, f"expected one .sav, found {[f['filename'] for f in sav]}"
    url = sav[0]["content_details"]["download_url"]
    r = requests.get(url, timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", sav[0]["filename"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    df, _meta = pyreadstat.read_sav(fetch_raw(path), apply_value_formats=False)
    items = [c for c in df.columns if c.upper().startswith("CERQ")]
    # Book-balancing: every column in the file must be accounted for, so a
    # composite or demographic added in a later deposit version cannot be
    # silently swept into the item list or silently dropped.
    unaccounted = [c for c in df.columns if c not in items]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    assert len(items) == 36, f"expected 36 CERQ items, found {len(items)}"

    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    long = (df.melt(id_vars=["id"], value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() > 1
    assert long["resp"].between(1, 5).all(), "CERQ is a 1-5 scale"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
