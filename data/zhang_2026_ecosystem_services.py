"""Zhang (2026), Mendeley Data -- ecosystem services and tourist well-being.

Source: https://data.mendeley.com/datasets/62rjwfhm6j
DOI: 10.17632/62rjwfhm6j
License: CC BY 4.0

1,016 tourists rating perceived ecosystem services and three further
constructs, all on a 1-7 scale.

Tables written
--------------
zhang_2026_ecosystem_services   1,016 x 12 items, 1-7
zhang_2026_tourist_wellbeing    1,016 x  4 items, 1-7
zhang_2026_healthy_attitude     1,016 x  4 items, 1-7
zhang_2026_ecological_values    1,016 x  4 items, 1-7

Coding notes
------------
* **The four ecosystem-services blocks are one table, not four.**
  Provisioning, Regulating, Cultural and Supporting are the four standard
  dimensions of a single perceived-ecosystem-services measure, three items
  each; they ship as one 12-item table with `itemcov_dimension`. The other
  three constructs are separate measures and get their own tables.
* Sheet 2 of the workbook holds per-construct means (`GJ`, `TJ`, `WH`, `ZC`,
  ...) rather than responses, and is not read.
* `Average value` on sheet 1 is the row mean across all 25 items.
* `no` is the deposit's own respondent number and is used as `id`.
"""

import io
import os
import re
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

DOI = "10.17632/62rjwfhm6j"
DATASET, VERSION = "62rjwfhm6j", 1
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
COVS = {"gender": "cov_gender", "age": "cov_age_band",
        "Education level": "cov_education"}
ES_DIMS = ["Provisioning services", "Regulating services",
           "Cultural services", "Supporting services"]
SOLO = [("tourist_wellbeing", "Tourist well-being", 4),
        ("healthy_attitude", "healthy attitude", 4),
        ("ecological_values", "Ecological Values", 4)]


def ship(long, name, unit, out):
    assert long["resp"].between(1, 7).all()
    assert not long.duplicated(["id", "item"]).any()
    assert long.groupby("item")["resp"].nunique().min() > 1
    checks = run_qc(long)
    bad = [c for c in checks if c.status == "fail"]
    assert not bad, (name, [(c.name, c.detail) for c in bad])
    path = os.path.join(OUTDIR, f"{name}.csv")
    assert not os.path.exists(path), name
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"{path}: {n_id} {unit} x {n_it} items = {len(long)} responses, "
          f"density {len(long) / (n_id * n_it):.3f}")
    return len(long)


def main():
    s = requests.Session()
    s.headers.update(UA)
    listing = s.get(f"https://data.mendeley.com/public-api/datasets/"
                    f"{DATASET}/files?folder_id=root&version={VERSION}",
                    timeout=120).json()
    hit = [f for f in listing if f["filename"].lower().endswith(".xlsx")]
    assert len(hit) == 1, [f["filename"] for f in listing]
    raw = s.get(hit[0]["content_details"]["download_url"], timeout=600)
    raw.raise_for_status()
    book = pd.ExcelFile(io.BytesIO(raw.content))
    d = book.parse(book.sheet_names[0])
    print(f"  reading sheet {book.sheet_names[0]!r}; "
          f"sheet {book.sheet_names[1]!r} holds construct means, not responses")

    d = d.rename(columns={"no": "id", **COVS})
    covs = list(COVS.values())
    os.makedirs(OUTDIR, exist_ok=True)
    shipped, total = set(), 0

    es_items, dim_of = [], {}
    for dim in ES_DIMS:
        cols = [c for c in d.columns if re.fullmatch(rf"{dim}\d+", str(c))]
        assert len(cols) == 3, (dim, cols)
        es_items += cols
        for c in cols:
            dim_of[c] = dim.replace(" services", "")
    shipped.update(es_items)
    long = d.melt(id_vars=["id"] + covs, value_vars=es_items,
                  var_name="item", value_name="resp")
    long["itemcov_dimension"] = long["item"].map(dim_of)
    long["item"] = long["item"].str.replace(" ", "_", regex=False)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    total += ship(long[["id", "item", "resp", "itemcov_dimension"] + covs],
                  "zhang_2026_ecosystem_services", "tourists", OUTDIR)

    for suffix, prefix, n_expected in SOLO:
        items = [c for c in d.columns if re.fullmatch(rf"{prefix}\d+", str(c))]
        assert len(items) == n_expected, (suffix, items)
        shipped.update(items)
        long = d.melt(id_vars=["id"] + covs, value_vars=items,
                      var_name="item", value_name="resp")
        long["item"] = long["item"].str.replace(" ", "_", regex=False)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        total += ship(long[["id", "item", "resp"] + covs],
                      f"zhang_2026_{suffix}", "tourists", OUTDIR)

    for c in d.columns:
        if c in shipped or c in covs or c == "id":
            continue
        assert c == "Average value", f"unaccounted source column: {c}"
        print("  skip Average value: row mean across all 25 items")
    print(f"\n4 tables, {total:,} responses")


if __name__ == "__main__":
    main()
