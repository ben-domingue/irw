"""Hochsteiner, Tezza & de Borba (2026), Harvard Dataverse -- perceived
relevance of environmental sustainability indicators in smart campuses.

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/FCNTSN
DOI: 10.7910/DVN/FCNTSN
License: CC0 1.0

291 respondents rating the relevance of 27 sustainability indicators grouped
into six domains, from a scale-development and validation study.

Tables written
--------------
hochsteiner_2026_sustainability_relevance   291 respondents x 27 items, 1-5

Coding notes
------------
* **The spreadsheet has two header rows, not one.** Row 1 holds the domain
  name over the first column of each group (Water, Air, Energy, Waste,
  Social, Technology) and is blank elsewhere; row 2 holds the item number
  1..27. Read naively, pandas takes row 1 as the header and row 2 as data,
  which is what makes the column maxima look like 1..27. Both header rows are
  read explicitly here: the numbers become the item ids and the domain is
  forward-filled into `itemcov_domain`.
* One instrument on one 1-5 relevance scale, so one table; the domain is an
  item covariate rather than a table split.
* **`10.6084/m9.figshare.33126869` is the same dataset** deposited by the same
  authors on figshare (identical 291 x 27 shape and values); only this copy is
  shipped.
* The deposit carries no identifier column, so `id` is row position.
"""

import io
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

BASE = "https://dataverse.harvard.edu"
DOI = "10.7910/DVN/FCNTSN"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
TABLE = "hochsteiner_2026_sustainability_relevance"


def main():
    s = requests.Session()
    s.headers.update(UA)
    meta = s.get(f"{BASE}/api/datasets/:persistentId/",
                 params={"persistentId": f"doi:{DOI}"}, timeout=120
                 ).json()["data"]["latestVersion"]
    hit = [f["dataFile"] for f in meta["files"]
           if f["dataFile"]["filename"].lower().endswith(".xlsx")]
    assert len(hit) == 1
    raw = s.get(f"{BASE}/api/access/datafile/{hit[0]['id']}",
                params={"format": "original"}, timeout=600)
    raw.raise_for_status()
    book = pd.read_excel(io.BytesIO(raw.content), header=None)

    domains = book.iloc[0].ffill().tolist()
    numbers = book.iloc[1].astype(int).tolist()
    assert numbers == list(range(1, 28)), numbers
    assert set(domains) == {"Water", "Air", "Energy", "Waste", "Social",
                            "Technology"}, set(domains)
    body = book.iloc[2:].reset_index(drop=True)
    body.columns = [f"I{n}" for n in numbers]
    domain_of = {f"I{n}": dom for n, dom in zip(numbers, domains)}

    body["id"] = range(1, len(body) + 1)
    long = body.melt(id_vars=["id"], value_vars=list(domain_of),
                     var_name="item", value_name="resp")
    long["itemcov_domain"] = long["item"].map(domain_of)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "itemcov_domain"]]

    assert long["resp"].between(1, 5).all(), (long["resp"].min(),
                                              long["resp"].max())
    assert not long.duplicated(["id", "item"]).any()
    assert long.groupby("item")["resp"].nunique().min() > 1
    checks = run_qc(long)
    bad = [c for c in checks if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f"{TABLE}.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"{path}: {n_id} respondents x {n_it} items = {len(long)} "
          f"responses, density {len(long) / (n_id * n_it):.3f}")
    print("  items per domain: "
          + ", ".join(f"{k} {v}" for k, v in
                      long.groupby("itemcov_domain")["item"].nunique().items()))


if __name__ == "__main__":
    main()
