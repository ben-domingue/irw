#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0120493
# DOI: 10.1371/journal.pone.0120493
# Paper: Guo W, Xue J-M, Shao D, Long Z-T, Cao F-L (2015). Effect of the
#   interplay between trauma severity and trait neuroticism on posttraumatic
#   stress disorder symptoms among adolescents exposed to a pipeline
#   explosion. PLOS ONE 10(3): e0120493.
# Data: S1 Dataset (journal.pone.0120493.s001, legacy .xls), 662 students of a
#   junior middle school (grades 7-8) next to the 2013 Qingdao pipeline
#   explosion, assessed one month after it.
# License: CC BY 4.0 (the article; the data is its Supporting Information).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 3, BATCH_LOG.md).
#
# Two output tables:
#   guo_2015_pcl          pcl1..pcl17, PTSD Checklist-Civilian (PCL-C),
#                         1 "not at all" .. 5 "extremely". Verified: a PCL
#                         total >= 38 gives 13.1% (87/662), the paper's figure.
#   guo_2015_neuroticism  neuroticism1..12, NEO-FFI Neuroticism subscale,
#                         1-5 as deposited. The paper says "1 (strong
#                         approval) to 5 (strong disapproval)"; items 1, 4, 7,
#                         10 are the NEO-FFI's reverse-keyed N items and are
#                         NOT re-keyed here.
# Covariate: age. Dropped: Gender and Grade (1/2 codes with no labels in the
#   deposit or the paper), and the six Explosion Exposure Questionnaire items
#   (Family1..Perceived6: mixed 1-2/1-3/1-4 codes with no labels).
# `id` is the row index (the deposit has no id column).
#
# Item text: not shipped -- both label levels absent (legacy .xls, column
#   names only); the Chinese PCL-C and NEO-FFI wording is not in the article
#   or SI. NEO-FFI is registered block (PAR); PCL-C (Weathers 1993) has no row.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("GUO_RAW", "journal.pone.0120493.s001.xls")


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
    df = pd.read_excel(RAW, engine="xlrd")
    assert len(df) == 662 and len(df.columns) == 38
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert txt == []
    df["id"] = range(1, len(df) + 1)
    df["cov_age"] = df["Age"]
    pcl = [f"pcl{i}" for i in range(1, 18)]
    neu = [f"neuroticism{i}" for i in range(1, 13)]
    assert (df[pcl].sum(axis=1) >= 38).sum() == 87
    os.makedirs(OUT_DIR, exist_ok=True)
    names = [emit("guo_2015_pcl", df, pcl, ["cov_age"], [1, 2, 3, 4, 5]),
             emit("guo_2015_neuroticism", df, neu, ["cov_age"], [1, 2, 3, 4, 5])]
    assert len(set(names)) == len(names)
    dropped = ["Gender", "Grade", "Family1", "Friends2", "Witness3", "House4", "Property5", "Perceived6"]
    assert set(df.columns) - {"id", "cov_age"} == set(pcl) | set(neu) | {"Age"} | set(dropped)
    print("dropped:", dropped)


if __name__ == "__main__":
    convert()
