"""Cosenza & Nigro (2015), Harvard Dataverse -- Consideration of Future
Consequences in adolescent gamblers.

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DWWZSI
DOI: 10.7910/DVN/DWWZSI
License: CC0 1.0
Paper: Cosenza, M., & Nigro, G. (2015). Wagering the future: cognitive
distortions, impulsivity, delay discounting, and time perspective in
adolescent gambling. Journal of Adolescence, 45, 56-66.

Tables written
--------------
cosenza_2015_cfc   1,030 adolescents x 14 items, 1-7

Coding notes
------------
* The full CFC-14 (Joireman et al., 2012), all 14 items on one 1-7 scale.
* Two source columns are spelled `CF4`/`CF5` rather than `CFC4`/`CFC5`; that
  is a typo in the deposit, not a second instrument -- both sit in the CFC
  numbering with no gap and share the scale -- so they are renamed to the
  regular form and the numbering is asserted to be 1..14 with no duplicates.
* The deposit carries no identifier column, so `id` is row position.
* Reverse-keyed items are left as administered; the deposit ships no scored
  totals to check a recode against.
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
DOI = "10.7910/DVN/DWWZSI"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
TABLE = "cosenza_2015_cfc"
COVS = {"GENDER": "cov_gender", "AGE": "cov_age"}


def main():
    s = requests.Session()
    s.headers.update(UA)
    meta = s.get(f"{BASE}/api/datasets/:persistentId/",
                 params={"persistentId": f"doi:{DOI}"}, timeout=120
                 ).json()["data"]["latestVersion"]
    hit = [f["dataFile"] for f in meta["files"]
           if f["dataFile"]["filename"] == "WAGERING.tab"]
    assert len(hit) == 1
    raw = s.get(f"{BASE}/api/access/datafile/{hit[0]['id']}",
                params={"format": "original"}, timeout=600)
    raw.raise_for_status()
    d = pd.read_excel(io.BytesIO(raw.content))

    items = [c for c in d.columns if re.fullmatch(r"CFC?\d+", str(c))]
    nums = sorted(int(re.sub(r"\D", "", c)) for c in items)
    assert nums == list(range(1, 15)), nums
    rename = {c: f"CFC{int(re.sub(r'[^0-9]', '', c))}" for c in items}
    d = d.rename(columns=rename)
    items = [f"CFC{i}" for i in range(1, 15)]

    d["id"] = range(1, len(d) + 1)
    long = d.melt(id_vars=["id"] + list(COVS), value_vars=items,
                  var_name="item", value_name="resp")
    long = long.rename(columns=COVS)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + list(COVS.values())]

    assert long["resp"].between(1, 7).all()
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long)
    bad = [c for c in checks if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    accounted = set(items) | set(COVS) | {"id"}
    for c in d.columns:
        assert c in accounted, f"unaccounted source column: {c}"

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f"{TABLE}.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
          f"resp {long['resp'].min()}-{long['resp'].max()}, "
          f"density {len(long) / (n_id * n_it):.3f}")


if __name__ == "__main__":
    main()
