#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0354954
# DOI: 10.1371/journal.pone.0354954
# Paper: Martinez A, Bautista A, Vazquez AL, et al. (2026). Mexican American
#   Cultural Values Scale: Considerations for college students. PLOS ONE
#   21(9): e0354954.
# Data: S1 File (journal.pone.0354954.s001, "MACVSanonymized", .csv), 495
#   Hispanic/Latinx US college students.
# License: CC BY 4.0 (the article; the data is its Supporting Information).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 3, BATCH_LOG.md).
#
# Three output tables, the deposit's own item codes:
#   martinez_2026_macvs  MACVS_1..50, Mexican American Cultural Values Scale
#                        (Knight et al. 2010), 1 not at all .. 5 completely.
#   martinez_2026_pedq   PEDQ_1..17, Perceived Ethnic Discrimination
#                        Questionnaire (Brondolo et al. 2005), 1 never
#                        happened, 3 sometimes, 5 happened very often (paper).
#                        The paper describes 18 items; the deposit has 17.
#   martinez_2026_sas    SAS_1..12, Short Acculturation Scale (Marin et al.
#                        1987), 1 only English, 2 English better than
#                        Spanish, 3 both equally, 4 Spanish better than
#                        English, 5 only Spanish (paper).
# Covariates: age, country of origin (heritage country, 18 values).
# Dropped: DEMO_Gender (1/2, no labels in the deposit or paper),
#   DEMO_Hispanic (constant 1).
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. A .csv of column codes (no labels at any level); the
#   wording of all three instruments is not in the article or SI. All three
#   are third-party instruments.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("MARTINEZ_RAW", "journal.pone.0354954.s001.csv")


def emit(name, df, items, cov_cols, permitted):
    long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
    long = long[long["resp"].notna()]
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(permitted)
    long = long[["id", "item", "resp"] + cov_cols]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    return name


def convert():
    df = pd.read_csv(RAW)
    assert df.shape == (495, 83)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert txt == ["DEMO_OriginCountry"] and df["DEMO_OriginCountry"].nunique() == 18
    df["id"] = range(1, len(df) + 1)
    df["cov_age"] = df["DEMO_Age"]
    df["cov_origin_country"] = df["DEMO_OriginCountry"]
    cov_cols = ["cov_age", "cov_origin_country"]
    macvs = [f"MACVS_{i}" for i in range(1, 51)]
    pedq = [f"PEDQ_{i}" for i in range(1, 18)]
    sas = [f"SAS_{i}" for i in range(1, 13)]
    os.makedirs(OUT_DIR, exist_ok=True)
    names = [emit("martinez_2026_macvs", df, macvs, cov_cols, [1, 2, 3, 4, 5]),
             emit("martinez_2026_pedq", df, pedq, cov_cols, [1, 2, 3, 4, 5]),
             emit("martinez_2026_sas", df, sas, cov_cols, [1, 2, 3, 4, 5])]
    assert len(set(names)) == len(names)
    dropped = ["DEMO_Gender", "DEMO_Hispanic"]
    assert set(df.columns) - {"id"} - set(cov_cols) == (set(macvs) | set(pedq) | set(sas)
                                                         | {"DEMO_Age", "DEMO_OriginCountry"} | set(dropped))
    print("dropped:", dropped)


if __name__ == "__main__":
    convert()
