#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/CC2HL8
# DOI: 10.7910/DVN/CC2HL8 (dataset; the record cites no paper)
#   Khan, Shazia (2023). Inspiring Followers to Follow: Perceiving Purpose and Motivation
#   behind Ethical Behavior and a Quest for 'Ethical' Leadership in the Organization
#   [Data set]. Harvard Dataverse.
# Data: "Consolidated Experimental Data.sav" (file 6429329, format=original) -- 176
#       participants in a six-condition vignette experiment on the inspirational value of
#       moral exemplars' actions (EL_Punishment, EL_Reward, WB_External, WB_Internal,
#       WB_Leave, WB_Silence), each rating items on 1-7 scales with value labels, plus the
#       authors' composite means.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Item variables have value labels (anchors) but most carry no
#   variable label, and the few that do give only a short name ("Similarity with
#   Protagonist"); no questionnaire or paper is deposited.
#
# How the blocks were identified: regressing each deposited composite on all 39 rating
#   items reproduces it exactly (max residual 0) as an equal-weight mean of one block:
#   Inspiration = the six Insp_* items; Motivation = MoralVal_P, Fear_Punish, Trustworthy,
#   Seen_ethicalP, Org_Reward, Control_People, Moral_Resp, Org_Prestige, Another_Motive
#   (its sub-means M_ObviousGains = Fear_Punish, Org_Reward, Control_People; M_NoObviousGains
#   and Moral_I = subsets of the rest); Purpose = Promote_EB, Discourage_UEB, Org_rep,
#   Examp_Punish, Imprv_PerformanceE, Wellbeing_Affectees, Freedom_E, Dignity_People,
#   Respectful_treatment_E, Equal_treatmentE, Auto_DM, Another_Purpose (sub-means
#   P_Culture_Care, P_Employee_Org). The script re-derives and asserts this.
# Tables (1-7, item = the deposit's variable name):
#   khan_2023_inspiration           Insp_* (6), anchors "Didn't feel anything" .. "Felt Very
#                                   Strongly"
#   khan_2023_perceived_motivation  the 9 Motivation items, strongly disagree .. strongly agree
#   khan_2023_perceived_purpose     the 12 Purpose items, strongly disagree .. strongly agree
# Skipped: the single-purpose ratings outside every composite (similarity with protagonist /
#   antagonist, difficulty of the act for each, role model x2, pleasantness, Same_mot_sit_P,
#   Same_purpose_sit_P, Conseq_Org/_society/_individuals); all composite means.
# Covariates (codes as stored; value labels via the covariate-label harvest): cov_condition
#   (1-6, labels above), cov_gender, cov_age_group, cov_education, cov_job_status,
#   cov_work_experience.
# id: the deposit's ID (1-176).

import os
import sys
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
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "cc2hl8"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/6429329?format=original"
P = "khan_2023_"
RANGE = range(1, 8)
TABLES = {"inspiration": ["Insp_Moved", "Insp_Uplifted", "Insp_OptimisticH", "Insp_warmFeeling",
                          "Insp_help", "Insp_betterperson"],
          "perceived_motivation": ["MoralVal_P", "Fear_Punish", "Trustworthy", "Seen_ethicalP",
                                   "Org_Reward", "Control_People", "Moral_Resp", "Org_Prestige",
                                   "Another_Motive"],
          "perceived_purpose": ["Promote_EB", "Discourage_UEB", "Org_rep", "Examp_Punish",
                                "Imprv_PerformanceE", "Wellbeing_Affectees", "Freedom_E",
                                "Dignity_People", "Respectful_treatment_E", "Equal_treatmentE",
                                "Auto_DM", "Another_Purpose"]}
COMP = {"Inspiration": "inspiration", "Motivation": "perceived_motivation",
        "Purpose": "perceived_purpose"}
SUBCOMP = ["M_NoObviousGains", "M_ObviousGains", "P_Employee_Org", "P_Culture_Care", "Moral_I"]
SINGLES = ["SimilaritywithProtagonist", "SimilaritywithAntagonist", "DifficultActforP",
           "Difficulty_A", "P_Rolemodel", "A_rolemodel", "Pleasant_ActionP", "Same_mot_sit_P",
           "Same_purpose_sit_P", "Conseq_Org", "Conseq_society", "Conseq_individuals"]
COVS = {"Condition": "cov_condition", "Gender_coded": "cov_gender", "Age_coded": "cov_age_group",
        "Education_Coded": "cov_education", "Job_Status_Coded": "cov_job_status",
        "WorkExperience_Coded": "cov_work_experience"}


def fetch() -> Path:
    p = RAW_DIR / "data.sav"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, _ = pyreadstat.read_sav(str(fetch()))
    assert d.shape == (176, 54) and d["ID"].is_unique
    items = [c for v in TABLES.values() for c in v]
    accounted = {"ID"} | set(items) | set(COMP) | set(SUBCOMP) | set(SINGLES) | set(COVS)
    assert accounted == set(d.columns), set(d.columns) ^ accounted
    rating = items + SINGLES
    cc = d.dropna(subset=rating + list(COMP))
    for comp, k in COMP.items():
        X = np.c_[np.ones(len(cc)), cc[rating].values]
        b = np.linalg.lstsq(X, cc[comp].values, rcond=None)[0]
        found = [rating[i] for i in range(len(rating)) if abs(b[i + 1]) > 0.02]
        assert sorted(found) == sorted(TABLES[k]), (comp, found)
    print(f"  [skip] {len(SINGLES)} single ratings outside the composites; {len(COMP) + len(SUBCOMP)} composites")
    d = d.rename(columns={"ID": "id", **COVS})
    d["id"] = d["id"].astype(int)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    names = [P + k for k in TABLES]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for k, its in TABLES.items():
        name = P + k
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(RANGE).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(RANGE) for i in its}
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
        for f in report.warnings:
            print(f"    [validate warn] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        total += len(t)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert total == int(d[items].notna().sum().sum()), "books do not balance"


if __name__ == "__main__":
    main()
