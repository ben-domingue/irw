"""Environmental concern and drone-delivery acceptance questionnaire.

Source: Jingqiong Wu & Ziwei Chen (2025), figshare 10.6084/m9.figshare.30236404,
CC BY 4.0 -- "Anonymized participant background information and questionnaire
scale scores", supporting PLOS ONE 10.1371/journal.pone.0333422. 498
respondents x 50 items on a 1-5 agreement scale.

The article ships a second file (figshare 30236407, "Questionnaire Score Test
Set", 102 respondents on the same 50 items) which is NOT used here. Its
columns are a strict subset of this file's, it carries no demographics, and 25
of its 102 rows reproduce a row of this file exactly across all 50 items --
enough overlap that appending it would double-count respondents, and not
enough documentation to say which 25. Shipping the larger, fully documented
file only.

Ten of the 48 non-demographic columns are NOT items: `Environmental
Cognition`, `UAV-Environmental Cognition`, `Perceived Usefulness`, `Perceived
Ease Of Use`, `Perceived Risk`, `Health Safety`, `Policy Support`, `Social
Norm`, `Service Performance` and `Willingness Accept` are construct means,
each sitting as a header immediately above the items it summarises. They give
themselves away by holding fractional values (e.g. 1.4) and 13-17 distinct
values where every real item has exactly 5 -- so the script identifies them by
that property and asserts it finds ten, rather than trusting a hard-coded list.
The construct each item belongs to is carried as `itemcov_construct`.

Item codes are the questionnaire's own English statements, so they are
replaced with positional `Q1`..`Q38` codes; the statements belong in an item
text table, not in the `item` column.
"""
import os

import pandas as pd
import requests

ARTICLE = 30236404
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "wu_2025_drone_delivery"

COVARIATES = {"Sexes": "cov_sex", "Age": "cov_age",
              "Education attainment": "cov_education",
              "Current place of residence": "cov_residence",
              "Type of occupation": "cov_occupation",
              "Frequency of online shopping": "cov_online_shopping_frequency"}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    meta = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                        timeout=120).json()
    f = next(x for x in meta["files"]
             if x["name"].lower().endswith((".xlsx", ".xls", ".csv")))
    r = requests.get(f["download_url"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["name"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    p = fetch_raw(path)
    df = pd.read_csv(p) if p.lower().endswith(".csv") else pd.read_excel(p)
    df = df.loc[:, [c for c in df.columns if not str(c).startswith("Unnamed")]]

    skip = set(COVARIATES) | {"Serial Number"}
    candidates = [c for c in df.columns if c not in skip]

    def is_composite(col):
        u = df[col].dropna()
        return bool((u != u.round()).any()) or u.nunique() > 5

    composites = [c for c in candidates if is_composite(c)]
    assert len(composites) == 10, \
        f"expected 10 construct means, found {len(composites)}: {composites}"

    # Each construct mean heads the block of items it summarises.
    construct_of, current = {}, None
    for c in candidates:
        if c in composites:
            current = str(c).strip()
        else:
            construct_of[c] = current
    statements = [c for c in candidates if c not in composites]
    assert len(statements) == 38, \
        f"expected 38 item statements, found {len(statements)}"

    rename = {c: f"Q{i}" for i, c in enumerate(statements, start=1)}
    construct_by_code = {rename[c]: construct_of[c] for c in statements}
    df = df.rename(columns={**rename, **COVARIATES}).reset_index(drop=True)
    covs = list(COVARIATES.values())
    items = list(rename.values())
    df["id"] = df.index + 1

    long = (df.melt(id_vars=["id"] + covs, value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)
    long["itemcov_construct"] = long["item"].map(construct_by_code)
    long = long[["id", "item", "resp", "itemcov_construct"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == len(items)
    assert long["resp"].between(1, 5).all(), \
        f"expected 1-5, saw {long['resp'].min()}-{long['resp'].max()}"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
