#!/usr/bin/env python3
# Source: https://doi.org/10.34894/JLKINY
# DOI: 10.34894/JLKINY (deposit; the paper has no DOI in the deposit record)
# Paper: Manger G, van der Weide S (2025). The Effect of Analytical Rigor on
#   Accuracy of Intelligence Forecasts. Journal of European and American
#   Intelligence Studies 8(2).
# Data: DataverseNL dataset doi:10.34894/JLKINY, "Supplemental materials for
#   'The Effect of Analytical Rigor on Accuracy of Intelligence Forecasts'",
#   file Data_master.xlsx (datafile 555981, sheet "Data", format=original),
#   with Code book.docx (the scoring rubric) and README supplemental
#   materials.txt. 105 intelligence products written by Netherlands Ministry
#   of Defence personnel on the Combined Analysis Course, scored by the
#   authors in 2024.
# License: CC BY-NC-SA 4.0 on the DEPOSIT (DataverseNL dataset licence). NC
#   proceeds per datastandard.md (2026-10-01); Derived License carries it.
#
# Worked from the cleaned leads list of 2026-11-07 (rank 41; source
# leads/repos_leads_2026-10-07.csv), leads batch 1.
#
# ONE output table: manger_2025_analytic_rigor. The focal unit (`id`) is the
#   intelligence PRODUCT, not a person (datastandard.md: "typically a person,
#   but sometimes another entity"): each product was scored on the analytic-
#   rigor criteria in the deposit's Code book.docx, a 0-3 rubric per criterion
#   ("0 Poor" .. "3 Excellent"; criterion 1 is description of sources, data
#   and methodologies, criterion 2 expression of uncertainties, and so on).
#   Items are the deposit's own criterion_1..criterion_6 and criterion_8;
#   there is no criterion_7 column in the file. Criteria 1-3 hold 0-2 only as
#   deposited. The raters are the authors and are not identified per row, so
#   there is no `rater` column.
# Covariates: analyst gender, year of the product (2018-2023), individual or
#   group product, difficulty (as given).
# Dropped: rigor_score (the sum of the criteria), and the forecast-accuracy
#   variables (forecast, occurrence, period_months, brier_score, ln(BS),
#   failure, failure_num) -- outcomes about the forecast, not rubric scores.
# `id` is the deposit's product ID (1..227, 105 unique values).
#
# Item text: NOT SHIPPED. The rubric text is in Code book.docx; not built in
#   this batch.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://dataverse.nl/api/access/datafile/555981?format=original"
RAW = os.environ.get("MANGER_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ITEMS = [f"criterion_{k}" for k in (1, 2, 3, 4, 5, 6, 8)]
DROPPED = ["rigor_score", "brier_score", "failure_num", "failure", "forecast", "period_months", "occurrence",
           "ln(BS"]


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=120)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_excel(src, sheet_name="Data")


def convert():
    df = load()
    df.columns = [str(c).strip() for c in df.columns]
    assert len(df) == 105 and df["ID"].nunique() == 105
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and set(txt) == {"failure", "gender", "group_individ", "difficulty"}
    covmap = {"gender": "cov_gender", "year": "cov_year", "group_individ": "cov_group_individ",
              "difficulty": "cov_difficulty"}
    used = {"ID"} | set(ITEMS) | set(DROPPED) | set(covmap)
    assert used == set(df.columns), set(df.columns) ^ used
    df["id"] = df["ID"].astype(int)
    for src, dst in covmap.items():
        df[dst] = df[src].str.strip() if df[src].dtype == object else df[src]
    covs = list(covmap.values())
    long = df[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {0, 1, 2, 3}
    # the deposit's total is the sum of the criteria it ships
    tot = long.groupby("id")["resp"].sum()
    agree = (tot == df.set_index("id")["rigor_score"].reindex(tot.index)).mean()
    print(f"rigor_score equals the sum of shipped criteria on {agree:.1%} of products")
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [0, 1, 2, 3] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "manger_2025_analytic_rigor.csv"), index=False)
    print(f"manger_2025_analytic_rigor: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}; dropped {DROPPED}")


if __name__ == "__main__":
    convert()
