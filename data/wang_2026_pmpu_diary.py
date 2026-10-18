#!/usr/bin/env python3
# Source: https://zenodo.org/records/20826719
# DOI: 10.5281/zenodo.20826719
# Data: data.sav (SPSS; only two variable labels in the whole file, both on
#   z-score columns, and NO value labels anywhere)
# License: CC BY 4.0 (verified on the Zenodo record)
# Reference: Wang, Aoxuan (2026). Daily reciprocal associations between
#   problematic smartphone use and meaning in life: A 14-day diary study.
#
# 232 Chinese university students x up to 14 daily occasions = 2,606
# person-days, one row each (verified: ID x TIME is unique). `TIME` 1..14 is
# the occasion index and becomes `wave`.
#
# SHIPPED: `PMPU1..PMPU4`, problematic smartphone use, 1-6.
#
# NOT SHIPPED -- `SMYY1`, `SMYY2`. Two daily meaning-in-life items. The
# register BLOCKS the Meaning in Life Questionnaire, and that row covers
# translations (Ben, irw#2401). This file carries NO variable labels and NO
# value labels for any item, so there is no way to tell a two-item MLQ-Presence
# extract from a study-authored pair -- and a two-item table was marginal
# anyway. Dropped rather than guessed. If the paper names the source, this is
# a cheap table to add later.
#
# DERIVED COLUMNS, PROVEN NOT ASSUMED. `MIL` and `PSU` look like additional
# single items on 1-7 and 1-6, which is how the triage counted them. They are
# block means: `MIL == mean(SMYY1, SMYY2)` and `PSU == mean(PMPU1..PMPU4)`,
# both on 100% of rows. `MIL_mean`/`PSU_mean` are the person-level means of
# those, and `ZMIL`/`ZPSU` their z-scores. All dropped.
#
# ID. `ID_ORI` is a structured study code (site + enrolment month + serial,
# e.g. "102052024001") and `ID` its numeric truncation; both have exactly 232
# distinct values. It is a study-internal participant serial, not a platform
# account and not PII -- but nothing is gained by carrying it, so `id` is a
# dense 1..232 index assigned on first appearance. No raw code is kept.
#
# Item text: NOT shipped. Both label levels were checked and BOTH are empty
# for every item -- the file carries exactly two variable labels in total
# ("Zscore(MIL)", "Zscore(PSU)") and no value labels at all. The item codes
# are positional. Where the text is: the published paper's instrument
# section, not this deposit.

import os

import numpy as np
import pandas as pd
import pyreadstat

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "automated_finding", "runs", "hr5", "raw",
                   "zenodo_20826719__data.sav")

PMPU = [f"PMPU{i}" for i in range(1, 5)]
SMYY = ["SMYY1", "SMYY2"]
PMPU_SCALE = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0}


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    print(f"raw: {df.shape}")

    assert df.groupby(["ID", "TIME"]).size().max() == 1, "ID x TIME not unique"
    assert set(df["TIME"].dropna().unique()) <= set(range(1, 15)), "TIME outside 1-14"

    # Prove the two composite columns before dropping them.
    assert np.isclose(df["MIL"], df[SMYY].mean(axis=1)).all(), \
        "MIL is not mean(SMYY1,SMYY2)"
    assert np.isclose(df["PSU"], df[PMPU].mean(axis=1)).all(), \
        "PSU is not mean(PMPU1..4)"
    print("MIL and PSU are block means on 100% of rows -> dropped as derived")

    labs = meta.column_names_to_labels or {}
    vlabs = meta.variable_value_labels or {}
    assert not any(labs.get(c) for c in PMPU), "items now carry labels"
    assert not any(vlabs.get(c) for c in PMPU), "items now carry value labels"
    print("both label levels empty for every item -> no item text to ship")
    print(f"NOT shipping {SMYY}: 2 daily meaning-in-life items with no label "
          f"of either kind, and the register blocks the MLQ in every language")

    # Dense person index in order of first appearance; no raw code kept.
    order = df["ID"].drop_duplicates().tolist()
    idmap = {v: i + 1 for i, v in enumerate(order)}
    df["person"] = df["ID"].map(idmap)

    accounted = set(["ID", "ID_ORI", "person", "TIME", "gender", "age",
                     "MIL", "PSU", "MIL_mean", "PSU_mean", "ZMIL", "ZPSU"]) \
        | set(PMPU) | set(SMYY)
    skipped = {}
    for c in df.columns:
        if c in ("person", "TIME", "gender", "age") or c in PMPU:
            continue
        if c in ("MIL", "PSU"):
            skipped[c] = "block mean, proved above"
        elif c in ("MIL_mean", "PSU_mean"):
            skipped[c] = "person-level mean of a block mean"
        elif c in ("ZMIL", "ZPSU"):
            skipped[c] = "z-score of a block mean"
        elif c in ("ID", "ID_ORI"):
            skipped[c] = "study participant serial, replaced by a dense index"
        elif c in SMYY:
            skipped[c] = "possible MLQ extract, unlabelled; see header"
        else:
            skipped[c] = "not an item or covariate"
    for c, why in sorted(skipped.items()):
        print(f"  skip {c:10} {why}")
    assert set(df.columns) <= accounted, \
        f"unaccounted: {set(df.columns) - accounted}"

    long = (df[["person", "TIME", "gender", "age"] + PMPU]
            .melt(id_vars=["person", "TIME", "gender", "age"],
                  var_name="item", value_name="resp")
            .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(float)
    bad = set(long["resp"].unique()) - PMPU_SCALE
    assert not bad, f"{sorted(bad)} outside the observed 1-6 scale"

    long = long.rename(columns={"person": "id", "TIME": "wave",
                                "gender": "cov_gender", "age": "cov_age"})
    assert long["item"].nunique() == 4, "PMPU should have 4 items"
    assert long["id"].nunique() >= 100, f"N={long['id'].nunique()}"
    long = long[["id", "item", "resp", "wave", "cov_gender", "cov_age"]]

    name = "wang_2026_pmpu"
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} waves={long['wave'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
