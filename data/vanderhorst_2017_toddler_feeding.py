#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0178149
# DOI: 10.1371/journal.pone.0178149
# Paper: van der Horst, K., & Sleddens, E. F. C. (2017). Parenting styles,
#   feeding styles and food-related parenting practices in relation to
#   toddlers' eating styles: A cluster-analytic approach. PLOS ONE 12(5):
#   e0178149.
# Data: journal.pone.0178149.s002 (S1 Datafile, .xlsx, sheets 'Data parenting
#   paper' and 'Variable labels'). 1,005 US mothers/caregivers of a child aged
#   12-36 months, online survey, 2012.
# License: CC BY 4.0 (the article; the data is its own Supporting Information
#   file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30, worked from
# leads/plos_leads_2026-10-30.csv on 2026-10-31 (BATCH_LOG.md).
#
# FIVE output tables, the five instrument blocks the workbook's own
# 'Variable labels' sheet names item by item (every item column has its full
# stem there; all 1-5, no missing cell anywhere):
#   vanderhorst_2017_cebq    CEBQ_1..35   Children's Eating Behaviour
#                                         Questionnaire (Wardle et al. 2001),
#                                         "My child loves food." ...
#   vanderhorst_2017_cfsq    CFSQ_1..19   Caregiver's Feeding Styles
#                                         Questionnaire (Hughes et al. 2005),
#                                         "Physically struggle with your child
#                                         to get him or her to eat ..."
#   vanderhorst_2017_cgpq    CGPI_1..69   Comprehensive General Parenting
#                                         Questionnaire (Sleddens et al. 2014;
#                                         the deposit's column prefix is CGPI),
#                                         "I encourage my child to be curious
#                                         and to explore things."
#   vanderhorst_2017_cfpq_a  CFPP_1..13   Comprehensive Feeding Practices
#                                         Questionnaire (Musher-Eizenman &
#                                         Holub 2007), the frequency-format
#                                         items ("How much do you keep track of
#                                         the sweets ...")
#   vanderhorst_2017_cfpq_b  CFPPb_14..46 the CFPQ's agreement-format items
#                                         ("Most of the food I keep in the
#                                         house is healthy.")
# The CFPQ ships as two tables because the deposit splits it into two blocks
# with two response formats (the workbook's own prefixes CFPP and CFPPb);
# both are 1-5 and the item numbers run 1-13 and 14-46 across the two.
#
# Item codes are the workbook's column names with the trailing "_slice"
# dropped (CEBQ_1_slice -> CEBQ_1), so the 'Variable labels' sheet's stem for
# each column is the stem for each code.
#
# `id` is the deposit's own Respondent_Serial (unique).
#
# Covariates: caregiver age in years, child age in months, child sex code
# (1/2, no label), number of children under 18 in the household, US region
# code 1-4, education code 1-8, household income code 1-7 (the workbook
# gives the question wording for these but not the code meanings, so the
# codes ship as codes with the question named in the column). DEM_1 (gender)
# is 1 for every respondent and is dropped as constant.
#
# Item text: NOT SHIPPED. The stems are in hand for all 169 items (the
# 'Variable labels' sheet), so this is a rights hold on four third-party
# instruments -- the CEBQ (Wardle), CFSQ (Hughes), CFPQ (Musher-Eizenman &
# Holub) and the CGPQ (Sleddens, a co-author here, but the instrument's own
# terms are what govern); register rows added as holds. The anchors are not
# in the deposit either.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("VANDERHORST_RAW", "S1_Datafile.xlsx")
N_ROWS = 1005
BLOCKS = {
    "vanderhorst_2017_cebq": ("CEBQ_", 35),
    "vanderhorst_2017_cfsq": ("CFSQ_", 19),
    "vanderhorst_2017_cgpq": ("CGPI_", 69),
    "vanderhorst_2017_cfpq_a": ("CFPP_", 13),
    "vanderhorst_2017_cfpq_b": ("CFPPb_", 33),
}


def convert():
    x = pd.ExcelFile(RAW)
    df = x.parse("Data parenting paper")
    vl = x.parse("Variable labels", header=None)
    stems = dict(zip(vl[0].astype(str), vl[1].astype(str)))
    assert len(df) == N_ROWS, len(df)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert not txt
    assert df["Respondent_Serial"].is_unique
    assert (df["DEM_1"] == 1).all()

    cov = pd.DataFrame({
        "id": df["Respondent_Serial"].astype(int),
        "cov_caregiver_age": df["DEM_1_1"].astype(int),
        "cov_child_age_months": df["DEM_10"].astype(int),
        "cov_child_sex_code": df["DEM_11"].astype(int),
        "cov_n_children_under_18": df["DEM_14"].astype(int),
        "cov_us_region_code": df["DEM_15"].astype(int),
        "cov_education_code": df["DEM_7"].astype(int),
        "cov_income_code": df["DEM_8"].astype(int),
    })
    assert cov["cov_child_age_months"].between(12, 36).all()
    cov_cols = [c for c in cov.columns if c != "id"]

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, (pre, n) in BLOCKS.items():
        cols = [c for c in df.columns if c.startswith(pre) and c.endswith("_slice")]
        assert len(cols) == n, (name, len(cols))
        for c in cols:
            assert len(stems.get(c, "")) > 10, (c, stems.get(c))
        wide = df[["Respondent_Serial"] + cols].rename(columns={"Respondent_Serial": "id"})
        assert int(wide[cols].isna().sum().sum()) == 0
        long = wide.melt(id_vars=["id"], value_vars=cols, var_name="item", value_name="resp")
        long["item"] = long["item"].str.replace(r"_slice$", "", regex=True)
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) == {1, 2, 3, 4, 5}, (name, sorted(long["resp"].unique()))
        long = long.merge(cov, on="id", how="left")[["id", "item", "resp"] + cov_cols]
        assert long["id"].nunique() == N_ROWS and long["item"].nunique() == n
        checks = run_qc(long, permitted_values={re.sub(r"_slice$", "", c): [1, 2, 3, 4, 5] for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} resp=1-5")
    print(f"TOTAL responses: {total}")


if __name__ == "__main__":
    convert()
