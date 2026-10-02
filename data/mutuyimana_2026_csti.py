#!/usr/bin/env python3
# Source: https://zenodo.org/records/20385027
# DOI: 10.1371/journal.pone.0358482
#   Mutuyimana, C., & Maercker, A. (2026). "Eastern African expressions of
#   suffering: A new Cultural Scripts of Trauma Inventory." PLOS One.
#   (Read from Europe PMC full text, PMC13614634; its Data Availability
#   statement names this deposit. The deposit has no related identifiers.)
#   Dataset: Mutuyimana, C. (2026). Cross validation of Cultural Scripts of
#   Trauma Inventory, Clinical Aspects of Historical Trauma Questionnaire
#   and ... Zenodo. https://doi.org/10.5281/zenodo.20385027
# Data: "Quantitative Dataset.xlsx", one sheet "DATASET AND CODES" (1,210
#       rows x 204 columns). Row 1 is the deposit's codebook -- the response
#       labels and instrument name for each block, written above its first
#       column -- row 2 the variable names, rows 3+ the 1,208 respondents
#       (online survey, Rwanda/Uganda/Tanzania/Kenya; paper N = 1,208).
# License: CC BY 4.0 (Zenodo API).
#
# Item text: not shipped. Both levels checked: the sheet has variable names
#   only (no stems) and a per-block response-label row. The 71 pre-CSTI items
#   are in the paper's S4 File (initial pool) and the final 15 in S5 File;
#   the other instruments are published scales. Not data_labels-based.
#
# Ranges: every block's response set is printed in the deposit's codebook
# row (asserted against the observed values below) and, where the paper
# describes the measure, agrees with it: CSTI 0 never .. 4 always (paper;
# codebook 0 strongly disagree .. 4 strongly agree -- same 0-4 set), ITQ
# 0-4, CAHTQ 0-4, EPIL 1-7, GSE 1-5 (nine highest-loading items, per the
# paper), SV 1-7. The SV codebook cell lists 1..6 and then "1:Absolutely
# true", an evident typo for 7; 1-7 is asserted. Helplessness, Social Axioms
# and Personal Mastery are not described in the paper; their sets come from
# the codebook row alone.
#
# Tables (item codes are the source column names, except PMS4 -- see below):
#   mutuyimana_2026_trauma_exposure  TE1-TE17     0 not happened, 1 heard
#                                    about, 2 witnessed, 3 experienced
#   mutuyimana_2026_csti     CSTI1-CSTI71  pre-CSTI item pool (0-4); the
#                            paper's final 15-item CSTI is a subset
#   mutuyimana_2026_cahtq    CAHTQ1-20  Clinical Aspects of Historical
#                            Trauma Questionnaire (0-4)
#   mutuyimana_2026_itq      PTSD1-9, DSO1-9  International Trauma
#                            Questionnaire, one instrument (0-4)
#   mutuyimana_2026_helplessness  HQ1-HQ10 (1-7)
#   mutuyimana_2026_social_axioms SAQ1-SAQ15 (1-5)
#   mutuyimana_2026_epil     PL1-PL7  Existential Scale of the Purpose in
#                            Life Questionnaire (1-7)
#   mutuyimana_2026_gse      GSE1-GSE9 (1-5)
#   mutuyimana_2026_subjective_vitality  SV1-SV7 (1-7)
#   mutuyimana_2026_personal_mastery     PMS1-PMS7 (1-5)
#   The PMS block's fourth column has a blank header between PMS3 and PMS5;
#   it is named PMS4 here, and PMSTotal equals the sum of all seven
#   (asserted). One trailing space is stripped from "SAQ1 ".
#
# Dropped: the totals (TETotal, CSTITotal, CAHTQTotal, PTSDTotal, DSOTotal,
#   HQTotal, SAQTotal, PLTotal, GSETotal, SVTotal, PMSTotal). Each is
#   asserted to equal its block's sum except CSTITotal, which does not equal
#   the 71-item sum and is not documented; it is dropped unasserted.
# id: row index. "No" is a 1..1208 sequence (asserted) and is not shipped.
# Covariates: cov_birth_year (as entered; 1943-2022 -- the paper reports
#   ages 18-81, so the few years implying a child are entry errors, kept
#   as-is), cov_gender (1 male, 2 female, 3 neither), cov_country (1 Rwanda,
#   2 Uganda, 3 Tanzania, 4 Kenya), cov_marital (1 single, 2 married,
#   3 separated/divorced), cov_education (1 primary .. 5 PhD), cov_occupation
#   (1 student, 2 unemployed, 3 self-employed/employed), cov_income
#   (1 <100$ .. 6 >3000$ monthly), cov_religion (1 none, 2 Christian,
#   3 Muslim, 4 traditional), cov_trauma_type (1 genocide, 2 war, 3 exile,
#   4 childhood trauma, 5 imprisonment, 6 terrorism, 7 rape, 8 other),
#   cov_location (1 rural, 2 urban), cov_trauma_time (ITQ index-event
#   timing: 1 <6 months .. 6 >20 years ago).

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/20385027/files/"
       "Quantitative%20Dataset.xlsx/content")


def block(p, n):
    return [f"{p}{i}" for i in range(1, n + 1)]


# table -> (items, permitted set, total column)
TABLES = {
    "mutuyimana_2026_trauma_exposure": (block("TE", 17), range(0, 4),
                                        "TETotal"),
    "mutuyimana_2026_csti": (block("CSTI", 71), range(0, 5), None),
    "mutuyimana_2026_cahtq": (block("CAHTQ", 20), range(0, 5), "CAHTQTotal"),
    "mutuyimana_2026_itq": (block("PTSD", 9) + block("DSO", 9), range(0, 5),
                            None),
    "mutuyimana_2026_helplessness": (block("HQ", 10), range(1, 8),
                                     "HQTotal"),
    "mutuyimana_2026_social_axioms": (block("SAQ", 15), range(1, 6),
                                      "SAQTotal"),
    "mutuyimana_2026_epil": (block("PL", 7), range(1, 8), "PLTotal"),
    "mutuyimana_2026_gse": (block("GSE", 9), range(1, 6), "GSETotal"),
    "mutuyimana_2026_subjective_vitality": (block("SV", 7), range(1, 8),
                                            "SVTotal"),
    "mutuyimana_2026_personal_mastery": (block("PMS", 7), range(1, 6),
                                         "PMSTotal"),
}
# First column of each block -> a fragment of its codebook cell (row 1).
CODEBOOK = {
    "TE1": "0:Not happened 1:Heard about 2:Witnessed 3:Experienced",
    "CSTI1": "0:Strongly disagree 1:Disagree 2:Neutral 3:Agree "
             "4:Strongly agree",
    "CAHTQ1": "0:Not at all 1:Little a bit 2:Sometimes 3:Often 4:All the time",
    "PTSD1": "0:Not at all 1:A little a bit 2:Moderately 3:Quit a bit "
             "4:Extremel",
    "DSO1": "0:Not at all 1:A little a bit 2:Moderately 3:Quit a bit 4:",
    "HQ1": "1:Absolutely untrue 2:Mostly untrue 3:Somewhat untrue "
           "4:Can't Say true or false 5:Somewhat true 6:Mostly true "
           "7:Absolutely true",
    "SAQ1": "1. Strongly disagree 2. Disagree 3. Neither agree or disagree "
            "4.Agree 5.Strongly agree",
    "PL1": "1: The lowest level of your response",
    "GSE1": "1. Strongly disagree 2. Disagree 3. Neither agree or disagree "
            "4.Agree 5.Strongly agree",
    "SV1": "6:Mostly true 1:Absolutely true",
    "PMS1": "1.Strongly disagree 2.Disagree 3.Neither agree or disagree "
            "4.Agree 5.Strongly agree",
}
OTHER_TOTALS = {"CSTITotal", "PTSDTotal", "DSOTotal"}
COVS = {"Year_of_birth": "cov_birth_year", "Gender": "cov_gender",
        "Country": "cov_country", "Marital_status": "cov_marital",
        "Education_level": "cov_education", "Occupation": "cov_occupation",
        "Monthly_income": "cov_income", "Religion": "cov_religion",
        "Traumatic_exposure": "cov_trauma_type", "Location": "cov_location",
        "TETime": "cov_trauma_time"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        raw = pd.read_excel(path, sheet_name="DATASET AND CODES", header=None)
    finally:
        os.unlink(path)
    return raw


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = load()
    assert raw.shape == (1210, 204), raw.shape
    header = [str(h).strip() if pd.notna(h) else None for h in raw.iloc[1]]
    assert header[199] is None and header[198] == "PMS3" \
        and header[200] == "PMS5"
    header[199] = "PMS4"
    assert len(set(header)) == len(header)
    codebook = {h: " ".join(str(v).split()) for h, v in zip(header,
                                                           raw.iloc[0])
                if pd.notna(v)}
    for col, frag in CODEBOOK.items():
        assert frag in codebook[col], (col, codebook[col])
    d = raw.iloc[2:].copy()
    d.columns = header
    d = d.apply(pd.to_numeric, errors="raise").reset_index(drop=True)
    assert len(d) == 1208

    # Balance the books.
    items = [c for its, _, _ in TABLES.values() for c in its]
    totals = {t for _, _, t in TABLES.values() if t} | OTHER_TOTALS
    known = set(items) | totals | set(COVS) | {"No"}
    assert set(d.columns) == known, set(d.columns) ^ known
    assert len(items) == len(set(items))

    assert (d["No"] == range(1, 1209)).all()
    assert not d.drop(columns="No").duplicated().any()
    assert not d[items].T.duplicated().any()
    assert d[items].notna().all().all()
    for _, (its, _, tot) in TABLES.items():
        if tot:
            assert (d[its].sum(axis=1) == d[tot]).all(), tot
    assert (d[block("PTSD", 9)].sum(axis=1) == d["PTSDTotal"]).all()
    assert (d[block("DSO", 9)].sum(axis=1) == d["DSOTotal"]).all()
    # The paper's country counts.
    assert d["Country"].value_counts().to_dict() == {3: 412, 1: 320,
                                                     2: 256, 4: 220}

    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, allowed, _) in TABLES.items():
        allowed = set(allowed)
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
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
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
