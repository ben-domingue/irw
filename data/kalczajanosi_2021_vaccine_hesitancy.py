"""Three-dimensional COVID-19 vaccine hesitancy scale.

Source: Kalcza-Janosi, Kotta & Marschalko (2021), figshare
10.6084/m9.figshare.15090891.v1, CC BY 4.0. Single .sav, 1,503 respondents
x 62 columns.

Three subscales ship as separate tables, following the KEPAQ/KORQ precedent:

  kalczajanosi_2021_covid_fear         CV_FEAR1-14
  kalczajanosi_2021_vaccine_skepticism CV_skept1-11
  kalczajanosi_2021_covid_risk         CV_risk1-12

All three are 1-5 Likert.

Four columns are computed and are NOT items -- `Scepticism` (5-25), `Risk`
(6-30), `Fear` (4-20) and `Vaccine_hesitancy_total` (15-75) are subscale and
total scores. Their ranges give them away: each is a sum over a *subset* of
its subscale's items, so none of them is even on the item response scale.
Shipping them would put a deterministic function of the other items into the
item set. They are dropped rather than kept as covariates, because the sums
are reproducible from the items that ship.

`disease` is a free-text field naming the respondent's chronic condition (241
distinct values). It is dropped: it is unstructured text, not a covariate
value, and free text in a health context is exactly where identifying detail
tends to leak.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

ARTICLE = 15090891
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SCALES = {
    "kalczajanosi_2021_covid_fear": (r"^CV_FEAR\d+$", 14),
    "kalczajanosi_2021_vaccine_skepticism": (r"^CV_skept\d+$", 11),
    "kalczajanosi_2021_covid_risk": (r"^CV_risk\d+$", 12),
}
COVARIATES = {
    "age": "cov_age", "gender": "cov_gender", "country": "cov_country",
    "education": "cov_education",
    "Perceived_health_status": "cov_perceived_health",
    "chronic_disease": "cov_chronic_disease", "Smoking": "cov_smoking",
    "flu_vaccine_past": "cov_flu_vaccine_past",
    "optional_vaccine_past": "cov_optional_vaccine_past",
    "diagnosed_Covid19": "cov_diagnosed_covid19",
    "symptoms_severity": "cov_symptoms_severity",
    "hospitalization_Covid19": "cov_hospitalization_covid19",
    "vaccine_intention": "cov_vaccine_intention",
    "vaccine_type": "cov_vaccine_type",
    "Weight_kg": "cov_weight_kg", "Hight_cm": "cov_height_cm",
    # Collapsed recodes the authors analysed alongside the originals: country
    # 1-5 -> 1-3, vaccine_intention 1-8 -> 1-3. Kept as covariates in their own
    # right rather than dropped, since the collapse rule is not recoverable
    # from the raw codes.
    "country_merged": "cov_country_merged",
    "vaccine_intention_merged": "cov_vaccine_intention_merged",
}
# Computed scores, not items. See the module docstring.
COMPOSITES = ["Scepticism", "Risk", "Fear", "Vaccine_hesitancy_total"]
DROP = ["disease", "time"]


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    meta = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                        timeout=120).json()
    f = next(x for x in meta["files"] if x["name"].lower().endswith(".sav"))
    r = requests.get(f["download_url"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["name"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    df, _meta = pyreadstat.read_sav(fetch_raw(path), apply_value_formats=False)
    df = df.rename(columns={"id": "person_id"})

    item_cols = {}
    for table, (pat, n) in SCALES.items():
        cols = [c for c in df.columns if re.match(pat, c)]
        assert len(cols) == n, f"{table}: expected {n} items, found {len(cols)}"
        item_cols[table] = cols

    # Book-balancing: every source column is an item, a covariate, a known
    # composite, or an explicit drop. Anything else stops the run rather than
    # being silently ignored.
    accounted = (set(sum(item_cols.values(), [])) | set(COVARIATES)
                 | set(COMPOSITES) | set(DROP) | {"person_id"})
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVARIATES)
    covs = [v for v in COVARIATES.values()]
    df["id"] = df["person_id"].astype(int)

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, cols in item_cols.items():
        long = (df.melt(id_vars=["id"] + covs, value_vars=cols,
                        var_name="item", value_name="resp")
                  .dropna(subset=["resp"]))
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        assert long["id"].nunique() >= 100, table
        assert long["item"].nunique() > 1, table
        assert long["resp"].between(1, 5).all(), f"{table}: expected 1-5"
        long.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        print(f"{table}: {len(long):,} rows, {long['id'].nunique():,} ids, "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
