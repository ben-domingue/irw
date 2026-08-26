"""Okoro (2022), Harvard Dataverse -- effect of motivation strategies on
students' interest.

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/QAWGJV
DOI: 10.7910/DVN/QAWGJV
License: CC0 1.0

100 secondary students randomly assigned to an intrinsic- or an
extrinsic-motivation teaching condition (50 each), measured on a 30-item
interest inventory.

Tables written
--------------
okoro_2022_interest_inventory   100 students x 30 items, 1-4

Coding notes
------------
* **The item-level block is the post-test administration.** The deposit also
  carries `PretestInterest` and `PosttestInterest` totals; the row sum of
  `Item1`..`Item30` equals `PosttestInterest` exactly for all 100 students
  and equals `PretestInterest` for none, so the 30 columns are the post-test
  and the pre-test exists only as a total. There is therefore no `wave`
  column -- one administration is deposited at item level, not two.
* `Methods` is the randomly assigned condition and ships as `treat`
  (1 = intrinsic motivation, 2 = extrinsic motivation), per `datastandard.md`.
* `Pretest`/`Posttest` are achievement-test scores on a different instrument,
  deposited only as totals.
* The deposit carries no identifier column, so `id` is row position.
"""

import os
import sys

import pandas as pd
import pyreadstat
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

BASE = "https://dataverse.harvard.edu"
DOI = "10.7910/DVN/QAWGJV"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
TABLE = "okoro_2022_interest_inventory"
COVS = {"Class": "cov_class", "Age": "cov_age_band", "Gender": "cov_gender"}
SKIP = {"PretestInterest": "pre-test total; its items are not deposited",
        "PosttestInterest": "total of Item1..Item30, recomputable",
        "Pretest": "achievement-test total on another instrument",
        "Posttest": "achievement-test total on another instrument"}


def main():
    s = requests.Session()
    s.headers.update(UA)
    meta = s.get(f"{BASE}/api/datasets/:persistentId/",
                 params={"persistentId": f"doi:{DOI}"}, timeout=120
                 ).json()["data"]["latestVersion"]
    hit = [f["dataFile"] for f in meta["files"]
           if f["dataFile"]["filename"].endswith(".tab")]
    assert len(hit) == 1
    raw = s.get(f"{BASE}/api/access/datafile/{hit[0]['id']}",
                params={"format": "original"}, timeout=600)
    raw.raise_for_status()
    open("/tmp/okoro.sav", "wb").write(raw.content)
    d, _ = pyreadstat.read_sav("/tmp/okoro.sav")

    items = [f"Item{i}" for i in range(1, 31)]
    assert set(items) <= set(d.columns)
    # this is what identifies the block as the post-test, not the pre-test
    assert (d[items].sum(axis=1) == d["PosttestInterest"]).all()
    assert (d[items].sum(axis=1) == d["PretestInterest"]).sum() == 0

    d["id"] = range(1, len(d) + 1)
    d["treat"] = d["Methods"].astype(int)
    long = d.melt(id_vars=["id", "treat"] + list(COVS), value_vars=items,
                  var_name="item", value_name="resp")
    long = long.rename(columns=COVS)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "treat"] + list(COVS.values())]

    assert long["resp"].between(1, 4).all()
    assert not long.duplicated(["id", "item"]).any()
    assert long.groupby("item")["resp"].nunique().min() > 1
    checks = run_qc(long)
    bad = [c for c in checks if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    for c in d.columns:
        if c in items or c in COVS or c in ("id", "treat", "Methods"):
            continue
        assert c in SKIP, f"unaccounted source column: {c}"
        print(f"  skip {c}: {SKIP[c]}")

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f"{TABLE}.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"\n{path}: {n_id} students x {n_it} items = {len(long)} "
          f"responses, density {len(long) / (n_id * n_it):.3f}")


if __name__ == "__main__":
    main()
