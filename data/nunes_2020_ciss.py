#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0229511
# DOI: 10.1371/journal.pone.0229511
# Paper: Nunes AF, Monteiro PL, Nunes AS (2020). Factor structure of the
#   convergence insufficiency symptom survey questionnaire. PLoS ONE 15(2):
#   e0229511.
# Data: PLOS Supporting Information S1 Dataset (journal.pone.0229511.s001,
#   sheet "CISS-AFE"), 183 higher-education students, University of Beira
#   Interior, Portugal. S2 Dataset is byte-for-byte the same data (every ID
#   and every item cell equal), so only S1 is read.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (rank 26; source
# leads/plos_leads_2026-10-30.csv), leads batch 1.
#
# ONE output table: nunes_2020_ciss -- the Convergence Insufficiency Symptom
#   Survey (Portuguese version), 15 items I1..I15, 0-4. The paper: "The
#   response to each item ranges from 'never' to 'always' on a 5-level Likert
#   scale"; the file codes it 0-4. I3, I7 and I10 hold 0-3 only as deposited
#   (nobody answered "always"), which is a fact about the responses.
# Covariates: gender (2 = female, 1 = male: 94/183 = 51.4% are coded 2 and the
#   paper reports 51.5% female), age, degree course (the deposit's "Class").
# `id` is the row index; the deposit's ID column mixes short numbers with
#   student-number-shaped codes and is not carried.
#
# Item text: NOT SHIPPED. The file has header codes only (I1..I15), no labels
#   at either level; the CISS is a published instrument (Borsting et al.) and
#   the Portuguese wording is the cited translation [23], not in the deposit.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0229511.s001&type=supplementary"
RAW = os.environ.get("NUNES_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
GENDER = {1: "male", 2: "female"}


def load():
    if RAW:
        return pd.read_excel(RAW, sheet_name="CISS-AFE")
    r = requests.get(URL, headers=HDR, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name="CISS-AFE")


def convert():
    df = load()
    items = [f"I{i}" for i in range(1, 16)]
    assert list(df.columns) == ["ID", "Class", "Gender", "Age"] + items, list(df.columns)
    assert len(df) == 183, len(df)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and set(txt) <= {"ID", "Class"}
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df["cov_gender"] = df["Gender"].map(GENDER)
    assert df["cov_gender"].notna().all()
    df["cov_age"] = df["Age"]
    df["cov_course"] = df["Class"].astype(str).str.strip()
    covs = ["cov_gender", "cov_age", "cov_course"]
    assert {"ID", "Class", "Gender", "Age"} | set(items) == set(df.columns) - {"id"} - set(covs)
    long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {0, 1, 2, 3, 4}
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [0, 1, 2, 3, 4] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "nunes_2020_ciss.csv"), index=False)
    print(f"nunes_2020_ciss: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
