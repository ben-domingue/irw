#!/usr/bin/env python3
# Source: https://doi.org/10.34894/Y3H5GX
# DOI: 10.34894/Y3H5GX (dataset, DataverseNL; no paper DOI on the record)
#   Sijbrandij, M. (2018). "Quality of life in Indonesian women suspected of breast
#   cancer and the general population" [data set]. DataverseNL.
# Data: DATA.xls (downloaded format=original; DATA.txt is the same table): 603
#       Indonesian women -- 132 with breast-cancer symptoms, 471 from the general
#       population -- x group, respondent code, age (+ band), residence, education,
#       income, EQ-5D-5L descriptive system (5 items) + EQ-VAS, WHOQOL-BREF item1-26,
#       four WHOQOL domain scores and an EQ-5D utility. README.txt documents every
#       column and the EQ-5D-5L codes (1 no problems ... 5 extreme problems/unable).
# License: CC0 1.0 (DataverseNL record).
#
# Item text: not shipped. Levels checked: xls headers are codes (item1-26,
#   mobility5l ...); README gives EQ-5D-5L option labels only; no WHOQOL wording. Both
#   instruments are blocked in itemtext/instrument_rights_register.csv (WHOQOL family;
#   EQ-5D).
#
# Tables:
#   sijbrandij_2018_whoqol_bref  item1-26 (WHOQOL-BREF, 1-5, as stored -- the README does
#                                not say whether items 3, 4, 26 were reversed in storage)
#   sijbrandij_2018_eq5d5l       mobility5l, selfcare5l, usualactivities5l,
#                                paindiscomfort5l, anxietydepression5l (1-5)
# Dropped cells: two non-integer WHOQOL values (item3 = 3.5, item25 = 3.714...),
#   imputation, not responses.
# Not shipped: vas5l (single 0-100 rating), phys/psych/soc/envir_dom100 (domain scores),
#   utility (value-set transform), age_code (band of age).
# Covariates: cov_group (type_data: bc = breast-cancer symptom group, public = general
#   population), cov_age, cov_residence (rural/urban), cov_education (low/middle/high),
#   cov_income (low <2M, middle 2-4M, high >4M IDR). id = resp_code (unique).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "sijbrandij_2018"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.nl/api/access/datafile/11676?format=original"
TABLES = {"sijbrandij_2018_whoqol_bref": [f"item{i}" for i in range(1, 27)],
          "sijbrandij_2018_eq5d5l": ["mobility5l", "selfcare5l", "usualactivities5l",
                                     "paindiscomfort5l", "anxietydepression5l"]}
COVS = {"type_data": "cov_group", "age": "cov_age", "place_code": "cov_residence",
        "educationlevel_code": "cov_education", "income_code": "cov_income"}
SKIP = ["vas5l", "phys_dom100", "psych_dom100", "soc_dom100", "envir_dom100", "utility",
        "age_code"]


def fetch() -> Path:
    p = RAW_DIR / "DATA.xls"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch())
    assert d.shape == (603, 44) and d["resp_code"].is_unique
    items = [c for v in TABLES.values() for c in v]
    assert set(d.columns) == set(items) | set(COVS) | set(SKIP) | {"resp_code"}
    print(f"  [skip] {SKIP}: single VAS rating, domain scores, utility, age band")
    d = d.rename(columns={"resp_code": "id", **COVS})
    d["id"] = d["id"].astype(str)
    covs = list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, its in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        frac = t["resp"] % 1 != 0
        print(f"  {name}: dropped {frac.sum()} non-integer cell(s): "
              f"{t.loc[frac, ['item', 'resp']].values.tolist()}")
        t = t[~frac]
        assert t["resp"].isin(range(1, 6)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        pv = {i: {1, 2, 3, 4, 5} for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:160]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
