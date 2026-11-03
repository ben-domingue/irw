#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0210639
# DOI: 10.1371/journal.pone.0210639
# Paper: Novara C, Boiche J, Lebrun C, Macgregor A, Mateo Y, Raffard S (2019).
#   Disgust assessment: Factorial structure and psychometric properties of the
#   French version of the Disgust Propension and Sensibility Scale
#   Revised-12. PLOS ONE 14(1): e0210639.
# Data: S1 Data (journal.pone.0210639.s001, .xlsx), sheet
#   "VALID_FINAL_MODIFIE_OUTLIERS ok": 281 French adults from the general
#   population (online platform and paper questionnaires).
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 5, BATCH_LOG.md).
#
# PROCESSING DONE BY THE AUTHORS AND VISIBLE IN THE FILE (paper, Data
# analysis): 10 participants with <10% missing were multiply imputed (SPSS),
# and 14 univariate outliers (|z| > 3.29) "were replaced by the corresponding
# extreme, within a range of normal value". The imputed cells are the
# non-integer values and are DROPPED here. The 14 replaced cells are integer
# and cannot be told apart from real answers; they stay (14 cells in ~60,000).
#
# FIVE output tables, the instruments the paper describes in Measures:
#   novara_2019_dpssr   DPSS-R French, 12 items (DPSSR_1..12), 1-5
#     (Disgust Propensity and Sensitivity Scale-Revised; never .. always).
#   novara_2019_asir    Anxiety Sensitivity Index-Revised, 36 items, 1 "very
#     little" .. 5 "very much".
#   novara_2019_obq44   Obsessive Beliefs Questionnaire-44, 1 "strongly
#     disagree" .. 7 "strongly agree".
#   novara_2019_ocir    Obsessive-Compulsive Inventory-Revised, 18 items,
#     0 "not at all" .. 4 "extremely".
#   novara_2019_panas   PANAS, 20 items, 1 "not at all or very little" .. 5
#     "extremely".
# NOT shipped:
#   DSR_1..27 -- a 27-item disgust battery (DS-R shape, 0-4) the paper does
#     not describe anywhere; not shipped on the err-on-exclusion rule.
#   STAIB_1..20 -- the paper describes a 1-4 scale, but the file holds 0-4
#     on some items and 1-5 on others (scored, with an unstated recode).
#   R_DPSSR_1..12 -- the two-month retest. Only 75 people have item 1, yet the
#     other retest columns are filled (and mostly fractional) for far more:
#     the retest block is imputed, not observed.
#   All subscale/total columns (DS_*, DPSS_*, ISA_CS/CPC, STAI_B, OBQ_CP/R/IP,
#     OCI_* subscales, OCI, PANAS_P/N, R_* totals).
# Reverse-keyed items are as deposited.
# Covariates: age; gender (1 female / 2 male: 187/72 reproduces the paper's
#   "187 females, 72 males, 25 did not provide gender"). ETUDE and OCCUPATION
#   are dropped: their codes have no labels anywhere.
# `id` is the row index (the file's own ID REPONDANT is a sequence number).
#
# Item text: NOT SHIPPED. Column codes only (no labels at any level); the
#   French wording of none of the six instruments is in the article or SI.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("NOVARA_RAW", "journal.pone.0210639.s001.xlsx")
BLOCKS = {"dpssr": ("DPSSR_", 12, range(1, 6)), "asir": ("ISA_", 36, range(1, 6)),
          "obq44": ("OBQ_", 44, range(1, 8)), "ocir": ("OCI_", 18, range(0, 5)),
          "panas": ("PANAS_", 20, range(1, 6))}
NOT_SHIPPED_PREFIX = ("DSR_", "STAIB_", "R_DPSSR_")
COMPOSITES = {"DS_CORE", "DS_AR", "DS_CONTA", "DS_TOTAL", "DPSS_PROP", "DPSS_SENS1", "DPSS_SENS2",
              "DPSS_SENS3", "DPSS_SRD", "DPSS 2-10", "DPSS_TOTAL 311", "DPSS_TOTAL 29", "ISA_CS",
              "ISA_CPC", "STAI_B", "OBQ_CP", "OBQ_R", "OBQ_IP", "OCI_V", "OCI_L", "OCI_P", "OCI_N",
              "OCI_S", "OCI_A", "OCI", "PANAS_P", "PANAS_N", "R_PROP", "R_SENSI", "R_SENSI10",
              "R_DPSSTOTAL"}


def convert():
    df = pd.read_excel(RAW)
    assert df.shape == (281, 225), df.shape
    df.columns = [c.replace("\u00c2", "").replace("\u00a0", "").strip() for c in df.columns]
    df = df.copy()
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    assert df["GENRE"].value_counts().to_dict() == {1: 187, 2: 72}
    df["id"] = range(1, len(df) + 1)
    df["cov_age"] = df["AGE"]
    df["cov_gender"] = df["GENRE"].map({1: "female", 2: "male"})
    covs = ["cov_age", "cov_gender"]
    used = {"ID REPONDANT", "AGE", "GENRE", "ETUDE", "OCCUPATION"} | COMPOSITES
    used |= {c for c in df.columns if c.startswith(NOT_SHIPPED_PREFIX)}
    names, total = [], 0
    for block, (pfx, k, ok) in BLOCKS.items():
        items = [f"{pfx}{i}" for i in range(1, k + 1)]
        used |= set(items)
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        frac = long[long["resp"] % 1 != 0]
        out = long[(long["resp"] % 1 == 0) & ~long["resp"].isin(list(ok))]
        assert out.empty, out
        long = long[long["resp"] % 1 == 0].copy()
        long["resp"] = long["resp"].astype(int)
        print(f"  {block}: dropped {len(frac)} imputed (non-integer) cell(s)")
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(ok) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"novara_2019_{block}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert len(set(names)) == len(names)
    left = set(df.columns) - used - {"id"} - set(covs)
    assert not left, left
    print(f"total responses {total}")


if __name__ == "__main__":
    convert()
