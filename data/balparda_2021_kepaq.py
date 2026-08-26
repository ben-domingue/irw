"""Balparda et al. (2021), Harvard Dataverse -- Keratoconus End-Points
Assessment Questionnaire (KEPAQ) in a Colombian cohort.

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/LTMAHE
DOI: 10.7910/DVN/LTMAHE
License: CC0 1.0

526 keratoconus patients completing the KEPAQ, which has a Functional and an
Emotional scale, each Rasch-calibrated separately.

Tables written
--------------
balparda_2021_kepaq_functional   526 patients x 9 items, 0-3
balparda_2021_kepaq_emotional    526 patients x 7 items, 0-3

Coding notes
------------
* Two tables, one per KEPAQ scale, for the same reason as the KORQ deposit by
  the same group: the two scales are separately calibrated measures that
  happen to share a 0-3 response format.
* `NAME` and `ID` hold the literal string "DELETED TO KEEP ANONYMITY" in
  every row; the depositor redacted them, so `id` is row position.
* Comorbidity flags that are constant across the cohort are not shipped.
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
DOI = "10.7910/DVN/LTMAHE"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
COVS = {"AGE_AT_DIAGNOSIS": "cov_age_at_diagnosis",
        "REFRACTIVE_SITUATION": "cov_refractive_status",
        "KERATOPLASTY": "cov_keratoplasty",
        "CORNEAL_RINGS": "cov_corneal_rings",
        "CROSSLINKING": "cov_crosslinking",
        "INTRAOCULAR_LENS": "cov_intraocular_lens"}
BLOCKS = [("functional", "KEPAQ_F_Q", 9), ("emotional", "KEPAQ_E_Q", 7)]


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
    d = pd.read_csv(io.BytesIO(raw.content), low_memory=False)

    for col in ("NAME", "ID"):
        assert d[col].nunique() == 1, col   # redacted placeholder, not PII
    d["id"] = range(1, len(d) + 1)

    os.makedirs(OUTDIR, exist_ok=True)
    shipped, total = set(), 0
    for suffix, prefix, n_expected in BLOCKS:
        items = [c for c in d.columns if str(c).startswith(prefix)]
        assert len(items) == n_expected, (suffix, len(items))
        shipped.update(items)

        long = d.melt(id_vars=["id"] + list(COVS), value_vars=items,
                      var_name="item", value_name="resp")
        long = long.rename(columns=COVS)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + list(COVS.values())]

        assert long["resp"].between(0, 3).all()
        assert not long.duplicated(["id", "item"]).any()
        assert long.groupby("item")["resp"].nunique().min() > 1
        checks = run_qc(long)
        bad = [c for c in checks if c.status == "fail"]
        assert not bad, (suffix, [(c.name, c.detail) for c in bad])

        name = f"balparda_2021_kepaq_{suffix}"
        path = os.path.join(OUTDIR, f"{name}.csv")
        assert not os.path.exists(path), name
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        total += len(long)
        print(f"{path}: {n_id} patients x {n_it} items = {len(long)} "
              f"responses, density {len(long) / (n_id * n_it):.3f}")

    n_const = 0
    for c in d.columns:
        if c in shipped or c in COVS or c == "id":
            continue
        if d[c].nunique(dropna=True) <= 1:
            n_const += 1
        else:
            print(f"  skip {c}: clinical/background variable not shipped "
                  f"as a covariate")
    print(f"  skip {n_const} constant/redacted columns")
    print(f"\n{len(BLOCKS)} tables, {total:,} responses")


if __name__ == "__main__":
    main()
