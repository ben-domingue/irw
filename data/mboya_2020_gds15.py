"""Mboya (2020), Mendeley Data -- depression in an elderly population
(Kilimanjaro, Tanzania).

Source: https://data.mendeley.com/datasets/btrrmwtfmh
DOI: 10.17632/btrrmwtfmh
License: CC BY 4.0

304 adults aged 60+ screened with the 15-item Geriatric Depression Scale.

Tables written
--------------
mboya_2020_gds15   304 respondents x 15 items, 0/1

Coding notes
------------
* The GDS-15 is a yes/no screen, so `resp` is dichotomous. The `0`/`1`
  suffixes on the source column names (`satisfy0`, `drop1`, ...) record which
  answer is the depression-consistent one, not the response itself; they are
  kept in the item ids so the keying stays visible and item text can join.
* `intid` is the deposit's own respondent number and is used as `id`.
* `gdsgrp` is the derived above/below-threshold classification and is not an
  item; nor are the clinical history and social-participation variables,
  which ship as covariates.
"""

import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

DOI = "10.17632/btrrmwtfmh"
DATASET, VERSION = "btrrmwtfmh", 1
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
TABLE = "mboya_2020_gds15"

ITEMS = ["satisfy0", "drop1", "feel1", "bored1", "spirt0", "fraid1", "hapy0",
         "hepless1", "stay1", "memo1", "alive0", "worth1", "energy0",
         "hopless1", "better1"]
COVS = {"age": "cov_age", "sex": "cov_sex",
        "age_cat_1": "cov_age_band", "edulevel_cat_1": "cov_education",
        "occupation": "cov_occupation", "marstat": "cov_marital_status",
        "living": "cov_living_alone", "social_grp": "cov_social_group",
        "beendiagnosedwithhypertension": "cov_hypertension",
        "beendiagnosedwithasthma": "cov_asthma",
        "beendiagnosedwithdiabetes": "cov_diabetes",
        "beendiagnosedwithstroke": "cov_stroke",
        "stressfulevent": "cov_stressful_event",
        "cognitiveimpairment": "cov_cognitive_impairment",
        "depressionhistory": "cov_depression_history",
        "consumedalcoholicdrinkwithin12mo": "cov_alcohol",
        "everusedtobacco": "cov_tobacco",
        "takepartinsocialactivity": "cov_social_activity",
        "takepartinreligiousactivities": "cov_religious_activity",
        "peopleclosetoyou": "cov_close_contacts",
        "concernpeopleshow": "cov_perceived_concern",
        "practicalhelp": "cov_practical_help"}
SKIP = {"gdsgrp": "derived above/below-threshold GDS classification"}


def main():
    s = requests.Session()
    s.headers.update(UA)
    listing = s.get(f"https://data.mendeley.com/public-api/datasets/"
                    f"{DATASET}/files?folder_id=root&version={VERSION}",
                    timeout=120).json()
    hit = [f for f in listing if f["filename"].lower().endswith(".dta")]
    assert len(hit) == 1, [f["filename"] for f in listing]
    raw = s.get(hit[0]["content_details"]["download_url"], timeout=600)
    raw.raise_for_status()
    open("/tmp/mboya_gds.dta", "wb").write(raw.content)
    d = pd.read_stata("/tmp/mboya_gds.dta", convert_categoricals=False)

    assert set(ITEMS) <= set(d.columns), sorted(set(ITEMS) - set(d.columns))
    d = d.rename(columns={"intid": "id", **COVS})
    covs = sorted(set(COVS.values()))

    long = d.melt(id_vars=["id"] + covs, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]

    assert long["resp"].isin([0, 1]).all()
    assert not long.duplicated(["id", "item"]).any()
    assert long.groupby("item")["resp"].nunique().min() > 1
    checks = run_qc(long)
    bad = [c for c in checks if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    for c in d.columns:
        if c in ITEMS or c in covs or c == "id":
            continue
        assert c in SKIP, f"unaccounted source column: {c}"
        print(f"  skip {c}: {SKIP[c]}")

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f"{TABLE}.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"\n{path}: {n_id} respondents x {n_it} items = {len(long)} "
          f"responses, density {len(long) / (n_id * n_it):.3f}")


if __name__ == "__main__":
    main()
