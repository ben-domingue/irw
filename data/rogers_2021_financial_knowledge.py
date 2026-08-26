"""Rogers (2021), Mendeley Data -- financial knowledge in Brazilian university
students, analysed by item response theory.

Source: https://data.mendeley.com/datasets/fzw7dthwh6
DOI: 10.17632/fzw7dthwh6
License: CC BY 4.0

232 university students answering a 13-item financial-knowledge test, scored
right/wrong.

Tables written
--------------
rogers_2021_financial_knowledge   232 students x 13 items, 0/1

Coding notes
------------
* Achievement rather than self-report: `resp` is 0/1 correctness. The chosen
  options are not deposited -- the Stata labels point to the item stems in the
  companion `FinalForm.pdf`, which is where item text would come from.
* `N` is the deposit's own student identifier and is used as `id`.
* The `*_C` columns are the paper's collapsed recodes of the demographic
  variables they follow; the uncollapsed originals are shipped as covariates
  and the recodes are skipped.
* `ESCORETRI` / `ESCORETRI_C` are the estimated IRT score and its banding.
"""

import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

DOI = "10.17632/fzw7dthwh6"
DATASET, VERSION = "fzw7dthwh6", 1
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
TABLE = "rogers_2021_financial_knowledge"
ITEMS = [f"Q{i}" for i in range(1, 14)]
COVS = {"PERIODO": "cov_year_of_study", "CURSO": "cov_major",
        "SEXO": "cov_sex", "IDADE": "cov_age_band",
        "RENDA": "cov_family_income", "N_DEPEN": "cov_dependents",
        "ESCOL_PAI": "cov_father_education",
        "ESCOL_MAE": "cov_mother_education", "RACA": "cov_race",
        "TRABALHO": "cov_works_in_finance"}
SKIP = {"CURSO_C": "collapsed recode of CURSO",
        "IDADE_C": "collapsed recode of IDADE",
        "RENDA_C": "collapsed recode of RENDA",
        "DEPEN": "collapsed recode of N_DEPEN",
        "ESCOL_PAI_C": "collapsed recode of ESCOL_PAI",
        "ESCOL_MAE_C": "collapsed recode of ESCOL_MAE",
        "RACA_C": "collapsed recode of RACA",
        "ESCORETRI": "estimated IRT score",
        "ESCORETRI_C": "banded IRT score"}


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
    open("/tmp/rogers_finknow.dta", "wb").write(raw.content)
    d = pd.read_stata("/tmp/rogers_finknow.dta", convert_categoricals=False)

    assert set(ITEMS) <= set(d.columns)
    d = d.rename(columns={"N": "id", **COVS})
    long = d.melt(id_vars=["id"] + list(COVS.values()), value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + list(COVS.values())]

    assert long["resp"].isin([0, 1]).all()
    assert not long.duplicated(["id", "item"]).any()
    assert long.groupby("item")["resp"].nunique().min() > 1
    checks = run_qc(long)
    bad = [c for c in checks if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    for c in d.columns:
        if c in ITEMS or c in COVS.values() or c == "id":
            continue
        assert c in SKIP, f"unaccounted source column: {c}"
        print(f"  skip {c}: {SKIP[c]}")

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f"{TABLE}.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"\n{path}: {n_id} students x {n_it} items = {len(long)} "
          f"responses, density {len(long) / (n_id * n_it):.3f}, "
          f"mean correct {long['resp'].mean():.3f}")


if __name__ == "__main__":
    main()
