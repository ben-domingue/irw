#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0186143
# DOI: 10.1371/journal.pone.0186143
# Paper: Li, H., Luo, X., Ke, X., Dai, Q., Zheng, W., Zhang, C., Cassidy, R. M.,
#   Soares, J. C., Zhang, X., & Ning, Y. (2017). Major depressive disorder and
#   suicide risk among adult outpatients at several general hospitals in a
#   Chinese Han population. PLOS ONE 12(10): e0186143.
# Data: journal.pone.0186143.s003 (S1 Dataset, "Screening database", .sav).
#   5,284 adult outpatients at four tertiary general hospitals in Guangzhou,
#   March-June 2016 (gastroenterology, cardiology, gynecology and neurology
#   clinics).
# License: CC0 1.0 (the article's own licence statement; the data is its
#   Supporting Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30, worked from
# leads/plos_leads_2026-10-30.csv on 2026-10-31 (BATCH_LOG.md).
#
# THREE output tables, one per self-report instrument the paper documents:
#   li_2017_gad7    GADSEV1..7,   0-3  (GAD-7, "from 0 (not at all) to 3
#                                       (nearly every day)")
#   li_2017_phq9    PHQNIN1..9,   0-3  (PHQ-9, same scale)
#   li_2017_phq15   PHQFIF1..15,  0-2  (PHQ-15, "from 0 (not bothered at all)
#                                       to 2 (bothered a lot)")
# The .sav has NO variable or value labels on any item column (checked both
# levels: 11 of 119 columns carry labels, all of them covariates). The
# identification is from the column names plus the deposit's own total-score
# columns: GADSEV8 equals the sum of GADSEV1-7 on 99.96% of rows, PHQNIN10 the
# sum of PHQNIN1-9 on 100%, PHQFIF16 the sum of PHQFIF1-15 on 99.8%, which
# pins each block as the instrument's items in order. The totals are derived
# and are not shipped.
#
# Not shipped: SLEEP1-8 (two sleep-duration columns and six 0-3/0-4 columns
# the paper describes only as "3 questions validated for screening" insomnia,
# with no response scale stated); the SF-12 (present only as the two
# component scores AGG_PHYS1/AGG_MENT1 -- aggregates, not items); the MINI
# interview modules (A1.., B1.., C1.., diagnostic yes/no items answered by a
# psychiatrist for the 120 respondents who screened positive -- a skip-gated
# clinical interview, not a battery); DRINKING1-3, SMOKING1-4.
#
# `id` is the row index. The deposit's RESPONDENT column is 1..5284 except
# that 3864 and 4898 each appear twice, so it is not used as the id.
#
# Covariates are the labelled columns only: sex, marital status (deposit
# labels), education in years, employment, and the four MINI-derived
# diagnostic flags (MDD, bipolar, anxiety disorder, suicide risk) plus the
# insomnia flag, each carried as 0/1 with the deposit's own meaning. CENTER,
# DEPARTMENT, INCOME, AIM, PAYMENT, LIVINGCOND, RESIDENCE and the 1-5 age
# band are unlabelled integer codes with no codebook and are dropped.
#
# Item text: NOT SHIPPED. Both label levels are empty for every item column,
# and the three instruments are the PHQ/GAD screener family, which the
# register already carries as `ship` -- so the text is recoverable from the
# canonical instruments by a later pass, but nothing in this deposit says
# which wording (the Chinese versions) was administered.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LI_RAW", "S1_Dataset.sav")
N_ROWS = 5284

BLOCKS = {
    "li_2017_gad7": ([f"GADSEV{i}" for i in range(1, 8)], "GADSEV8", 0, 3),
    "li_2017_phq9": ([f"PHQNIN{i}" for i in range(1, 10)], "PHQNIN10", 0, 3),
    "li_2017_phq15": ([f"PHQFIF{i}" for i in range(1, 16)], "PHQFIF16", 0, 2),
}


def convert():
    df, meta = pyreadstat.read_sav(RAW, apply_value_formats=False)
    assert len(df) == N_ROWS, len(df)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert set(txt) == {"B1", "B1A", "B1B"}   # MINI yes/no letters, read: Y/N/Q/U/E only
    for c in txt:
        assert set(df[c].astype(str).str.strip()) <= {"", "N", "Q", "Y", "n", "U", "E"}, c
    labelled = [c for c in df.columns if meta.column_names_to_labels.get(c)]
    print(f"{len(labelled)} labelled columns: {labelled}")
    assert not any(c.startswith(("GADSEV", "PHQNIN", "PHQFIF")) for c in labelled)

    df["id"] = range(1, N_ROWS + 1)
    assert df["RESPONDENT"].duplicated().sum() == 2
    vl = meta.variable_value_labels
    cov = pd.DataFrame({
        "id": df["id"],
        "cov_sex": df["SEX"].map({1: "male", 2: "female"}),  # 1,791 vs 3,492: paper says 66.2% women
        "cov_marital_status": df["MARITAL"].map({1: "single", 2: "married", 3: "divorced", 4: "widowed"}),
        "cov_education_years": df["EDUCATION"],
        "cov_employed": df["occupationgroup"].map({1: 1, 2: 0}),
        "cov_mdd": df["MDD"].astype(int),
        "cov_bipolar_disorder": df["Bipolordisorders"].astype(int),
        "cov_anxiety_disorder": df["Anxietydisorders"].astype(int),
        "cov_suicide_risk": df["suiciderisk"].astype(int),
        "cov_insomnia": df["insomnia"].astype(int),
    })
    assert abs((cov["cov_sex"] == "female").mean() - 0.662) < 0.005
    assert vl["MDD"][1.0] == "MDD" and vl["suiciderisk"][1.0] == "suicide risk"
    assert vl["occupationgroup"] == {1.0: "employed", 2.0: "none employed"}
    # MARITAL has no value label; the paper reports 79.4% married and code 2 is 4,199/5,176
    assert abs((df["MARITAL"] == 2).sum() / N_ROWS - 0.794) < 0.005
    cov_cols = [c for c in cov.columns if c != "id"]

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, (cols, total_col, lo, hi) in BLOCKS.items():
        wide = df[["id"] + cols]
        agree = (wide[cols].sum(axis=1) == df[total_col]).mean()
        print(f"{name}: deposit total reproduces from the items on {agree:.2%} of rows")
        assert agree > 0.99
        assert int(wide[cols].isna().sum().sum()) == 0
        long = wide.melt(id_vars=["id"], value_vars=cols, var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) == set(range(lo, hi + 1)), sorted(long["resp"].unique())
        long = long.merge(cov, on="id", how="left")[["id", "item", "resp"] + cov_cols]
        assert long["id"].nunique() == N_ROWS and long["item"].nunique() == len(cols)
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(range(lo, hi + 1)) for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} resp={lo}-{hi}")
    print(f"TOTAL responses: {total}")


if __name__ == "__main__":
    convert()
