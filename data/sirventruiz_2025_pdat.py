"""Sirvent-Ruiz, Miranda & Moral-Jimenez (2025), PLOS ONE -- Predictors of
Dropout in Addiction Treatment (PDAT).

Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0326853
DOI: 10.1371/journal.pone.0326853
Data: S2 Dataset (journal.pone.0326853.s002)
License: CC BY 4.0

243 patients in addiction treatment, assessed repeatedly with the 26-item
PDAT during their admission -- 878 assessments in all. Found by the
2026-08-25 educational-measurement term sweep (PLOS mode) and resolved from
its `worth_retrying` bucket.

Table written
-------------
sirventruiz_2025_pdat   26 items, resp 1-5, 878 assessments over 243 patients

Coding notes
------------
* **This is repeated-measures data and ships with a `wave` column.** The file
  has 878 rows over 243 `Patient.ID` values -- most patients contribute 1-6
  assessments, one contributes 39 -- so `Patient.ID` alone does not key a row
  and a naive melt produces duplicate id/item pairs. That is why triage
  flagged it rather than passing it.
* `wave` is the rank of `Days.between.admission.and.PDAT` within each patient,
  giving 1..n in administration order. Two of the 878 rows share a
  (patient, day) pair, so the rank is taken with `method="first"` to break
  those deterministically; the script asserts that every (id, wave, item)
  triple is unique afterwards. The raw day count is also kept as
  `cov_days_admission_to_pdat`, so the actual spacing is not lost -- `date` is
  not used, since the deposit gives days relative to admission rather than
  an absolute timestamp.
* All 26 items span 1-5 on every item, with no out-of-range values.
* Excluded as derived: `Motivation.scores`, `Craving.scores`,
  `Problem.awareness.scores`, `Dysphoria.scores` (the PDAT's four subscale
  scores) and `PDAT13.scores` (the short-form total). The deposit's S3 Table
  documents the correspondence between the 26-item and 13-item versions.
* `Reason.for.discharge` and the other three day-gap columns are outcome
  variables measured after the assessment; they are carried as covariates
  rather than dropped, since they describe the person-occasion.
"""

import os
import re

import pandas as pd
import requests

ARTICLE = ("https://journals.plos.org/plosone/article/file"
           "?type=supplementary&id=10.1371/journal.pone.0326853.s002")
OUTDIR = "irw_output"

COVS = {
    "Days.between.admission.and.PDAT": "cov_days_admission_to_pdat",
    "Days.between.PDAT.and.discharge": "cov_days_pdat_to_discharge",
    "Days.between.PDAT.and.48.hour.request": "cov_days_pdat_to_48h_request",
    "Days.between.PDAT.and.anticraving.medication": "cov_days_pdat_to_anticraving",
    "Reason.for.discharge": "cov_reason_for_discharge",
}


def main():
    raw = requests.get(ARTICLE, timeout=300,
                       headers={"User-Agent": "Mozilla/5.0 (IRW-research)"})
    raw.raise_for_status()
    import io
    d = pd.read_excel(io.BytesIO(raw.content))

    items = [c for c in d.columns if re.match(r"^PDAT26_Item\.\d+$", str(c))]
    assert len(items) == 26, len(items)

    # Repeated measures: rank the assessments within each patient. method
    # "first" breaks the two tied (patient, day) pairs deterministically.
    day = "Days.between.admission.and.PDAT"
    assert d[day].notna().all()
    d = d.rename(columns={"Patient.ID": "id"})
    d["wave"] = (d.groupby("id")[day].rank(method="first").astype(int))
    assert not d.duplicated(["id", "wave"]).any()

    d = d.rename(columns=COVS)
    cov_cols = [c for c in COVS.values() if c in d.columns]

    long = d.melt(id_vars=["id", "wave"] + cov_cols, value_vars=items,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave"] + cov_cols]

    assert long["resp"].between(1, 5).all()
    assert long.groupby("item")["resp"].nunique().min() > 1
    assert not long.duplicated(["id", "item", "wave"]).any()

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "sirventruiz_2025_pdat.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"{path}: {n_id} ids x {n_it} items x {long['wave'].max()} max waves "
          f"= {len(long)} responses, resp {long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    main()
