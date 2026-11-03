#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0190749
# DOI: 10.1371/journal.pone.0190749
# Paper: Yu P, Qian S (2018). Developing a theoretical model and
#   questionnaire survey instrument to measure the success of electronic
#   health records in residential aged care. PLOS ONE 13(1): e0190749.
# Data: S3 Appendix "Original dataset" (journal.pone.0190749.s003, .csv),
#   243 staff of Australian residential aged-care facilities. (S6 Appendix,
#   the "refined dataset", is the same 243 rows minus the three SerQ
#   columns.)
# Items: S2 Appendix "Original measurement items"; questionnaire: S1
#   Appendix.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 5, BATCH_LOG.md).
#
# ONE output table:
#   yu_2018_ehr_success  EHR-success questionnaire, 24 agreement items: Tr1-3
#     training, SE1-2 self-efficacy, SysQ1-4 system quality, IQ1-4
#     information quality, SerQ1-3 service quality, US1 overall satisfaction,
#     NB1-7 net benefits. 1 strongly disagree, 2 disagree, 3 slightly
#     disagree, 4 neutral, 5 slightly agree, 6 agree, 7 strongly agree (S1
#     Appendix). The questionnaire's eighth option, 0 "don't know", is a
#     non-response and is set to missing (dropped).
# NOT shipped: U1-U3 (minutes per shift, log-ons per shift, number of
#   functions used) -- usage counts in bins, not agreement items.
# No covariates in the deposit. `id` is the row index.
#
# Item text: NOT SHIPPED. The English wording of every item is in S2
#   Appendix, and the survey was administered in English, but most items
#   are adapted from published IS-success / TAM instruments (DeLone &
#   McLean and others) with no rights reading.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("YU_EHR_RAW", "journal.pone.0190749.s003.csv")
ITEMS = (["Tr1", "Tr2", "Tr3", "SE1", "SE2"] + [f"SysQ{i}" for i in range(1, 5)] + [f"IQ{i}" for i in range(1, 5)]
         + [f"SerQ{i}" for i in range(1, 4)] + ["US1"] + [f"NB{i}" for i in range(1, 8)])
NOT_SHIPPED = {"U1", "U2", "U3"}


def convert():
    df = pd.read_csv(RAW)
    assert df.shape == (243, 27), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    df["id"] = range(1, len(df) + 1)
    long = df[["id"] + ITEMS].melt(id_vars=["id"], var_name="item", value_name="resp")
    dk = (long["resp"] == 0).sum()
    long = long[long["resp"] != 0].dropna(subset=["resp"])
    assert set(long["resp"]) <= set(range(1, 8))
    long["resp"] = long["resp"].astype(int)
    print(f"  dropped {dk} 'don't know' (0) cells")
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: list(range(1, 8)) for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    assert set(df.columns) - {"id"} == set(ITEMS) | NOT_SHIPPED
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "yu_2018_ehr_success.csv"), index=False)
    print(f"yu_2018_ehr_success: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
