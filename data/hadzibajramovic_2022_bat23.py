#!/usr/bin/env python3
# Source: https://springernature.figshare.com/articles/dataset/Additional_file_7_of_Shortening_of_the_Burnout_Assessment_Tool_BAT_from_23_to_12_items_using_content_and_Rasch_analysis/19396179
# DOI: 10.1186/s12889-022-12946-y
#   Hadzibajramovic, E., Schaufeli, W., & De Witte, H. (2022). Shortening of the
#   Burnout Assessment Tool (BAT) -- from 23 to 12 items using content and Rasch
#   analysis. BMC Public Health, 22, 560. (Open access, PMC8939057; read.)
# Data: the article's Additional files 5-8 (figshare 10.6084/m9.figshare.19396173,
#       .19396176, .19396179, .19396182). File 7 (MOESM7_ESM.xlsx, figshare file
#       34460628) is the complete-case analysis file: 2,978 workers (NL 1500,
#       Flanders 1478) x age, SEX, country, W_EX1-8, W_MD1-5, W_CC1-5, W_EC1-5.
#       Files 5 and 6 are the paper's two random 800-person stratified subsamples
#       (every row matches a row of file 7 on SEX, country and all 23 items; age is
#       median-split there), and file 8 is file 7 restricted to the 12 BAT12 items
#       (cell-for-cell identical). So only file 7 is read; 5, 6 and 8 add no people
#       and no responses.
# License: CC BY 4.0 (+ CC0 for data; figshare record "CC BY + CC0").
#
# Item text: not shipped. Levels checked: xlsx headers are codes only (no variable
#   or value labels, no codebook in the deposit); the 23 items are in the paper's
#   Additional file 1, but the BAT is blocked in
#   itemtext/instrument_rights_register.csv.
#
# Shipped: hadzibajramovic_2022_bat23 -- BAT-23 (original Dutch version), work-
#   related: exhaustion W_EX1-8, mental distance W_MD1-5, cognitive impairment
#   W_CC1-5, emotional impairment W_EC1-5; 1 = never ... 5 = always (paper,
#   Methods). Complete cases only (as deposited).
# Covariates: cov_age (years), cov_sex (SEX 1/2 as deposited; the paper does not
#   give the coding), cov_country (1 = the Netherlands, 2 = Flanders -- decoded from
#   the paper's NL = 1500 / FL = 1478 against the file's 1500/1478 counts).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "hadzibajramovic_2022"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/34460628"   # Additional file 7
NAME = "hadzibajramovic_2022_bat23"
ITEMS = ([f"W_EX{i}" for i in range(1, 9)] + [f"W_MD{i}" for i in range(1, 6)]
         + [f"W_CC{i}" for i in range(1, 6)] + [f"W_EC{i}" for i in range(1, 6)])
COVS = {"age": "cov_age", "SEX": "cov_sex", "country": "cov_country"}


def fetch() -> Path:
    p = RAW_DIR / "MOESM7_ESM.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch())
    assert d.shape == (2978, 26) and d.columns.tolist() == list(COVS) + ITEMS, d.columns
    assert d["country"].value_counts().to_dict() == {1: 1500, 2: 1478}
    d = d.rename(columns=COVS)
    d.insert(0, "id", range(1, len(d) + 1))      # no id column in the deposit
    covs = list(COVS.values())
    t = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item", value_name="resp")
    assert t["resp"].notna().all() and t["resp"].isin(range(1, 6)).all()
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any()
    pv = {i: {1, 2, 3, 4, 5} for i in ITEMS}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
