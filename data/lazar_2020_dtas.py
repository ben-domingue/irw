#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0235957
# DOI: 10.1371/journal.pone.0235957
# Paper: Lazar IM, Panisoara G, Panisoara IO (2020). Digital technology
#   adoption scale in the blended learning context in higher education:
#   Development, validation and testing of a specific tool. PLOS ONE 15(7):
#   e0235957.
# Data: S4 Appendix "Data set" (journal.pone.0235957.s004, .xlsx), three
#   sheets: Stage 1 (250), Stage 2 (206), Stage 3 and 4 (262 + 310) --
#   1,028 Romanian university students in four independent samples, one per
#   development stage (item analysis, EFA, CFA, CFA).
# Questionnaire: S3 Appendix (journal.pone.0235957.s003), English.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 5, BATCH_LOG.md).
#
# ONE output table, the four samples stacked with cov_stage (same items,
# same 1-5 scale, administered by the same team; the paper's own
# development stages):
#   lazar_2020_dtas  Digital technology adoption / Blended Learning Scale
#     item pool, 1 "completely disagree" .. 5 "completely agree" (S3
#     Appendix). R1-R11 (no R7) familiarity with digital tools; CR1-5
#     obstacles; AT1-4 feelings (AT1-3 negatively worded, AT4 positive;
#     raw, as answered); PEU1-9 perceived ease of use; OR1-5 perceived
#     usefulness; BU1-3 intention to use. Stage 1 answered the 36-item pool;
#     items AT4, PEU7, PEU8 and PEU9 were dropped after Stage 1, so Stages
#     2-4 have 32 items.
# Not shipped: AT4r (Stage 1's reversed copy of AT4) and Total_scale.
# Covariates: stage, university, field of study, degree level, age. Gender
#   is NOT carried: Stages 1-2 spell it out, but Stages 3-4 code it 1/2 with
#   no label, and the paper never reports the split that would decode it.
# `id` is "s<stage>_<row>" so the four samples cannot collide.
#
# Item text: NOT SHIPPED. English stems for every code are in S3 Appendix,
#   but the students were Romanian (University of Bucharest), the
#   administration language is not stated, and several items are adapted
#   from published TAM / computer-anxiety scales with no rights reading.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LAZAR_RAW", "journal.pone.0235957.s004.xlsx")
META = ["Stage", "University", "Field of study", "Degree level ", "Age", "Gender"]
NOT_SHIPPED = {"AT4r", "Total_scale"}


def convert():
    sheets = pd.read_excel(RAW, sheet_name=None)
    assert list(sheets) == ["Stage 1", "Stage 2", "Stage 3 and 4"], list(sheets)
    parts = []
    for sname, df in sheets.items():
        txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
        print(f"PII screen [{sname}]: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
        assert len(df.columns) > 0 and set(txt) <= {"Stage", "University", "Field of study", "Degree level ", "Gender"}
        items = [c for c in df.columns if c not in META and c not in NOT_SHIPPED]
        assert set(df.columns) == set(META) | set(items) | (NOT_SHIPPED & set(df.columns)), sname
        df = df.copy()
        df["row"] = range(1, len(df) + 1)
        stage_no = df["Stage"].str.extract(r"(\d)")[0]
        df["id"] = "s" + stage_no + "_" + df["row"].astype(str)
        df["cov_stage"] = df["Stage"]
        df["cov_university"] = df["University"]
        df["cov_field"] = df["Field of study"]
        df["cov_degree"] = df["Degree level "]
        df["cov_age"] = df["Age"]
        covs = ["cov_stage", "cov_university", "cov_field", "cov_degree", "cov_age"]
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        parts.append(long.dropna(subset=["resp"]))
    long = pd.concat(parts, ignore_index=True)
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    items = sorted(long["item"].unique())
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "lazar_2020_dtas.csv"), index=False)
    print(f"lazar_2020_dtas: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    print(long.groupby("cov_stage")["id"].nunique().to_dict())


if __name__ == "__main__":
    convert()
