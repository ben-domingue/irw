"""Redline, Jones & Almonroeder (2026), Harvard Dataverse -- the 10-item
Professional Self-Belief questionnaire (ProSBq).

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/4E3UDL
DOI: 10.7910/DVN/4E3UDL
License: CC0 1.0

634 respondents completing the 10-item ProSBq, from which the paper derives a
brief 2-item measure.

Tables written
--------------
redline_2026_prosbq   634 respondents x 10 items, 1-6

Coding notes
------------
* The `_VC` and `_SA` suffixes mark the questionnaire's two content facets;
  all ten items share one 1-6 response format and were administered as a
  single instrument, so this is one table with `itemcov_facet` rather than
  two.
* **`10.7910/DVN/UWTICO` is the same data.** The authors deposited the file a
  second time two weeks later ("rows 2445 development"); the two files are
  byte-identical (md5 7dbbcc3aaf56f16d67ac27b3a03209dc), so only this one is
  shipped.
* The deposit carries no identifier column, so `id` is row position.
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

BASE = "https://dataverse.harvard.edu"
DOI = "10.7910/DVN/4E3UDL"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
TABLE = "redline_2026_prosbq"


def main():
    s = requests.Session()
    s.headers.update(UA)
    meta = s.get(f"{BASE}/api/datasets/:persistentId/",
                 params={"persistentId": f"doi:{DOI}"}, timeout=120
                 ).json()["data"]["latestVersion"]
    hit = [f["dataFile"] for f in meta["files"]
           if f["dataFile"]["filename"].startswith("Dataset 1")]
    assert len(hit) == 1
    raw = s.get(f"{BASE}/api/access/datafile/{hit[0]['id']}", timeout=600)
    raw.raise_for_status()
    d = pd.read_csv(io.BytesIO(raw.content), sep="\t", low_memory=False)

    items = [c for c in d.columns if re.fullmatch(r"Q\d+_(VC|SA)", str(c))]
    assert len(items) == 10, sorted(items)
    assert len(d.columns) == 10, list(d.columns)   # nothing else in the file

    d["id"] = range(1, len(d) + 1)
    long = d.melt(id_vars=["id"], value_vars=items,
                  var_name="item", value_name="resp")
    long["itemcov_facet"] = long["item"].str.split("_").str[1]
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "itemcov_facet"]]

    assert long["resp"].between(1, 6).all()
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long)
    bad = [c for c in checks if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f"{TABLE}.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
          f"density {len(long) / (n_id * n_it):.3f}")


if __name__ == "__main__":
    main()
