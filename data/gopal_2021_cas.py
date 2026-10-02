#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/fkgf3fwnpz (version 2)
# DOI: 10.1016/j.dib.2021.107052
#   Raghavendra, N. K., Gopal, S., & Munuswamy, J. (2021). "Data set on
#   impact of COVID-19 on mental health of internal migrant workers in
#   India: Corona Virus Anxiety Scale (CAS) approach." Data in Brief, 36,
#   107052. (Open access, PMC8114112.)
#   Dataset: Suresh G[opal], Naveen Kumar, M Jothi (2021). Mendeley Data v2,
#   https://doi.org/10.17632/fkgf3fwnpz.2
# Data: "Migrant Workers Anxiety data.csv" (1,350 x 13). Telephone
#       interviews with internal migrant workers across India, June-August
#       2020.
#       The deposit's other file, "Master Table Migrant with Code.xlsx",
#       is NOT used for responses: its "Data set" sheet disagrees with the
#       CSV on 523-578 cells per CAS item (and has two "c" cells), and only
#       the CSV reproduces the paper. The CSV's item means 1.66/1.71/1.74/
#       1.76/1.65 equal the paper's Table 3 and its covariate counts equal
#       Table 2 (both asserted). The xlsx "Code" sheet is used for item text.
# License: CC BY 4.0 (Mendeley Data API, data_licence short_name).
#
# Instrument: Coronavirus Anxiety Scale (Lee 2020), 5 items, as worded in
#   the authors' interview schedule. "How often have you experienced the
#   following activities over the last 2 weeks?" 0 Not at all, 1 Rare, less
#   than a day, 2 Several days, 3 More than a week, 4 nearly every day over
#   last 2 weeks (xlsx "Code" sheet; the paper's Table 1 lists the same five
#   options and Table 3 gives each item's range as 0-4). Asserted per item.
#   Item codes are the source column names CAS1-CAS5.
# Item text: shipped (automated_finding/itemtext_output/gopal_2021_cas__items.csv)
#   from the xlsx "Code" sheet, which gives each CAS column its English stem
#   and the five option labels. Both label levels checked: CSV/xlsx carry no
#   variable or value labels; the codebook sheet is the label source.
#
# Checked and kept: 177 rows repeat another row's 5 items and 6 coded
#   covariates. With five 0-4 items and six 2-3 level covariates, chance
#   coincidence is expected at this N, and the paper's N of 1,350 counts
#   them, so none is treated as a repeated submission.
# Dropped: TotalCAS (sum of CAS1-5, asserted), ResID (row counter 1-1350),
#   COVIDInfec (codebook says 1 = tested positive, 2 = not; the file holds
#   0/1, and nothing pins which is which).
# id: row index (ResID is 1..1350 in order, asserted).
# Covariates, decoded from the paper's Table 2 counts (the codebook's 1/2/3
#   codes do not match the file's 0/1 coding for gender and marital status):
#   cov_age_group (1 <=30, 2 31-40, 3 41+), cov_gender (0 male, 1 female),
#   cov_marital (0 married/partnered, 1 unmarried/single), cov_education
#   (1 primary, 2 secondary, 3 no formal education -- the paper's Table 2
#   order, which differs from the codebook's), cov_income (1 <= Rs 15,000,
#   2 Rs 15,001-20,000, 3 > Rs 20,000 a month).

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://data.mendeley.com/public-files/datasets/fkgf3fwnpz/files/"
       "ac763764-27a3-461f-b5a9-0c5f8d16751a/file_downloaded")
TABLE = "gopal_2021_cas"
ITEMS = [f"CAS{i}" for i in range(1, 6)]
COVS = {"Age": "cov_age_group", "Gender": "cov_gender",
        "Maritalstatus": "cov_marital", "Education": "cov_education",
        "Income": "cov_income"}
PERMITTED = set(range(0, 5))


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content), encoding="utf-8-sig")
    assert d.shape == (1350, 13), d.shape
    known = {"ResID", "COVIDInfec", "TotalCAS"} | set(ITEMS) | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert d["ResID"].tolist() == list(range(1, 1351))
    assert (d[ITEMS].sum(axis=1) == d["TotalCAS"]).all()
    # Reproduces the paper (Table 3 means, Table 2 group sizes).
    assert d[ITEMS].mean().round(2).tolist() == [1.66, 1.71, 1.74, 1.76, 1.65]
    assert d["Age"].value_counts().to_dict() == {1: 728, 2: 345, 3: 277}
    assert d["Gender"].value_counts().to_dict() == {0: 758, 1: 592}
    assert d["Maritalstatus"].value_counts().to_dict() == {0: 823, 1: 527}
    assert d["Education"].value_counts().to_dict() == {1: 786, 2: 446, 3: 118}
    assert d["Income"].value_counts().to_dict() == {2: 877, 1: 415, 3: 58}

    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())
    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    assert not long["resp"].isna().any()
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - PERMITTED
        assert not bad, (it, bad)
    pv = {i: PERMITTED for i in ITEMS}
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() == 1350 and long["item"].nunique() == 5
    fails = [(c.name, c.detail) for c in run_qc(long, permitted_values=pv)
             if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
