#!/usr/bin/env python3
# Source: https://zenodo.org/records/4441996
# DOI: 10.1037/tra0001068
#   Sandoz, V., Hingray, C., Stuijfzand, S., Lacroix, A., El Hage, W., &
#   Horsch, A. (2022). "Measurement and conceptualization of maternal PTSD
#   following childbirth: Psychometric properties of the City Birth Trauma
#   Scale - French Version (City BiTS-F)." Psychological Trauma: Theory,
#   Research, Practice, and Policy 14(4), 696-704. (APA, paywalled; read
#   2026-10-02 from a PDF Ben supplied.)
# Data: Zenodo 4441996, Dataset_CBTS-F_mother_validation.xlsx (541 rows x 80
#       columns; French-speaking mothers who gave birth 1-12 months earlier,
#       online survey June-Sept 2020). The deposit's .csv is the same data
#       (latin-1); Codebook_CBTS-F_mother_validation.xlsx gives each
#       variable's French question text; the readme says "No missing data"
#       although some items are blank.
# License: CC BY 4.0 (Zenodo record metadata).
#
# Item text: not shipped. A spreadsheet, so no variable or value labels; the
#   deposit's codebook carries the French stem for every item keyed by the
#   variable name (cheap for a later pass), but no response-option text. The
#   anchors are in the published instruments (City BiTS: Ayers et al. 2018;
#   PCL-5; EPDS: Cox et al. 1987; HADS: Zigmond & Snaith 1983). HADS
#   wording must not ship at all: irw-validate's rights register lists it
#   (GL Assessment, verdict block); response data is fine.
#
# Tables (item codes are the source column names):
#   sandoz_2021_cbts           24 items  City Birth Trauma Scale, French
#                              (CBTS_M_1..CBTS_M_12, CBTS_13..CBTS_24).
#                              Items 1-2 are the criterion-A stressor
#                              questions (paper: yes = 0, no = 1), items
#                              3-24 the symptom frequencies over the past
#                              week, 0 not at all, 1 once, 2 2-4 times,
#                              3 5 or more times (paper, Measures).
#   sandoz_2021_pcl5           20 items  PTSD Checklist for DSM-5, worded
#                              about the birth, 0 (not at all) .. 4
#                              (extremely) (paper).
#   sandoz_2021_epds           10 items  Edinburgh Postnatal Depression
#                              Scale, 4-point Likert, 0-3 (paper). Stored
#                              as scored:
#                              every inter-item correlation is positive, so
#                              the reverse-keyed items are already reflected.
#   sandoz_2021_hads_anxiety    7 items  HADS anxiety subscale (HADS_1, 3, 5,
#                              7, 9, 11, 13), 4-point, total 0-21 (paper;
#                              Zigmond & Snaith 1983).
#                              Also stored as scored (HADS_7 correlates
#                              positively with the rest).
#
# Dropped:
#   - CBTS_onset, CBTS_duration (timing categories 1-3 plus a 333 code,
#     n = 123, for "no symptoms"), CBTS_distress, CBTS_daily_life,
#     CBTS_substance (City BiTS items 25-29: the DSM criterion F-H
#     qualifiers. The paper codes onset 0 before birth / 1 within 6 months /
#     2 after 6 months, duration by month bands, and distress, interference
#     and physical cause as 0 yes, 1 no, 2 sometimes, so the codes are not
#     an ordered symptom scale; the deposit's own codes differ again).
#   - Type_parents, Birth_1mth_M_inclusion, Birth_12mth_M_inclusion
#     (inclusion screeners, constant 1).
#   - Marital_status_Autre (free text "other" marital status, two rows;
#     already folded into Marital_status per the codebook).
#   - Participant_numer (1..541) -> replaced by the row index.
# No PII: age in years only, no names, contact details or dates.
# Covariates: cov_age, cov_marital_status (1 single, 2 in a relationship,
#   3 separated/divorced/widowed, 6 other), cov_education (1 none ..
#   5 university), cov_parity, cov_past_pregnancies, cov_gestational_weeks,
#   cov_delivery_type (1 vaginal, 2 vacuum, 3 forceps, 4 planned caesarean,
#   5 emergency caesarean; multi-select, so kept as the source string such as
#   "1;2"), cov_previous_traumatic_birth and cov_past_trauma (1 yes, 2 no).

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
URL = ("https://zenodo.org/api/records/4441996/files/"
       "Dataset_CBTS-F_mother_validation.xlsx/content")

CBTS_STRESSOR = ["CBTS_M_1", "CBTS_M_2"]
CBTS_SYMPTOM = ([f"CBTS_M_{i}" for i in range(3, 13)]
                + [f"CBTS_{i}" for i in range(13, 25)])
TABLES = {
    "sandoz_2021_cbts": {**{c: set(range(0, 2)) for c in CBTS_STRESSOR},
                         **{c: set(range(0, 4)) for c in CBTS_SYMPTOM}},
    "sandoz_2021_pcl5": {f"PCL5_{i}": set(range(0, 5)) for i in range(1, 21)},
    "sandoz_2021_epds": {f"EPDS_{i}": set(range(0, 4)) for i in range(1, 11)},
    "sandoz_2021_hads_anxiety": {f"HADS_{i}": set(range(0, 4))
                                 for i in (1, 3, 5, 7, 9, 11, 13)},
}
DROPPED = {"CBTS_onset", "CBTS_duration", "CBTS_distress", "CBTS_daily_life",
           "CBTS_substance", "Type_parents", "Birth_1mth_M_inclusion",
           "Birth_12mth_M_inclusion", "Marital_status_Autre",
           "Participant_numer"}
COVS = {"Age": "cov_age", "Marital_status": "cov_marital_status",
        "Education": "cov_education", "Child_number": "cov_parity",
        "Past_pregnancies": "cov_past_pregnancies",
        "Gestational_age": "cov_gestational_weeks",
        "Type_delivery": "cov_delivery_type",
        "Trauma_birth": "cov_previous_traumatic_birth",
        "Past_trauma": "cov_past_trauma"}
INT_COVS = ["cov_age", "cov_marital_status", "cov_education", "cov_parity",
            "cov_past_pregnancies", "cov_previous_traumatic_birth",
            "cov_past_trauma"]


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = load()
    assert d.shape == (541, 80), d.shape

    items = {c for spec in TABLES.values() for c in spec}
    known = items | DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert sorted(d["Participant_numer"]) == list(range(1, 542))
    for c in ("Type_parents", "Birth_1mth_M_inclusion",
              "Birth_12mth_M_inclusion"):
        assert set(d[c]) == {1}, c
    assert (d["CBTS_onset"] == 333).sum() == 123
    assert not d.drop(columns="Participant_numer").duplicated().any()
    for t in ("sandoz_2021_epds", "sandoz_2021_hads_anxiety"):
        assert (d[list(TABLES[t])].corr().values > 0).all(), t

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    d["cov_delivery_type"] = d["cov_delivery_type"].astype(str)
    cov_cols = list(COVS.values())

    names = []
    for table, spec in TABLES.items():
        its = list(spec)
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - spec[it]
            assert not bad, (table, it, bad)
        pv = {i: spec[i] for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in INT_COVS:
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
