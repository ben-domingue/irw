"""Balparda et al. (2021), Harvard Dataverse -- Keratoconus Outcomes Research
Questionnaire (KORQ) validated in Colombian patients.

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/URNE8Q
DOI: 10.7910/DVN/URNE8Q
License: CC0 1.0

158 keratoconus patients completing the KORQ, a Rasch-calibrated
patient-reported outcome measure with two separately scored scales.

Tables written
--------------
balparda_2021_korq_activity_limitation   158 patients x 18 items, 0-3
balparda_2021_korq_symptoms              158 patients x 11 items, 0-3

Coding notes
------------
* **Two tables, one per KORQ scale.** Activity Limitation and Symptoms are
  calibrated and scored separately in the instrument's own validation work,
  including in this paper, so they are separate measurement scales even
  though both use the same 0-3 response format.
* Missing responses are coded `x` in the source and become missing rows.
* `NAME` and `DOCUMENT` are present but hold the literal string "Deleted to
  keep anonymity" in every row -- the depositor redacted them; no identifying
  values are in the file.
* `CONSECUTIVE` is the deposit's own patient number and is used as `id`.
* The many comorbidity flags that are constant zero across all 158 patients
  (Marfan, Apert, Turner, ...) are not shipped as covariates.
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
DOI = "10.7910/DVN/URNE8Q"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
COVS = {"AGE": "cov_age", "SEX": "cov_sex",
        "edad_diagnostico": "cov_age_at_diagnosis",
        "situacion_refractiva": "cov_refractive_status",
        "queratoplastia": "cov_keratoplasty",
        "anillos": "cov_corneal_rings",
        "crosslinking": "cov_crosslinking",
        "lente_intraocular": "cov_intraocular_lens"}
BLOCKS = [("activity_limitation", "korq_limita_q", 18),
          ("symptoms", "korq_sintomas_q", 11)]


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

    for col in ("NAME", "DOCUMENT"):
        assert d[col].nunique() == 1, col   # redacted placeholder, not PII

    d = d.rename(columns={"CONSECUTIVE": "id"})
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

        name = f"balparda_2021_korq_{suffix}"
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
    print(f"  skip {n_const} constant comorbidity flags")
    print(f"\n{len(BLOCKS)} tables, {total:,} responses")


if __name__ == "__main__":
    main()
