#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0239721
# DOI: 10.1371/journal.pone.0239721
# Paper: Jackson, D. L., Frey, M. P., McLellan, C., Rauti, C. M., Lamborn,
#   P. B., & Singleton-Jackson, J. A. (2020). I deserve more A's: A report on the development of
#   a measure of academic entitlement. PLOS ONE 15(9): e0239721.
# Data: University of Windsor Dataverse (Borealis) 10.5683/SP2/3JPURV,
#   AESManuscriptDataverse.sav (downloaded with format=original, not the
#   .tab conversion), 912 University of Windsor undergraduates (psychology
#   participant pool) after the paper's cleaning steps.
# License: CC0 1.0, verified on the DEPOSIT (Dataverse API, license
#   "CC0 1.0"); the article is CC BY 4.0.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# FOUR output tables:
#   jackson_2020_aes_pool  AEQ1-AEQ52: the 52-item administered pool from
#       which the paper's 30-item Academic Entitlement Scale (AES) was
#       selected -- items written by the authors plus items culled from
#       published AE measures. 1 strongly disagree .. 7 strongly agree.
#   jackson_2020_kopp_aeq  AEQ_K1-AEQ_K8: Kopp et al.'s 8-item Academic
#       Entitlement Questionnaire, 1-7.
#   jackson_2020_pni       PNI1-PNI50: Pathological Narcissism Inventory
#       (Pincus et al. 2009), 50 of its 52 items -- the paper says two were
#       omitted from the online form by mistake. 1 "not at all like me" ..
#       6 "very much like me".
#   jackson_2020_leq       LEQ1-LEQ13: Legitimate Entitlement Questionnaire,
#       13-item version as administered, 1 "not at all true" .. 7
#       "definitely true".
# All as deposited; nothing reversed.
#
# IMPUTED CELLS DROPPED. 342 of the 112,176 item cells hold non-integer
# values (e.g. AEQ3 = 3.9112): the deposit was missing-value imputed after
# the paper's cleaning (which removed cases with >10% missing), and these
# are the imputations. Integer cells are real responses and are kept; the
# fractional ones are dropped, so those person-items are simply absent.
#
# Covariate: gender (1 Female / 2 Male / 3 Other, the .sav's value labels;
# 3 blank). The deposit's 16 derived subscale scores are dropped.
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. Every item's stem is in the .sav's variable labels
#   ("AEQ | Great academic success should just come to me."), but (a) the
#   labels' curly quotes and apostrophes were destroyed in an encoding round
#   trip ("A" becomes "â??Aâ?_"), so the wording would have to be repaired by
#   hand, and (b) the AES pool mixes the authors' items with items taken
#   from published measures, and the Kopp AEQ, PNI and LEQ are named
#   third-party instruments -- no register grant for any of them.

import os
import sys

import numpy as np
import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("JACKSON_RAW", "AESManuscriptDataverse.sav")
N_ROWS = 912
TABLES = {
    "aes_pool": ([f"AEQ{i}" for i in range(1, 53)], range(1, 8)),
    "kopp_aeq": ([f"AEQ_K{i}" for i in range(1, 9)], range(1, 8)),
    "pni": ([f"PNI{i}" for i in range(1, 51)], range(1, 7)),
    "leq": ([f"LEQ{i}" for i in range(1, 14)], range(1, 8)),
}
DERIVED = ["GeneralAE", "RewardForEffort", "Accomodation", "ResponsibilityAvoidance", "CustomerOrientation",
           "CustomerService", "GradeHaggling", "ContingentSelfEsteem", "Exploitative",
           "SelfSacrificingSelfEnhancemnet", "HidingSelf", "GrandioseFantasy", "Devaluing", "EntitlementRage",
           "KoppAEQ", "LegitimateEntitlementReduced"]


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert txt == ["Gender"] and set(df["Gender"]) == {"", "1", "2", "3"}
    df["id"] = range(1, N_ROWS + 1)
    df["cov_gender"] = df["Gender"].map(meta.variable_value_labels["Gender"])
    names, total, dropped = [], 0, 0
    for suffix, (items, scale) in TABLES.items():
        long = df[["id", "cov_gender"] + items].melt(id_vars=["id", "cov_gender"], var_name="item",
                                                     value_name="resp")
        assert long["resp"].notna().all()
        frac = (long["resp"] % 1) != 0
        dropped += int(frac.sum())
        long = long[~frac].copy()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(scale), (suffix, set(long["resp"]))
        long = long[["id", "item", "resp", "cov_gender"]]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(scale) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {suffix} {c.name}: {c.detail[:160]}")
        name = f"jackson_2020_{suffix}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert dropped == 342, dropped
    assert len(set(names)) == len(names)
    accounted = {c for items, _ in TABLES.values() for c in items} | set(DERIVED) | {"Gender"}
    assert set(meta.column_names) == accounted, set(meta.column_names) ^ accounted
    print(f"total responses {total}; dropped {dropped} imputed (non-integer) cells and {len(DERIVED)} derived scores")


if __name__ == "__main__":
    convert()
