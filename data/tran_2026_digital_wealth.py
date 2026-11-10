#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0353922
# DOI: 10.1371/journal.pone.0353922
# Paper: Tran MT, Pasekova M (2026). Digital financial literacy and trust in
#   hybrid AI advisory: Explaining perceived private wealth management
#   capability among digitally engaged retail investors in an emerging market.
#   PLOS ONE 21(10).
# Data: S1 File (XLSX, "Anonymized dataset"), 249 rows x 28 columns; S2 File
#   (XLSX) is the depositors' codebook: every variable's construct, item
#   wording and coding. Both attached to the article.
# License: CC BY 4.0 (the article's licence covers its SI files).
#
# Found by the PLOS monthly run of 2026-11-09 (leads/plos_leads_2026-11-09.csv,
# triage flag good).
#
# SEVEN output tables, one per construct, 3 items each, all on "1 = Strongly
# disagree; 2 = Disagree; 3 = Neutral; 4 = Agree; 5 = Strongly agree" (S2
# Codebook and Notes sheet). Item codes are the deposit's own headers.
# Constructs as the codebook names them:
#   DFL  Digital Financial Literacy
#   THA  Trust in Hybrid AI Advisory
#   PWMC Perceived Private Wealth Management Capability
#   PAAT Perceived AI Advisory Transparency
#   CSP  Cyber-risk Self-Protection
#   IWK  Investment and Wealth Knowledge
#   DWMB Digital Wealth Management Behavior
# Three items is the intake floor (datastandard, 2026-10-19); each construct
# is the paper's own reflective measurement block.
#
# Covariates (codebook labels, carried as the source's codes):
#   cov_gender (GEN: 1 = Male, 2 = Female), cov_age_group (AGE: 1 = 18-29,
#   2 = 30-39, 3 = 40-45, 4 = over 45), cov_education (EDU: 1 = Bachelor,
#   2 = Postgraduate, 3 = College/Intermediate, 4 = High School),
#   cov_income (INC: monthly income band 1-5), cov_invest_experience (EXP:
#   years band 1-5), cov_risk_tolerance (RIS: 1 = Very Low .. 5 = Very High).
#   RIS is a single self-rating the codebook lists under demographics; it is a
#   covariate, not an item.
# `id`: the deposit's Respondent_ID (R001-R249) is "an artificial anonymous
#   respondent identifier ... created for S1 only"; replaced by the row index
#   (the integer part of the same code), verified unique.
#
# Imputation: none. The codebook's Notes sheet: "249 observations, no missing
#   values in the analytic variables, and all 21 measurement items contain
#   only values from 1 to 5"; asserted below. No "imput" in the article.
#
# Item text: NOT SHIPPED. Cheap in form (the S2 codebook gives every stem), but
#   the paper says "Measurement items were adapted from established
#   construct-specific scales reported in prior studies, as summarized in
#   Table 1", so the rights question has to be answered per source scale; same
#   adapted-from-the-literature shape as zhao_2025_* (2026-10-30), left for a
#   general ruling rather than decided here. Stems are in S2 File, sheet
#   "Codebook", column "Description".
#
# PII: screened over all 28 columns; the only string column is the artificial
#   respondent code. Demographics are banded by the depositors.

import os
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
URL = ("https://journals.plos.org/plosone/article/file?type=supplementary"
       "&id=10.1371/journal.pone.0353922.s001")
RAW = os.environ.get("TRAN_RAW", "")

N_ROWS = 249
LO, HI = 1, 5
CONSTRUCTS = {
    "DFL": "tran_2026_digital_financial_literacy",
    "THA": "tran_2026_trust_hybrid_ai_advisory",
    "PWMC": "tran_2026_wealth_mgmt_capability",
    "PAAT": "tran_2026_ai_advisory_transparency",
    "CSP": "tran_2026_cyber_risk_self_protection",
    "IWK": "tran_2026_investment_knowledge",
    "DWMB": "tran_2026_digital_wealth_mgmt_behavior",
}
COVS = {"GEN": "cov_gender", "AGE": "cov_age_group", "EDU": "cov_education",
        "INC": "cov_income", "EXP": "cov_invest_experience",
        "RIS": "cov_risk_tolerance"}


def fetch():
    if RAW:
        return RAW
    _uc.allowed_gai_family = lambda: socket.AF_INET  # IPv6 stalls here
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=120)
    r.raise_for_status()
    path = os.path.join(tempfile.mkdtemp(), "tran_s1.xlsx")
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


def screen_for_pii(df):
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])
               or df[c].dtype == object]
    print(f"PII screen: {len(df.columns)} columns examined, {len(strings)} "
          f"string column(s): {strings}")
    assert len(df.columns) > 0
    assert strings == ["Respondent_ID"], strings
    assert df["Respondent_ID"].str.fullmatch(r"R\d{3}").all()


def convert():
    df = pd.read_excel(fetch(), sheet_name="Data")
    assert df.shape == (N_ROWS, 28), df.shape
    screen_for_pii(df)
    assert df["Respondent_ID"].is_unique
    df["id"] = df["Respondent_ID"].str[1:].astype(int)
    assert df["id"].is_unique
    df = df.rename(columns=COVS)
    cov_cols = list(COVS.values())

    items_all = []
    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, name in CONSTRUCTS.items():
        assert len(name) <= 40, name
        cols = [f"{prefix}{i}" for i in (1, 2, 3)]
        items_all += cols
        assert int(df[cols].isna().sum().sum()) == 0
        assert df[cols].isin(range(LO, HI + 1)).all().all(), name
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert not long.duplicated(["id", "item"]).any()
        long = long[["id", "item", "resp"] + cov_cols]
        checks = run_qc(long, permitted_values=list(range(LO, HI + 1)))
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-"
              f"{long['resp'].max()}")

    accounted = set(items_all) | set(cov_cols) | {"Respondent_ID", "id"}
    assert accounted == set(df.columns), set(df.columns) ^ accounted
    assert len(set(CONSTRUCTS.values())) == len(CONSTRUCTS)
    assert total == 21 * N_ROWS, total
    print(f"7 tables, {total} responses (21 items x {N_ROWS}); all source "
          f"columns accounted for")


if __name__ == "__main__":
    convert()
