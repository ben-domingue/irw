#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/6szgbkpzn8
# DOI: 10.17632/6szgbkpzn8 (dataset; no paper DOI on the record)
#   Islam, Md (2021). "Modifiable and nonmodifiable factors associated with anxiety,
#   depression, and stress after one year of the COVID-19 pandemic" [data set], Mendeley
#   Data, V1.
# Data: "Mental health after one year of Covid-19 pandemic_August 26, 2021_Analysis 1.sav":
#       1899 adults across Bangladesh's eight divisions (online survey, May-June 2021) x 115
#       columns. Variable labels name each item positionally ("Beck Anxiety 1", "LOT-R 3");
#       value labels give the anchors.
# License: CC BY 4.0 (Mendeley record).
#
# Item text: not shipped. Levels checked: variable labels are positional ("PHQ-9 4",
#   "Mindfulness 2"), value labels give anchors only; no codebook. Option text alone is not
#   shipped (#1770).
#
# Tables (item codes = the .sav names; ranges = the value labels):
#   islam_2021_bai    Q24_1-21  0-3  Beck Anxiety Inventory (0 not at all .. 3 severely)
#   islam_2021_lotr   Q25_1-10  0-4  Life Orientation Test-Revised, all ten items incl. the
#                                    four fillers (the file's Optimism = items 1, 4, 10,
#                                    Pessimism = 3, 7, 9)
#   islam_2021_pss4   Q26_1-4   0-4  Perceived Stress Scale-4 (0 never .. 4 very often)
#   islam_2021_phq9   Q27_1-9   0-3  PHQ-9
#   islam_2021_maas   Q29_1-5   1-6  Mindful Attention Awareness Scale, 5-item form
#                                    (1 almost always .. 6 almost never)
# Skipped: ID (NewID kept as id), consent (Q1), the PHQ functioning item Q28, SES score
#   (Q11, fractional), number/age of children, days since infection and treatment place
#   (conditional follow-ups), every total/category score, dummy codings, outlier
#   diagnostics (MAH_1, COO_1, ...), filter_$.
# Covariates (codes; labels in the .sav value labels): cov_sex (0 male, 1 female, 3 third
#   gender), cov_age, cov_education, cov_mental_history, cov_division, cov_urban,
#   cov_living_with, cov_profession, cov_frontliner, cov_married, cov_has_children,
#   cov_covid_infected, cov_family_covid, cov_family_covid_death, cov_vaccinated,
#   cov_vaccine_interest.

import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "islam_2021"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://data.mendeley.com/public-files/datasets/6szgbkpzn8/files/"
       "2c86e14c-526e-4787-a46a-801b126612d2/file_downloaded")

TABLES = {"islam_2021_bai": ("Q24", 21, range(0, 4)), "islam_2021_lotr": ("Q25", 10, range(0, 5)),
          "islam_2021_pss4": ("Q26", 4, range(0, 5)), "islam_2021_phq9": ("Q27", 9, range(0, 4)),
          "islam_2021_maas": ("Q29", 5, range(1, 7))}
COVS = {"Q2": "cov_sex", "Q3": "cov_age", "Q4": "cov_education", "Q5": "cov_mental_history",
        "Q6": "cov_division", "Q7": "cov_urban", "Q8": "cov_living_with",
        "Q9": "cov_profession", "Q10": "cov_frontliner", "Q13": "cov_married",
        "Q14": "cov_has_children", "Q17": "cov_covid_infected", "Q20": "cov_family_covid",
        "Q21": "cov_family_covid_death", "Q22": "cov_vaccinated", "Q23": "cov_vaccine_interest"}


def fetch() -> Path:
    p = RAW_DIR / "data.sav"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, meta = pyreadstat.read_sav(fetch())
    assert d.shape == (1899, 115), d.shape
    cols = {t: [f"{q}_{i}" for i in range(1, k + 1)] for t, (q, k, _) in TABLES.items()}
    items = {c for v in cols.values() for c in v}
    assert items <= set(d.columns)
    skipped = [c for c in d.columns if c not in items | set(COVS) | {"NewID"}]
    print(f"  skip {len(skipped)} columns: original ID, consent, Q28, SES, child/infection "
          "follow-ups, totals and categories, dummies, outlier diagnostics, filter")
    assert d["NewID"].is_unique
    d = d.rename(columns={"NewID": "id", **COVS})
    d["id"] = d["id"].astype(int)
    covs = list(COVS.values())
    for c in covs:
        if c != "cov_age":
            d[c] = d[c].astype("Int64")
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (_, _, rng) in TABLES.items():
        its = cols[name]
        for c in its:
            assert set(meta.variable_value_labels[c]) == set(map(float, rng)), c
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(list(rng)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
