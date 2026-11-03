#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0242562
# DOI: 10.1371/journal.pone.0242562
# Paper: Tasic R, Rajovic N, Pavlovic V, Djikanovic B, Masic S, Velickovic I,
#   et al. (2020). Nursery teachers in preschool institutions facing burnout:
#   Are personality traits attributing to its development? PLOS ONE 15(11):
#   e0242562.
# Data: S1 File "Minimal data set" (journal.pone.0242562.s001, .xls), 302
#   female nursery teachers (health care professionals) in all of Belgrade's
#   preschool institutions, stratified cluster sample.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 5, BATCH_LOG.md).
#
# TWO output tables (the workbook's Legend sheet: "M1-16 MBI questionnaire",
# "V1-70 Big Five Plus Two questionnaire"):
#   tasic_2020_mbigs  Maslach Burnout Inventory - General Survey, Serbian
#     adaptation, M_1..M_16, 0 "never" .. 6 "everyday" (paper, Methods).
#   tasic_2020_bf2    Big Five Plus Two, shortened 70-item version,
#     V_1..V_70, 1 "strongly disagree" .. 5 "strongly agree" (paper). One
#     out-of-range cell (V_26 = 42, a keying slip) is dropped.
# Reverse-keyed items are as deposited (the paper does not say whether the
# file holds raw or scored answers).
# cluster_id = preschool institution (the sampling cluster; 17 institutions).
# Covariates: age, years of service, professional qualification, executive
#   position, self-rated socio-economic status. Gender is constant (all
#   female) and is not carried.
# `id` is the row index.
#
# Item text: NOT SHIPPED. Column codes only (no labels at any level); the
#   Serbian wording is in neither the article nor the SI. MBI-GS is a
#   commercial instrument (Mind Garden; adapted under licence, per the paper).

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("TASIC_RAW", "journal.pone.0242562.s001.xls")
COVS = {"Age": "cov_age", "Lenght_of_service": "cov_years_service",
        "Level_professional_qualification": "cov_qualification",
        "Executive_position": "cov_executive_position", "Socio_economic_status": "cov_ses"}
BLOCKS = {"mbigs": ([f"M_{i}" for i in range(1, 17)], range(0, 7)),
          "bf2": ([f"V_{i}" for i in range(1, 71)], range(1, 6))}


def convert():
    df = pd.read_excel(RAW, sheet_name="minimal data set")
    assert df.shape == (302, 93), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0
    assert set(df["Gender"]) == {"female"}
    assert df["Preschool_institution"].str.match(r"^Preschool Institution \d+$").all()
    df["id"] = range(1, len(df) + 1)
    df["cluster_id"] = df["Preschool_institution"].str.extract(r"(\d+)$")[0].astype(int)
    for s, t in COVS.items():
        df[t] = df[s]
    covs = list(COVS.values())
    used = set(COVS) | {"Gender", "Preschool_institution"}
    names, total = [], 0
    for block, (items, ok) in BLOCKS.items():
        used |= set(items)
        long = df[["id", "cluster_id"] + covs + items].melt(id_vars=["id", "cluster_id"] + covs,
                                                           var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        bad = long[~long["resp"].isin(list(ok))]
        print(f"  {block}: dropping {len(bad)} out-of-range cell(s): {bad[['id', 'item', 'resp']].values.tolist()}")
        long = long[long["resp"].isin(list(ok))].copy()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp", "cluster_id"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(ok) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"tasic_2020_{block}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert len(set(names)) == len(names)
    assert used == set(df.columns) - {"id", "cluster_id"} - set(covs), set(df.columns) - used
    print(f"total responses {total}")


if __name__ == "__main__":
    convert()
