#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0142620
# DOI: 10.1371/journal.pone.0142620
# Paper: Lam WWT, Liao Q, Wong JHF, Lai CL, Yuen MF, Tsang JWH, et al. (2015).
#   Measuring and Validating a General Cancer Predisposition Perception Scale:
#   An Adaptation of the Revised-IPQ-Genetic Predisposition Scale. PLOS ONE
#   10(11): e0142620.
# Data: S1 Dataset (Stage I, CSV, 290 x 86) and S2 Dataset (Stage II, CSV,
#   450 x 54), both attached to the article. No codebook in the SI; the scales
#   and their ranges are read from the paper's Methods.
# License: CC BY 4.0 (the article's licence covers its SI files).
#
# Found by the PLOS monthly run of 2026-11-09 (leads/plos_leads_2026-11-09.csv,
# step-2b recoverable_format).
#
# Hong Kong Chinese adults, two independently recruited samples:
#   Stage I  (S1): 167 HBsAg carriers (group 1) + 123 non-patients (group 0).
#   Stage II (S2): 148 healthy controls (group 1), 150 current smokers
#                  (group 2), 152 passive smokers (group 3).
#   The group codes are identified by their counts, which match the paper's
#   Results exactly (167/123; 148/150/152).
#
# FIVE output tables:
#   lam_2015_cpps_stage1 -- the 28-item draft Cancer Predisposition Perception
#       Scale (CPPS, adapted from the IPQ-R-GP), 1-5, Stage I. Deposit codes
#       IP_06..IP_38 (with gaps).
#   lam_2015_cpps_stage2 -- the same draft scale, Stage II. Deposit codes
#       ip_09..ip_36. NOT merged with Stage I: the two files number the 28
#       items differently and the paper's item table (Table 1) is an image, so
#       which Stage I item is which Stage II item cannot be confirmed. One table
#       per instrument as administered; the paper's six-factor subscale
#       structure is not encoded.
#   lam_2015_gses -- Chinese General Self-Efficacy Scale, 10 items, 1-4
#       ("4-point Likert scale ... 'Completely incorrect' to 'Completely
#       correct'"). Same instrument, same items gses1..gses10 and same 1-4
#       range in both samples, so ONE table with cov_study (1 = Stage I,
#       2 = Stage II). The two files' ids do not overlap (1..1029 vs
#       10002..10465), asserted below, so no offset is needed.
#   lam_2015_chq12 -- Chinese Health Questionnaire-12, 0-3 (4-point, 'Not at
#       all' to 'Much more than usual'), Stage I only.
#   lam_2015_clotr -- Chinese Life Orientation Test-Revised, 6 items, 1-4,
#       Stage II only.
#
# NOT SHIPPED:
#   - Stage I C-LOT-R (CLOT_1..6): coded 0-4, five values, against the paper's
#     "4-point Likert scale"; Stage II's copy is 1-4 as documented. Which
#     Stage I value is the extra one is not documented, so it is left out.
#   - PGH / PCH: single items (perceived general / current health).
#   - d* demographics (Stage I) and agegrou1/gender01/mar01/edu/ocu/income
#     (Stage II): no codebook gives their codes. Only the sample group ships,
#     as cov_group, labelled from the paper.
#
# Response cleaning:
#   - 999 (and 777 / 888) are missing / not-applicable codes outside every
#     documented range; dropped.
#   - IMPUTATION: Stage I carries 8 non-integer cells in item columns (IP_08
#     3.22, IP_28 3.52, CLOT_1 1.8, gses10 1.78 and 2.22, chq11 0.2, chq12 0.2),
#     each sitting on a one-step integer scale. They are mean-imputed values
#     (each is near its column's mean) and are dropped. The paper says nothing
#     about imputation (no "imput" in the text), so the integer cells cannot
#     be cleared of other imputation methods either; noted, not acted on.
#
# Item text: SHIPPED for lam_2015_gses only (English original as a stand-in);
#   the other four HELD. Label levels checked: the two CSVs carry no labels
#   (headers are codes; no codebook in the SI; S1/S2 Table are demographics).
#   The article's Table 1 prints English wording for 27 Stage I CPPS items as
#   text (numbered I1..I27, not the deposit's IP_06..IP_38, with no key between
#   the two), the English of a Chinese administration; Stage II's ip_ numbering
#   is not tied to it either. Instruments, from the Methods:
#   - GSES: Schwarzer & Jerusalem's General Self-Efficacy Scale, Chinese version
#     (CGSES; Cheung & Sun 1999). Register GSE (ship, originators' FAQ grant).
#     Chinese wording not deposited, and the CGSES translation's terms are
#     unestablished (register CGSES, hold, new 2026-11-09), so the originators'
#     English (userpage.fu-berlin.de/health/engscal.htm) ships as
#     translated_substitute, language Chinese, gsesK = item K (positional;
#     NO_ROUTE, verify_lam_2015.py). Built by make_itemtext_lam_2015.py.
#   - CPPS (cpps_stage1/2): the authors' "unofficial adaptation" of the IPQ-R
#     for genetic predisposition (Kaptein et al.), domain-swapped to cancer.
#     Register CPPS (hold, new 2026-11-09; domain-swap rule).
#   - CHQ-12: Chinese Health Questionnaire (Cheng & Williams; Chong & Wilkinson
#     1989), an adaptation of Goldberg's GHQ. Register CHQ (hold, new
#     2026-11-09; the GHQ row is block for all versions).
#   - C-LOT-R: register LOT-R is ship_with_note, but the Chinese wording is not
#     deposited and clot_1..6 cannot be tied to the LOT-R's scored items
#     without it (6 of 10 positions); not cheap, left for a later pass.
#
# PII: screened over all 86 + 54 columns. Two Stage I columns (d9.2, d9.4) read
#   as strings only because a blank ' ' cell sits among 0/1 codes; neither is
#   shipped. No names, emails, dates of birth or geography.

import os
import re
import socket
import sys
import tempfile

import pandas as pd
import requests
import urllib3.util.connection as _uc

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
BASE = ("https://journals.plos.org/plosone/article/file?type=supplementary"
        "&id=10.1371/journal.pone.0142620.")
RAW1 = os.environ.get("LAM_S1_RAW", "")
RAW2 = os.environ.get("LAM_S2_RAW", "")

GROUP1 = {0: "non-patient", 1: "HBsAg carrier"}
GROUP2 = {1: "healthy control", 2: "current smoker", 3: "passive smoker"}


def fetch(local, sid):
    if local:
        return local
    _uc.allowed_gai_family = lambda: socket.AF_INET  # IPv6 stalls here
    r = requests.get(BASE + sid, headers={"User-Agent": "IRW-Finder/1.0"},
                     timeout=120)
    r.raise_for_status()
    path = os.path.join(tempfile.mkdtemp(), f"lam_{sid}.csv")
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


def screen_for_pii(df, label, expect):
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])
               or df[c].dtype == object]
    print(f"PII screen {label}: {len(df.columns)} columns examined, "
          f"{len(strings)} string column(s): {strings}")
    assert len(df.columns) > 0
    assert strings == expect, strings
    for c in strings:   # blank-padded 0/1 codes, not text
        assert set(df[c].str.strip()) <= {"", "0", "1", "888", "999"}, c


def clean(long, lo, hi, name):
    long["resp"] = pd.to_numeric(long["resp"], errors="raise")
    n0 = len(long)
    sentinel = long["resp"].isin([777, 888, 999])
    frac = (long["resp"] % 1 != 0)
    long = long[~sentinel & ~frac].copy()
    assert long["resp"].between(lo, hi).all(), (name, sorted(long["resp"].unique()))
    long["resp"] = long["resp"].astype(int)
    print(f"  {name}: dropped {int(sentinel.sum())} missing-code and "
          f"{int(frac.sum())} imputed (non-integer) cells of {n0}")
    return long


def emit(long, name, lo, hi, cov_cols):
    assert len(name) <= 40
    long = long[["id", "item", "resp"] + cov_cols]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values=list(range(lo, hi + 1)))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-"
          f"{long['resp'].max()}")


def melt(df, items, cov_cols):
    return df.melt(id_vars=["id"] + cov_cols, value_vars=items,
                   var_name="item", value_name="resp")


def convert():
    s1 = pd.read_csv(fetch(RAW1, "s001"), low_memory=False)
    s2 = pd.read_csv(fetch(RAW2, "s002"))
    assert s1.shape == (290, 86) and s2.shape == (450, 54), (s1.shape, s2.shape)
    screen_for_pii(s1, "S1", ["d9.2", "d9.4"])
    screen_for_pii(s2, "S2", [])

    s1 = s1.rename(columns={"sub_no": "id"})
    s2 = s2.rename(columns={"subj_no": "id"})
    assert s1["id"].is_unique and s2["id"].is_unique
    assert not set(s1["id"]) & set(s2["id"]), "Stage I / II ids overlap"
    assert s1["group"].value_counts().to_dict() == {1: 167, 0: 123}
    assert s2["group"].value_counts().to_dict() == {3: 152, 2: 150, 1: 148}
    s1["cov_group"] = s1["group"].map(GROUP1)
    s2["cov_group"] = s2["group"].map(GROUP2)
    s1["cov_study"], s2["cov_study"] = 1, 2

    cpps1 = [c for c in s1.columns if re.fullmatch(r"IP_\d\d", c)]
    cpps2 = [c for c in s2.columns if re.fullmatch(r"ip_\d\d", c)]
    gses = [f"gses{i}" for i in range(1, 11)]
    chq = [f"chq{i}" for i in range(1, 13)]
    clot2 = [f"clot_{i}" for i in range(1, 7)]
    assert len(cpps1) == 28 and len(cpps2) == 28

    # balance the books: every item-like source column is shipped or named
    skipped1 = [f"CLOT_{i}" for i in range(1, 7)] + ["PGH", "PCH"]
    skipped2 = ["pgh", "pch"]
    other1 = [c for c in s1.columns if re.fullmatch(r"d\d+(\.\d+)?", c)]
    other2 = ["agegrou1", "gender01", "mar01", "edu", "ocu", "income"]
    acc1 = set(cpps1 + gses + chq + skipped1 + other1 + ["id", "group", "cov_group", "cov_study"])
    acc2 = set(cpps2 + gses + clot2 + skipped2 + other2 + ["id", "group", "cov_group", "cov_study"])
    assert acc1 == set(s1.columns), set(s1.columns) ^ acc1
    assert acc2 == set(s2.columns), set(s2.columns) ^ acc2
    print(f"not shipped -- S1: {skipped1} + {len(other1)} uncoded demographics; "
          f"S2: {skipped2} + {other2}")

    os.makedirs(OUT_DIR, exist_ok=True)
    cg = ["cov_group"]
    emit(clean(melt(s1, cpps1, cg), 1, 5, "cpps_stage1"), "lam_2015_cpps_stage1", 1, 5, cg)
    emit(clean(melt(s2, cpps2, cg), 1, 5, "cpps_stage2"), "lam_2015_cpps_stage2", 1, 5, cg)
    both = pd.concat([melt(s1, gses, ["cov_study"] + cg),
                      melt(s2, gses, ["cov_study"] + cg)], ignore_index=True)
    emit(clean(both, 1, 4, "gses"), "lam_2015_gses", 1, 4, ["cov_study"] + cg)
    emit(clean(melt(s1, chq, cg), 0, 3, "chq12"), "lam_2015_chq12", 0, 3, cg)
    emit(clean(melt(s2, clot2, cg), 1, 4, "clotr"), "lam_2015_clotr", 1, 4, cg)


if __name__ == "__main__":
    convert()
