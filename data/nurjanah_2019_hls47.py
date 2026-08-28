"""Indonesian Health Literacy Survey (HLS-EU-Q47).

Source: Nurjanah & Rachmani (2019), Mendeley Data 10.17632/zr54c7rxs3,
CC BY 4.0 -- data for "Using the Feature Selection with Genetic Algorithm to
Abbreviate Indonesia's Health Literacy Questionnaire". Single file
`data hl47.xlsx`, 1,029 respondents x 47 items (`q1`..`q47`) on a 1-4
difficulty scale.

Eight columns are derived and are dropped: `Health Care`, `Disease
Prevention`, `Health Promotion` and `General Health Literacy` are HLS-EU
domain and total indices, `HC_HLI` / `DP-HLI` / `HP-HLI` their standardised
forms, and `GHL Label` the banded category ("inadequate", "problematic", ...).
All are functions of the 47 items.
"""
import os
import re

import pandas as pd
import requests

DOI = "10.17632/zr54c7rxs3"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "nurjanah_2019_hls47"

DERIVED = ["Health Care", "HC_HLI", "Disease Prevention", "DP-HLI",
           "Health Promotion", "HP-HLI", "General Health Literacy",
           "GHL Label"]


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    key = DOI.split("/")[-1]
    data = requests.get(f"https://data.mendeley.com/public-api/datasets/{key}",
                        timeout=120).json()
    f = next(x for x in data["files"]
             if x["filename"].lower().endswith((".xlsx", ".xls")))
    r = requests.get(f["content_details"]["download_url"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["filename"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    df = pd.read_excel(fetch_raw(path))
    items = [c for c in df.columns if re.match(r"^q\d+$", str(c))]
    assert len(items) == 47, f"expected 47 HLS items, found {len(items)}"

    accounted = set(items) | set(DERIVED) | {"responden"}
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.reset_index(drop=True)
    df["id"] = df["responden"].astype(int)
    assert df["id"].is_unique, "`responden` is not one row per respondent"

    long = (df.melt(id_vars=["id"], value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 47
    assert long["resp"].between(1, 4).all(), "HLS-EU-Q47 is a 1-4 scale"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
