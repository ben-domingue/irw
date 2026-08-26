"""Doherty (2023), Mendeley Data -- burnout in Irish consultant doctors (BICDIS).

Source: https://data.mendeley.com/datasets/95cmh2ftwk
DOI: 10.17632/95cmh2ftwk
Data: BICDIS.sav
License: CC BY 4.0

472 Irish consultant doctors surveyed in 2019, completing three instruments.
Surfaced by the 2026-08-25 OpenAIRE/Mendeley pass.

Tables written
--------------
doherty_2023_dass21      21 DASS-21 items,              0-3
doherty_2023_burnout     16-item burnout scale,         1-7
doherty_2023_bfi10       10 Big Five Inventory items,   1-5

Coding notes
------------
* **DASS-21 confirmed positively**, not inferred: the deposit's own
  `DASStotal` equals the plain sum of `DASS1`..`DASS21` on every complete
  case, and the items span exactly the DASS 0-3 scale.
* **The 16-item burnout block is described structurally rather than named.**
  The deposit carries `MBIsubscaleEE`/`MBIsubscaleC`/`MBIsubscalePA`, which
  suggests the MBI, but those three subscales do not sum to the total of
  `MBS1`..`MBS16` (they are presumably subset sums with reverse-coding), so
  the identification cannot be verified from the file and is not asserted.
  The items themselves are a clean 16-item, 1-7 ordinal block.
* **The BFI reverse-coded duplicates are dropped.** The file stores five
  items twice: `BFI1R` = 6 - `BFI1` exactly (and likewise for 3, 4, 5, 7),
  confirmed on every row. Shipping both would put the same response in the
  table twice under two item names, so only the raw `BFI1`..`BFI10` are
  exported.
* All derived columns are excluded: `DASStotal`, `DASSsubscale*`,
  `MBIsubscale*`, `BFIextraversion` and the other four BFI trait scores.
* Covariates are the deposit's coarse practice descriptors. `Speciality` has
  only 10 categories over 472 respondents, so it carries no meaningful
  re-identification risk.
"""

import io
import os

import pandas as pd
import requests

API = "https://data.mendeley.com/public-api/datasets/95cmh2ftwk"
OUTDIR = "irw_output"

SCALES = {
    "dass21":  ([f"DASS{i}" for i in range(1, 22)], (0, 3)),
    "burnout": ([f"MBS{i}" for i in range(1, 17)],  (1, 7)),
    # BFI1..BFI10 only -- BFI1R/3R/4R/5R/7R are stored reversals of the same
    # five items, verified as 6 - raw on every row.
    "bfi10":   ([f"BFI{i}" for i in range(1, 11)],  (1, 5)),
}

COVS = {
    "Age2": "cov_age_band",
    "Gender": "cov_gender",
    "Speciality": "cov_speciality",
    "Exercise": "cov_exercise",
    "MHP": "cov_mental_health_problem",
    "ADT": "cov_alcohol_drug_treatment",
    "HSE": "cov_employer_type",
    "HoursTotal": "cov_weekly_hours",
    "Oncallfreq": "cov_oncall_frequency",
    "face2face": "cov_face_to_face_sessions",
    "Disciplinary": "cov_disciplinary_history",
    "Lawsuit": "cov_lawsuit_history",
    "Satisfied": "cov_job_satisfaction",
}


def _load() -> pd.DataFrame:
    meta = requests.get(API, timeout=60).json()
    sav = [f for f in meta["files"] if f["filename"].endswith(".sav")]
    assert len(sav) == 1, [f["filename"] for f in meta["files"]]
    raw = requests.get(sav[0]["content_details"]["download_url"], timeout=300,
                       headers={"User-Agent": "Mozilla/5.0 (IRW-research)"})
    raw.raise_for_status()
    # convert_categoricals=False so labelled variables keep their numeric codes.
    return pd.read_spss(io.BytesIO(raw.content), convert_categoricals=False)


def main():
    d = _load().rename(columns={"RespondentID": "id"})
    assert d["id"].is_unique

    # Positive check on the DASS block before trusting it.
    dass = [f"DASS{i}" for i in range(1, 22)]
    s = d[dass].sum(axis=1)
    ok = d["DASStotal"].notna() & s.notna()
    assert (s[ok] - d["DASStotal"][ok]).abs().max() < 1e-6, "DASStotal != sum(items)"

    # And that the R columns really are reversals, before dropping them.
    for n in (1, 3, 4, 5, 7):
        pair = (d[f"BFI{n}"] + d[f"BFI{n}R"]).dropna()
        assert (pair == 6).all(), f"BFI{n}R is not 6 - BFI{n}"

    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    os.makedirs(OUTDIR, exist_ok=True)
    for name, (items, (lo, hi)) in SCALES.items():
        missing = [c for c in items if c not in d.columns]
        assert not missing, (name, missing)

        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long["id"] = long["id"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]

        assert long["resp"].between(lo, hi).all(), (
            name, long["resp"].min(), long["resp"].max())
        assert long.groupby("item")["resp"].nunique().min() > 1
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"doherty_2023_{name}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
