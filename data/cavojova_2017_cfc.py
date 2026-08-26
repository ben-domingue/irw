"""Čavojová & Jurkovič (2017), Harvard Dataverse -- Consideration of Future
Consequences in Slovak teachers.

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/5VEZ7T
DOI: 10.7910/DVN/5VEZ7T
License: CC0 1.0
Paper: Čavojová, V., & Jurkovič, M. (2017). Comparison of experienced vs
novice teachers in cognitive reflection and rationality. Studia Psychologica
59(3), 100-112.

Tables written
--------------
cavojova_2017_cfc   170 teachers x 14 items, 1-6

Coding notes
------------
* CFC-14 again, but administered on a **1-6** scale here rather than the
  1-7 of `cosenza_2015_cfc`; the two are separate tables for that reason as
  well as being separate samples.
* The source suffixes `_F`/`_I` mark the Future and Immediate subscales; they
  are stripped from the item ids so numbering matches the published
  instrument, and the subscale is carried as `itemcov_subscale`.
* Seven `CFC*_R` columns are the reverse-scored copies of the Immediate items
  (verified: `CFCn_R == 7 - CFCn`) and are not shipped -- they are derived,
  not administered.
* `CFC_I`, `CFC_I_R`, `CFC_F`, `CFC_tot`, `CFC_tot_avg` are scored totals.
* The deposit carries no identifier column, so `id` is row position.
* `sample` (0/1) distinguishes the novice and experienced teacher samples and
  is kept as `cov_sample`.
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
DOI = "10.7910/DVN/5VEZ7T"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
TABLE = "cavojova_2017_cfc"
COVS = {"sex": "cov_sex", "age": "cov_age", "county": "cov_region",
        "workexp": "cov_experience", "sample": "cov_sample"}
SKIP = {"CFC_I": "scored subscale total", "CFC_I_R": "scored subscale total",
        "CFC_F": "scored subscale total", "CFC_tot": "scored total",
        "CFC_tot_avg": "scored mean"}


def main():
    s = requests.Session()
    s.headers.update(UA)
    meta = s.get(f"{BASE}/api/datasets/:persistentId/",
                 params={"persistentId": f"doi:{DOI}"}, timeout=120
                 ).json()["data"]["latestVersion"]
    hit = [f["dataFile"] for f in meta["files"]
           if f["dataFile"]["filename"] == "cfc14.tab"]
    assert len(hit) == 1
    raw = s.get(f"{BASE}/api/access/datafile/{hit[0]['id']}",
                params={"format": "original"}, timeout=600)
    raw.raise_for_status()
    open("/tmp/cavojova_cfc14.sav", "wb").write(raw.content)
    d = pd.read_spss("/tmp/cavojova_cfc14.sav", convert_categoricals=False)

    items = {}
    for c in d.columns:
        m = re.fullmatch(r"CFC(\d+)_([FI])", str(c))
        if m:
            items[c] = (int(m.group(1)),
                        {"F": "future", "I": "immediate"}[m.group(2)])
    assert sorted(n for n, _ in items.values()) == list(range(1, 15)), items

    # the _R columns must be derived, or they would be separate responses
    for c in d.columns:
        m = re.fullmatch(r"CFC(\d+)_R", str(c))
        if m:
            src = next(k for k, (n, _) in items.items() if n == int(m.group(1)))
            assert (d[c] == 7 - d[src]).all(), c

    d["id"] = range(1, len(d) + 1)
    long = d.melt(id_vars=["id"] + list(COVS), value_vars=list(items),
                  var_name="src", value_name="resp")
    long = long.rename(columns=COVS)
    long["item"] = long["src"].map(lambda c: f"CFC{items[c][0]}")
    long["itemcov_subscale"] = long["src"].map(lambda c: items[c][1])
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "itemcov_subscale"]
                + list(COVS.values())]

    assert long["resp"].between(1, 6).all()
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long)
    bad = [c for c in checks if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    for c in d.columns:
        if c in items or c in COVS or c == "id":
            continue
        if re.fullmatch(r"CFC\d+_R", str(c)):
            print(f"  skip {c}: reverse-scored copy of the administered item")
        else:
            assert c in SKIP, f"unaccounted source column: {c}"
            print(f"  skip {c}: {SKIP[c]}")

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f"{TABLE}.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"\n{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
          f"resp {long['resp'].min()}-{long['resp'].max()}, "
          f"density {len(long) / (n_id * n_it):.3f}")


if __name__ == "__main__":
    main()
