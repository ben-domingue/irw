#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/VWRTAW
# DOI: 10.12688/f1000research.51936.1
#   Abu Tabar, N., Al Qadire, M., Thultheen, I., & Alshraideh, J. (2021). Health-related
#   quality of life, uncertainty, and anxiety among patients with chronic obstructive
#   pulmonary disease. F1000Research, 10:420.
# Data: Harvard Dataverse 10.7910/DVN/VWRTAW (Alshraideh, Jafar; 2021-03-25).
#       "COPD dataset for F1000Research.sav" (file 4469702, format=original) -- 153 COPD
#       outpatients from three Jordanian hospitals x 97 columns: demographics and
#       clinical history, the 23 MUIS items, the 20 STAI state items, SGRQ domain scores,
#       recoded/reversed copies and totals.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. The .sav variable labels carry the English item stems at the
#   variable-label level (MUIS1 "I don't know what is wrong with me.", SAI1 "I feel
#   calm"), and value labels carry the anchors (MUIS 1 strongly disagree .. 5 strongly
#   agree; SAI 1 Not At All .. 4 Very Much So). Not shipped because the STAI is a
#   `block` row in itemtext/instrument_rights_register.csv (Mind Garden), and the study
#   was administered in Arabic (the labels are an English rendering), so the MUIS would be
#   a translated_substitute that needs its own rights check.
#
# Tables:
#   abu_tabar_2021_muis   MUIS1-MUIS23 (Mishel Uncertainty in Illness Scale, community
#                         form), 1-5 as administered; reverse-keyed items (6, 8, 19, 20,
#                         22, 23) are kept as worded -- the deposit's MUISkR copies are skipped.
#   abu_tabar_2021_stai_s SAI1-SAI20 (STAI form Y-1, state anxiety), 1-4 as administered;
#                         the SAIkR reversed copies are skipped.
# Skipped: SGRQ (only domain scores and a single global-health item are deposited),
#   MUISkR/SAIkR (recodes), totals, age/duration groupings (recodes of covariates kept),
#   free-text worktype / living_others / help_support (and their recodes, kept as codes).
# Covariates (the .sav's codes; value labels via the covariate-label harvest): cov_hospital
#   (H_ID), cov_age, cov_sex, cov_marital (M_S), cov_work_status, cov_worktype
#   (worktyperecode), cov_education, cov_living (livingstatus), cov_support
#   (Helpsupport_recod), cov_age_dx, cov_dx_years (Dx_year), cov_dx_type, cov_dm, cov_htn,
#   cov_ihd (comorbidity history), cov_smoking (smoking_hx), cov_admissions
#   (hospadmission), cov_gold (GOLD stage).
# id: P_ID (1-153, unique).

import os
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
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "vwrtaw"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/4469702?format=original"
MUIS = [f"MUIS{i}" for i in range(1, 24)]
SAI = [f"SAI{i}" for i in range(1, 21)]
TABLES = {"abu_tabar_2021_muis": (MUIS, range(1, 6)),
          "abu_tabar_2021_stai_s": (SAI, range(1, 5))}
COVS = {"H_ID": "cov_hospital", "age": "cov_age", "sex": "cov_sex", "M_S": "cov_marital",
        "workstatus": "cov_work_status", "worktyperecode": "cov_worktype",
        "educalevel": "cov_education", "livingstatus": "cov_living",
        "Helpsupport_recod": "cov_support", "age_dx": "cov_age_dx", "Dx_year": "cov_dx_years",
        "DXtype": "cov_dx_type", "hx_DM": "cov_dm", "hx_HTN": "cov_htn", "hx_IHD": "cov_ihd",
        "smoking_hx": "cov_smoking", "hospadmission": "cov_admissions",
        "GOLDstage": "cov_gold"}
SKIP_PREFIX = ("MUIS6R", "MUIS8R", "MUIS19R", "MUIS20R", "MUIS22R", "MUIS23R")
SKIP = {**{c: "reversed copy" for c in SKIP_PREFIX},
        **{f"SAI{i}R": "reversed copy" for i in (1, 2, 5, 8, 10, 11, 15, 16, 19, 20)},
        "MUIStotal": "total", "MUIStotalscore": "total", "SAItotals": "total",
        "SAItotalscore": "total", "SYMPSCORE": "SGRQ domain score",
        "ACTIVSCORE": "SGRQ domain score", "IMPACTSCORE": "SGRQ domain score",
        "SGRQTOTAL": "SGRQ total", "SGRQ": "single global-health item",
        "ageGroups": "grouping of age", "yearswithCOPD": "grouping of Dx_year",
        "durationofdisease": "grouping of Dx_year", "smokingbehaviuor": "recode of smoking_hx",
        "worktype": "free text", "living_others": "free text", "help_support": "free text",
        "age_smoking": "smoking detail", "smoking_time": "smoking detail",
        "smoking_packet": "smoking detail"}


def fetch() -> Path:
    p = RAW_DIR / "data.sav"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, meta = pyreadstat.read_sav(str(fetch()))
    assert d.shape == (153, 97) and d["P_ID"].is_unique
    items = MUIS + SAI
    accounted = {"P_ID"} | set(items) | set(COVS) | set(SKIP)
    assert accounted == set(d.columns), set(d.columns) ^ accounted
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    # reversed copies really are 6 - x / 5 - x of the kept items
    for c in SKIP_PREFIX:
        assert (d[c] == 6 - d[c[:-1]]).all(), c
    d = d.rename(columns={"P_ID": "id", **COVS})
    d["id"] = d["id"].astype(int)
    covs = list(COVS.values())
    names = list(TABLES)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, (its, rng) in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(list(rng)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
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
        for f in report.warnings:
            print(f"    [validate warn] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        total += len(t)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert total == int(d[items].notna().sum().sum()), "books do not balance"


if __name__ == "__main__":
    main()
