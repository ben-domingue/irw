#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0341597
# DOI: 10.1371/journal.pone.0341597
# Paper: Duc NT, Ninh NA, Trinh NP, Tuyen LQ, Hung NV, Khanh DH, et al. (2026).
#   Integration of the Pirogov interactive anatomy table into anatomy teaching:
#   A comparative study with cadaveric dissection. PLoS One 21(1): e0341597.
# Data: PLOS Supporting Information S2 File (journal.pone.0341597.s002, "Raw
#   dataset for the study analyses", sheet "Điểm"), 188 medical students,
#   Vietnam.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (rank 31; source
# leads/plos_leads_2026-10-30.csv), leads batch 1.
#
# ONE output table: duc_2026_pirogov_perceptions -- the 10-item student
#   perception questionnaire Q1..Q10, "a five-point Likert scale
#   (1 = strongly disagree, 5 = strongly agree), adapted from previously
#   published international studies". The paper groups the ten items into
#   four themes (its Table 1); the themes are 2-3 items each and the authors
#   report the questionnaire as one instrument, so it ships as one table.
#   Q1 and Q3 hold 1, 3, 4, 5 only as deposited (nobody chose 2).
# Covariates: gender (F/M; five trailing spaces in the deposit stripped), year
#   of study (Y1/Y2), group (A = Pirogov-table section first, B = cadaveric
#   dissection first; the groups swapped after the post-test and BOTH then
#   answered this questionnaire, so group is the order and is not `treat`).
#   Age is carried as given.
# Dropped: Pretest and Posttest (each a 20-item knowledge-test SCORE; the
#   per-question answers are not in the deposit).
# `id` is the deposit's Student No. (1..188, unique).
#
# Item text: NOT SHIPPED. Header codes only (Q1..Q10), no labels at either
#   level; the wording is in the article's Table 1, which PLOS serves as an
#   image only.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0341597.s002&type=supplementary"
RAW = os.environ.get("DUC_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ITEMS = [f"Q{i}" for i in range(1, 11)]
DROPPED = ["Pretest", "Posttest"]


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=120)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_excel(src, sheet_name=0)


def convert():
    df = load()
    assert list(df.columns) == ["Student No.", "Age", "Gender", "Grade", "Group"] + DROPPED + ITEMS, list(df.columns)
    assert len(df) == 188 and df["Student No."].nunique() == 188
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and set(txt) == {"Gender", "Grade", "Group"}
    df["id"] = df["Student No."].astype(int)
    df["cov_gender"] = df["Gender"].str.strip()
    assert set(df["cov_gender"]) == {"F", "M"}
    df["cov_age"] = df["Age"]
    df["cov_year"] = df["Grade"].str.strip()
    df["cov_group"] = df["Group"].str.strip()
    covs = ["cov_gender", "cov_age", "cov_year", "cov_group"]
    long = df[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "duc_2026_pirogov_perceptions.csv"), index=False)
    print(f"duc_2026_pirogov_perceptions: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}; dropped {DROPPED}")


if __name__ == "__main__":
    convert()
