#!/usr/bin/env python3
# Source: https://osf.io/y6edb/
#   DVMSQ_ProlificDataOSF_07.17.2022.csv            https://osf.io/download/3xamc/
#   DVMSQ_ProlificStudy_DataDictionary_07.17.2022.csv https://osf.io/download/efr89/  (codebook)
# Paper DOI: 10.3389/fpsyg.2022.897901
#   Williams, Z. J., Cascio, C. J., & Woynaroski, T. G. (2022). Psychometric validation of
#   a brief self-report measure of misophonia symptoms and functional impairment: The
#   Duke-Vanderbilt Misophonia Screening Questionnaire. Frontiers in Psychology, 13, 897901.
# Data DOI: 10.17605/OSF.IO/Y6EDB
# License: CC BY 4.0 (OSF node y6edb, license object 563c1cf88c5e4a3877f9e96a =
#   "CC-By Attribution 4.0 International", re-checked on the OSF API 2026-11-10)
#
# Companion to data/williams_2022_dvmsq.py (#2484), which took only the DVMSQ item pool
# and listed the other instruments in the same file as "not taken" on scope. This script
# builds those, from the same file, with the same id (row index + 1 in file order), so
# the tables link to williams_2022_dvmsq on id.
#
# Tables (items keep the REDCap variable name, except OASIS/ODSIS/RLSS/SSS-8 where the
#   descriptive suffix is cut: oasis_q1_frequency -> oasis_q1; wording in the dictionary):
#   williams_2022_dmss        Duke Misophonia Questionnaire symptom scale: affect (8),
#                             physiological (5), cognitive (10) items, 0-4 never..always.
#                             Branched in REDCap: 1,054 respondents were shown it; the rest
#                             are blank (NA) in the export, not zero-filled -- dropped.
#   williams_2022_ihs         Inventory of Hyperacusis Symptoms, 25 items. The dictionary
#                             gives codes 0-3 (not at all..very much); the export holds 1-4
#                             for every respondent (0 never occurs), i.e. shifted by +1.
#                             Shipped as exported, 1-4.
#   williams_2022_phonophobia DSM-5 severity measure for specific phobia, adapted to sound
#                             (dsm_1..dsm_10), 0-4 never..all of the time; all 1,403.
#   williams_2022_oasis       Overall Anxiety Severity and Impairment Scale, 5 items, 0-4.
#                             Items 2-5 are blank whenever item 1 = 0 (REDCap branching);
#                             blanks dropped, so those respondents contribute item 1 only
#                             (5 ODSIS respondents with item 1 = 0 still answered item 3; kept).
#   williams_2022_odsis       Overall Depression Severity and Impairment Scale, same shape.
#   williams_2022_rlss        Riverside Life Satisfaction Scale, 6 items, 1-7 (reverse-keyed
#                             items 2, 4, 6 left raw).
#   williams_2022_sss8        Somatic Symptom Scale-8, 8 items, 0-4.
# Not shipped: cuangos_* (5 anger items; the dictionary does not name the instrument),
#   dmss_frequency (single frequency item), dmss_impact_vas (0-100 slider), checkbox
#   blocks, summary scores, free-text fields.
# PII: prolific_id dropped, id = row index (2026-09-20 ruling). No names, emails, IPs,
#   birthdates or postal codes. Free-text trigger descriptions not carried.
# Covariates (same as williams_2022_dvmsq): cov_age, cov_gender, cov_sex, cov_education
#   (dictionary labels).
#
# Item text: not shipped -- stems and options are in the deposit's REDCap dictionary
#   (Field Label / Choices); no register rows yet for DMSS/IHS/OASIS/ODSIS/RLSS/SSS-8.
#   Cheap later from that one file.
from io import BytesIO
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402


def gate(t):
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
URL_DATA = "https://osf.io/download/3xamc/"
URL_DICT = "https://osf.io/download/efr89/"


def fetch(url):
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return r.content


def labels(choices: str) -> dict:
    return {int(k): v.strip() for k, v in (p.split(",", 1) for p in choices.split("|"))}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(BytesIO(fetch(URL_DATA)), low_memory=False)
    k = pd.read_csv(BytesIO(fetch(URL_DICT)), encoding="utf-8-sig").set_index(
        "Variable / Field Name")
    assert len(d) == 1403
    d = d.reset_index(drop=True).copy()
    d["id"] = d.index + 1
    d["cov_age"] = d["age_yrs"]
    d["cov_gender"] = d["gender"].map(labels(k.loc["gender", "Choices, Calculations, OR Slider Labels"]))
    d["cov_sex"] = d["sex"].str.lower()
    ed = labels(k.loc["education", "Choices, Calculations, OR Slider Labels"])
    d["cov_education"] = d["education"].str.extract(r"^LVL(\d+)_")[0].astype(int).map(ed)
    covs = ["cov_age", "cov_gender", "cov_sex", "cov_education"]
    assert d[covs].notna().all().all()

    pref = lambda p: [c for c in d.columns if c.startswith(p)]
    scales = {
        "dmss": [f"dmss_affect{i}" for i in range(1, 9)] + [f"dmss_physio{i}" for i in range(1, 6)]
                + [f"dmss_cog{i}" for i in range(1, 11)],
        "ihs": pref("ihs_"), "phonophobia": pref("dsm_"), "oasis": pref("oasis_q"),
        "odsis": pref("odsis_q"), "rlss": pref("rlss_q"), "sss8": pref("sss8_q"),
    }
    expect = {"dmss": 23, "ihs": 25, "phonophobia": 10, "oasis": 5, "odsis": 5, "rlss": 6, "sss8": 8}
    # branching checks: OASIS/ODSIS items 2-5 blank exactly when item 1 == 0
    for p in ("oasis", "odsis"):
        q1 = d[f"{p}_q1_frequency"]
        print(p, "items 2-5 answered when item 1 == 0:",
              d.loc[q1 == 0, pref(f"{p}_q")[1:]].notna().sum().to_dict())
    assert d[pref("ihs_")].min().min() == 1 and d[pref("ihs_")].max().max() == 4

    for name, cols in scales.items():
        assert len(cols) == expect[name], (name, len(cols))
        t = d[["id"] + covs + cols].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        if name in ("oasis", "odsis", "rlss", "sss8"):
            # REDCap names carry a descriptive suffix (oasis_q1_frequency, rlss_q5_satisfied);
            # the item code is the name up to the question number, which is unique per
            # scale and maps back to exactly one source column.
            t["item"] = t["item"].str.extract(r"^([a-z0-9]+_q\d+)_")[0]
            assert t["item"].notna().all() and t["item"].nunique() == len(cols)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        gate(t)
        t.to_csv(OUT_DIR / f"williams_2022_{name}.csv", index=False)
        print(f"williams_2022_{name}: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={sorted(t['resp'].unique())}")


if __name__ == "__main__":
    main()
