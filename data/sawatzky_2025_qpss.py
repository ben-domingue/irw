#!/usr/bin/env python3
# Source: https://doi.org/10.5683/SP3/A4JG2R
# DOI: 10.1371/journal.pone.0320306
#   Sawatzky, R., Schick-Makaroff, K., Ratner, P. A., Kwon, J.-Y.,
#   Whitehurst, D. G. T., Ohlen, J., Maybee, A., Stajduhar, K., Zetes-
#   Zanatta, L., & Cohen, S. R. (2025). "Did a digital quality of life (QOL)
#   assessment and practice support system in home health care improve the
#   QOL of older adults living with life-limiting conditions and of their
#   family caregivers? A mixed-methods pragmatic randomized controlled
#   trial." PLOS ONE. (PMC12054893)
#   Data: Sawatzky, R. (2025). "Replication Data for: Quality of Life
#   Assessment and Practice Support System Project." Borealis.
# Data: Borealis datafile 922779, QPSS_RCTData.sav (format=original; 1,745
#       rows x 93 columns, long format: one row per participant x two-month
#       assessment period; 331 home-care patients and 111 family caregivers,
#       British Columbia, ClinicalTrials.gov NCT02940951).
# License: CC BY 4.0 (Borealis dataset licence, API).
#
# Item text: not shipped. Variable labels carry the full English stem of
#   every MQOL-E and QOLLTI-F v3 item ("MQOL-E Over the past two days (48
#   hours), I was depressed: (Q4)"); there are no value labels (the 0-10
#   anchors are item-specific and not in the deposit). Not built because
#   both instruments are developer-copyrighted (McGill QOL family, Cohen et
#   al.) and are not yet in itemtext/instrument_rights_register.csv; the
#   stems are one step away once rights are checked.
#
# Tables (item codes are the source column names):
#   sawatzky_2025_mqol_e  MQOLA, MQOL1a, MQOL2-MQOL22: McGill Quality of Life
#       Questionnaire - Expanded, completed by patients. MQOLA is the
#       single-item global QOL rating.
#   sawatzky_2025_qollti_f  QOLFA, QOLF1-QOLF17: Quality of Life in
#       Life-Threatening Illness - Family Carer Version 3, completed by
#       family caregivers. QOLFA is the global item.
#   Both are scored 0 to 10 with item-specific anchors (paper, Table 1 and
#   Methods). Items are stored as answered: the negatively worded items
#   (e.g. MQOL4 "I was depressed") are not reverse-coded in the file (they
#   correlate negatively with the global item). The paper counts 20 MQOL-E
#   and 16 QOLLTI-F scored items plus the global item; the file holds 22 and
#   17, and all are shipped.
#   wave: assessment sequence number within participant (1..7), in file
#   order, which is sorted by Period_2Mo within every participant (asserted).
#   The two-month period itself is kept as cov_period, because 17
#   participants have two assessments inside the same period bin.
#
# Dropped:
#   - One caregiver row holding MQOL-E answers (the MQOL-E is the patient
#     instrument per the paper); not shipped.
#   - 7 rows with no item answered.
#   - MPLUSID: study participant number; replaced by a person index.
#   - ICD_01 .. ICD_23 (19 diagnosis-chapter flags) and the 19 ethnicity
#     dummies plus Ethnicity_other (sentinels -99/-98/-96): not carried.
#   - DaysSinceStart_min, P_FollowUp: trial bookkeeping.
# id: person index (1..442), shared across the two tables' row order.
# Covariates: cov_site (study site code), cov_group (2 = group A, 3 = group G
#   -- randomised arm, deposit codes), cov_period (two-month period, 1-7),
#   cov_gender (1 male, 2 female), cov_age (whole years, floored from the
#   file's decimal age), cov_income (1-5 bands), cov_born_canada (0/1),
#   cov_marital (1-4), cov_education (1-4).

import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://borealisdata.ca/api/access/datafile/922779?format=original"

MQOL = ["MQOLA", "MQOL1a"] + [f"MQOL{i}" for i in range(2, 23)]
QOLF = ["QOLFA"] + [f"QOLF{i}" for i in range(1, 18)]
TABLES = {"sawatzky_2025_mqol_e": (MQOL, 1.0),
          "sawatzky_2025_qollti_f": (QOLF, 2.0)}
COVS = {"Site": "cov_site", "Group": "cov_group",
        "Period_2Mo": "cov_period", "Gender2": "cov_gender",
        "Age_Valid": "cov_age", "Income": "cov_income",
        "BornCan": "cov_born_canada", "Marital_4C": "cov_marital",
        "Educ_valid_4C": "cov_education"}
ETHNIC = {"Aboriginal", "North_American", "Brit_Isles", "French",
          "Euro_West", "Euro_South", "Euro_East", "Euro_North", "Euro_Other",
          "Caribbean", "South_American", "African", "Asian", "Asia_East",
          "Asia_SE", "Asia_South", "Asia_Mid_Central", "Asia_Other",
          "Oceanian", "Ethnicity_other"}
ICD = {f"ICD_{k:02d}" for k in (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14,
                                15, 16, 20, 21, 22, 23)}
OTHER_DROPPED = {"MPLUSID", "MSDATA_P_type", "DaysSinceStart_min",
                 "P_FollowUp"}
ALLOWED = set(range(0, 11))


def load():
    r = requests.get(URL, headers=UA, timeout=180)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (1745, 93), d.shape

    # Balance the books.
    known = set(MQOL) | set(QOLF) | set(COVS) | ETHNIC | ICD | OTHER_DROPPED
    assert set(d.columns) == known, set(d.columns) ^ known
    assert not d.duplicated().any()
    assert d.groupby("MPLUSID", sort=False)["Period_2Mo"].apply(
        lambda s: s.is_monotonic_increasing).all()
    assert d.groupby("MPLUSID")["MSDATA_P_type"].nunique().max() == 1
    # Patients never answer the caregiver form; one caregiver row has MQOL.
    pat = d["MSDATA_P_type"] == 1.0
    assert not d.loc[pat, QOLF].notna().any().any()
    stray = (~pat) & d[MQOL].notna().any(axis=1)
    assert stray.sum() == 1

    d = d.copy()
    d["id"] = pd.factorize(d["MPLUSID"])[0] + 1
    d["wave"] = d.groupby("MPLUSID", sort=False).cumcount() + 1
    d["Age_Valid"] = np.floor(d["Age_Valid"])
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, ptype) in TABLES.items():
        sub = d[d["MSDATA_P_type"] == ptype]
        long = sub.melt(id_vars=["id", "wave"] + cov_cols, value_vars=its,
                        var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - ALLOWED
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp", "wave"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "wave", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its)
        pv = {i: ALLOWED for i in its}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} waves={long['wave'].max()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
