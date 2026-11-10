#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0177172
# DOI: 10.1371/journal.pone.0177172
# Paper: Fernandez-Dominguez JC, de Pedro-Gomez JE, Morales-Asencio JM,
#   Bennasar-Veny M, Sastre-Fullana P, Sese-Abad A (2017). Health
#   Sciences-Evidence Based Practice questionnaire (HS-EBP) for measuring
#   transprofessional evidence-based practice: Creation, development and
#   psychometric validation. PLoS ONE 12(5): e0177172.
# Data: PLOS SI S3 File (s003, .sav, pilot test: 211 health professionals in
#   the Balearic Islands, 73-item HS-EBP plus criterion scales) and S4 File
#   (s004, .sav, validation sample: 869 professionals across Spain, 72-item
#   HS-EBP). S1/S2 Files are the questionnaires.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv; also in
# repos_leads_2026-10-07.csv), overnight lane A 2026-11-10.
#
# The pilot and validation samples answered DIFFERENT versions of the HS-EBP
# (73 vs 72 items, refined between them) under different item codes, so they
# are separate tables. SIX output tables, items as answered:
#   fernandez_dominguez_2017_hsebp73  pilot HS-EBP, HSD1_1..HSD5_x, 73 items,
#     1-10.
#   fernandez_dominguez_2017_hsebp72  validation HS-EBP, 72 items in the five
#     domains CREAC (beliefs/attitudes, 14), RESULT (results from research,
#     16), PRAC (development of professional practice, 12), EVAL (assessment
#     of results, 15), BARFAC (barriers/facilitators, 15), 1-10.
#   Pilot criterion scales (Methods): fernandez_dominguez_2017_ebpq (EBPQ-19
#     knowledge/skills and practice items, 16, 1-7), _rtc (Spanish Resistance
#     to Change scale, 17, 1-6), _mbi (Maslach Burnout Inventory, 22, 0-6),
#     _cvp (CVP-35 intrinsic motivation, 9 as deposited, 1-10).
# Dropped: the pilot's RV1..RV15 (0/1, not described in the paper) and
#   TT1..TT5 (time percentages), free-text occupation/environment fields.
# Covariates: sex (pilot coded 0/1 unlabelled: 1 = 140 of 211 = the paper's
#   66.4% women; validation labelled 1 man / 2 women), age (pilot 0 set
#   missing), academic degree code, years worked.
# `id` = row index within each file.
#
# Item text: NOT SHIPPED. HS-EBP wording (study-authored, Spanish) is in the
#   S1/S2 questionnaire .docx files; the criterion scales are third-party.

import os
import re
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
BASE = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0177172."
RAW_DIR = os.environ.get("FERNANDEZ2017_RAW_DIR")
PFX = "fernandez_dominguez_2017_"


def read(sfx):
    if RAW_DIR:
        return pyreadstat.read_sav(os.path.join(RAW_DIR, sfx + ".sav"))[0]
    r = requests.get(BASE + sfx, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
    r.raise_for_status()
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"_fd2017_{sfx}.sav")
    with open(path, "wb") as f:
        f.write(r.content)
    df = pyreadstat.read_sav(path)[0]
    os.remove(path)
    return df


def block(df, prefix):
    return [c for c in df.columns if re.fullmatch(prefix + r"\d+(_\d+)?", c)]


def save(df, covs, items, name, values):
    long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= set(values), (name, set(long["resp"]))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, PFX + name + ".csv"), index=False)
    print(f"{PFX}{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    pilot = read("s003")
    val = read("s004")
    assert (len(pilot), len(val)) == (211, 869)
    covs = ["cov_sex", "cov_age", "cov_academic_degree", "cov_years_worked"]

    pilot = pilot.reset_index(drop=True)
    pilot["id"] = pilot.index + 1
    pilot["cov_sex"] = pilot["Sex"].map({1: "female", 0: "male"})
    assert (pilot["cov_sex"] == "female").sum() == 140
    pilot["cov_age"] = pilot["Age"].where(pilot["Age"] > 0)
    pilot["cov_academic_degree"] = pilot["Acdemic_degree"]
    pilot["cov_years_worked"] = pilot["Years_work"]
    blocks = {"HSD": ("hsebp73", range(1, 11), 73), "EBPQ": ("ebpq", range(1, 8), 16),
              "RDC": ("rtc", range(1, 7), 17), "MBI": ("mbi", range(0, 7), 22),
              "CVP": ("cvp", range(1, 11), 9)}
    for p, (name, vals, n) in blocks.items():
        items = block(pilot, p)
        assert len(items) == n, (p, len(items))
        save(pilot, covs, items, name, vals)

    val = val.reset_index(drop=True)
    val["id"] = val.index + 1
    val["cov_sex"] = val["Sex"].map({1: "male", 2: "female"})
    val["cov_age"] = val["Age"]
    val["cov_academic_degree"] = val["Acdemic_degree"]
    val["cov_years_worked"] = val["Years_work"]
    items = []
    for p in ("CREAC", "RESULT", "PRAC", "EVAL", "BARFAC"):
        items += block(val, p)
    assert len(items) == 72
    save(val, covs, items, "hsebp72", range(1, 11))


if __name__ == "__main__":
    convert()
