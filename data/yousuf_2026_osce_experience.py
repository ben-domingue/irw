#!/usr/bin/env python3
# Source: https://zenodo.org/records/21407793
# DOI: 10.5281/zenodo.21407793 (data)
#   Yousuf IM, Dahir SH, Jama YA, Osman AH, Darod AF (2026). Psychometric Properties and Factor
#   Structure of a 30-Item Questionnaire Assessing Students' Experiences of the Objective Structured
#   Clinical Examination at Citycot University, Somalia [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: OSCE_Psychometric_Data_FINAL..sav, 400 health-sciences students (396 complete on the 30 items;
#   four records miss one item each, per the deposit's Data Quality sheet). Codebook:
#   OSCE_Codebook_Data_Dictionary_and_Scoring_Key.xlsx in the same deposit (dictionary, value labels,
#   scoring key: seven domains, no reverse-coded items, no overall score recommended).
#
# Tables (item = the deposit's variable name):
#   yousuf_2026_osce_experience  -- 25 agreement items, 1 Strongly disagree .. 5 Strongly agree:
#     S1-S5 station quality, V1-V5 fairness/validity, P1-P5 procedures, E1-E3 physical environment,
#     E4-E6 examination stress (higher = more stress), O1-O4 perceived outcomes.
#   yousuf_2026_osce_discrepancy -- D1-D5, a different response format: 1 No discrepancy .. 5 Very
#     major discrepancy (value labels), so it is its own table.
# id: Participant_ID (the deposit's de-identified study code).
# Covariates (value labels applied): cov_gender, cov_age_group, cov_department, cov_academic_level,
#   cov_prior_osce, cov_previous_osce_here, cov_clinical_attachment.
# Not carried: discrepancy, challenge, sugg1-3 (optional free text).
# Item text: SHIPPED -- data_labels + study_materials: each item's .sav variable label is its question,
#   the value labels are its anchors (both label levels present on all 30 items).
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://zenodo.org/api/records/21407793/files/OSCE_Psychometric_Data_FINAL..sav/content"
COVS = {"Gender": "cov_gender", "Age_Group": "cov_age_group", "Department": "cov_department",
        "Current_Academic_Leve": "cov_academic_level", "Prior_OSCE_Experience": "cov_prior_osce",
        "Previously_Completed_OSCE": "cov_previous_osce_here",
        "Clinical_Attachment_Experience": "cov_clinical_attachment"}
BLOCKS = {
    "yousuf_2026_osce_experience": [f"{p}{i}" for p, n in [("S", 5), ("V", 5), ("P", 5), ("E", 6), ("O", 4)]
                                    for i in range(1, n + 1)],
    "yousuf_2026_osce_discrepancy": [f"D{i}" for i in range(1, 6)],
}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    assert len(d) == 400 and d["Participant_ID"].is_unique
    vl = meta.variable_value_labels
    d["id"] = d["Participant_ID"].astype(int)
    for src, cov in COVS.items():
        lab = dict(vl.get(src, {}))
        if src == "Clinical_Attachment_Experience":
            lab[1.0] = "None"  # the .sav carries this label; the codebook sheet shows it blank
        d[cov] = d[src].map(lab)
        assert d[cov].notna().sum() == d[src].notna().sum(), cov
    covs = list(COVS.values())
    for name, items in BLOCKS.items():
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        assert t["resp"].isin([1, 2, 3, 4, 5]).all()
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(1, 6)) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
