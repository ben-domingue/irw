#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0187041
# DOI: 10.1371/journal.pone.0187041
# Paper: Piccoli AB, Neiva-Silva L, Mosmann CP, et al. (2017). Adolescents'
#   perception of parental feeding practices: Adaptation and validation of the
#   Comprehensive Feeding Practices Questionnaire for Brazilian adolescents--
#   The CFPQ-Teen. PLOS ONE 12(11): e0187041.
# Data: S2 File (journal.pone.0187041.s002, "Databases", .sav), 455 Brazilian
#   adolescents aged 12-18 at public and private schools; 41 of them retested
#   in May 2013.
# License: CC BY 4.0 (the article; the data is its Supporting Information).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 3, BATCH_LOG.md).
#
# ONE output table, piccoli_2017_cfpq_teen: Q1..Q49, the CFPQ-Teen (the
# adolescent-report adaptation of Musher-Eizenman & Holub's CFPQ), twelve
# subscales named in each item's variable label. Two response formats within
# the one instrument, both 1-5 and both from the .sav's own value labels:
#   Q1-Q13  frequency  1 never, 2 almost never, 3 sometimes, 4 often, 5 always
#   Q14-Q49 agreement  1 disagree, 2 partly disagree, 3 neither, 4 partly
#                      agree, 5 strongly agree
# As administered: Q16, Q37 and Q42 are the reverse-keyed items and are NOT
# reversed (the deposit's *_R columns are recodes and are dropped).
# wave: 1 = the main administration (455); 2 = the retest of 41 adolescents
#   (Qk_CFPQTeen_2 and AFk_CFPQTeen_2, mapped back to Qk).
# Covariates: gender, age, school type (private/public), who the adolescent
#   names as the main feeding caregiver, and that caregiver's age (all from
#   the .sav's value labels).
# Dropped: Code (not unique: ten codes are shared by two different
#   adolescents; `id` is the row index), ICC (retest flag, carried by wave),
#   Age_Months (307 only), Q5_schooling (codes 1-5, only 1-4 labelled),
#   Date_retest, and every factor score (F1..F12, and their retest versions).
#
# Item text: NOT SHIPPED. The item variable labels are subscale names
#   ("Q1monitoring"), not stems (both levels checked; value labels are the
#   anchors only). The Portuguese questionnaire is S1 File
#   (journal.pone.0187041.s001, .doc), and the CFPQ is registered hold
#   (2026-10-31).

import os
import re
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("PICCOLI_RAW", "journal.pone.0187041.s002.sav")
NAME = "piccoli_2017_cfpq_teen"


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert df.shape == (455, 138)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0
    assert set(txt) <= {"Date_retest"}
    vl = meta.variable_value_labels
    items = [f"Q{i}" for i in range(1, 50)]
    df["id"] = range(1, len(df) + 1)
    df["cov_gender"] = df["Q1A_Gender"].map(vl["Q1A_Gender"])
    df["cov_age"] = df["Q3_Age"]
    df["cov_school_type"] = df["School_type"].map(vl["School_type"])
    df["cov_feeding_caregiver"] = df["Scale_CFPQTeen_caregiver"].map(vl["Scale_CFPQTeen_caregiver"])
    df["cov_caregiver_age"] = df["Scale_CFPQTeen_caregiver_age"]
    cov_cols = ["cov_gender", "cov_age", "cov_school_type", "cov_feeding_caregiver", "cov_caregiver_age"]
    w1 = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
    w1["wave"] = 1
    retest = {}
    for c in df.columns:
        m = re.fullmatch(r"(?:Q|AF)(\d+)_CFPQTeen_2", c)
        if m:
            retest[c] = f"Q{int(m.group(1))}"
    assert sorted(retest.values(), key=lambda s: int(s[1:])) == items
    rt = df[df["Date_retest"].notna() & (df["Date_retest"] != "")]
    assert len(rt) == 41
    w2 = rt[["id"] + cov_cols + list(retest)].rename(columns=retest).melt(
        id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
    w2["wave"] = 2
    long = pd.concat([w1, w2], ignore_index=True)
    long = long[long["resp"].notna()]
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) == {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp", "wave"] + cov_cols]
    assert not long.duplicated(["id", "item", "wave"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    used = set(items) | set(retest) | {"Q1A_Gender", "Q3_Age", "School_type", "Scale_CFPQTeen_caregiver",
                                       "Scale_CFPQTeen_caregiver_age"}
    dropped = [c for c in meta.column_names if c not in used]
    assert all(c in ("Code", "ICC", "Age_Months", "Q5_schooling", "Date_retest") or c.startswith("F")
               or c.endswith("_R") or c.endswith("_2R") for c in dropped), dropped
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"wave2 ids={long.loc[long.wave == 2, 'id'].nunique()}; dropped {len(dropped)}: {dropped}")


if __name__ == "__main__":
    convert()
