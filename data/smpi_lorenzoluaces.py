#!/usr/bin/env python3
"""Reshape the SMPI dataset into IRW long-format tables.

Source
    Lorenzo-Luaces, L., Rutter, L. A., & Scalco, M. D. (2020). Carving depression
    at its joints? Psychometric properties of the Sydney Melancholia Prototype
    Index. Psychiatry Research, 293, 113410.

Produces four tables, one per instrument, each with columns:
    id, item, resp, cov_gender, cov_age, cov_race, cov_ethnic

    smpi   SMPIa_1-12  -> A1-A12,  SMPIb_1-12 -> B1-B12   resp 1-5
    phq9   PHQ_1-9     -> unchanged                        resp 0-3
    gad7   gad1-7      -> GAD_1-GAD_7                      resp 0-3
    shaps  SHAPS_1-14  -> unchanged                        resp 0-4

Requires pandas and numpy.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "SMPI data.csv")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else ".")
PREFIX = "smpi_lorenzoluaces_2020"

# source column -> IRW item label, one mapping per output table
SPECS = {
    "smpi": {f"SMPIa_{i}": f"A{i}" for i in range(1, 13)}
    | {f"SMPIb_{i}": f"B{i}" for i in range(1, 13)},
    "phq9": {f"PHQ_{i}": f"PHQ_{i}" for i in range(1, 10)},
    "gad7": {f"gad{i}": f"GAD_{i}" for i in range(1, 8)},
    "shaps": {f"SHAPS_{i}": f"SHAPS_{i}" for i in range(1, 15)},
}

# person-invariant covariates: source column -> IRW column
COVS = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Race": "cov_race",
    "Ethnic": "cov_ethnic",
}


def load(path):
    """Read the source wide file, treating whitespace-only cells as missing."""
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
    df = df.replace(r"^\s*$", np.nan, regex=True)
    df.insert(0, "id", np.arange(1, len(df) + 1))
    return df


def to_long(df, mapping):
    """Melt one instrument's columns to id/item/resp and attach covariates."""
    cols = list(mapping)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"source columns not found: {missing}")

    long = (
        df[["id"] + cols]
        .melt(id_vars="id", var_name="item", value_name="resp")
        .dropna(subset=["resp"])
    )
    # ordered categorical so items sort A1..A12, B1..B12 rather than
    # alphabetically (which would give A1, A10, A11, A12, A2, ...)
    long["item"] = pd.Categorical(
        long["item"].map(mapping), categories=list(mapping.values()), ordered=True
    )
    long["resp"] = pd.to_numeric(long["resp"])

    covs = df[["id"] + list(COVS)].rename(columns=COVS)
    for c in COVS.values():
        covs[c] = pd.to_numeric(covs[c])
    long = long.merge(covs, on="id", how="left", validate="many_to_one")

    return long.sort_values(["id", "item"]).reset_index(drop=True)


def checks(df):
    """Sanity checks against figures reported in the paper."""
    num = df.drop(columns=["id"]).apply(pd.to_numeric)
    smpi_cols = [c for c in df.columns if c.startswith("SMPI")]
    gad = [f"gad{i}" for i in range(1, 8)]
    phq = [f"PHQ_{i}" for i in range(1, 10)]
    shaps = [f"SHAPS_{i}" for i in range(1, 15)]
    complete_phq = ~num[phq].isna().any(axis=1)

    print("\nchecks")
    print(f"  source rows: {len(df)} (paper: 487 administered the SMPI)")
    print(
        f"  complete SMPI cases: {int((~num[smpi_cols].isna().any(axis=1)).sum())}"
        " (paper: 476)"
    )
    print(
        "  gad items sum == GAD column:",
        bool((num[gad].sum(axis=1) == num["GAD"]).all()),
    )
    print(
        "  phq items sum == PHQ column (complete rows):",
        bool((num[phq].sum(axis=1) == num["PHQ"])[complete_phq].all()),
    )
    print(
        "  shaps items sum == SHAPS column:",
        bool((num[shaps].sum(axis=1) == num["SHAPS"]).all()),
    )


def main():
    raw = load(SRC)
    OUT.mkdir(parents=True, exist_ok=True)

    for name, mapping in SPECS.items():
        tbl = to_long(raw, mapping)
        path = OUT / f"{PREFIX}_{name}.csv"
        tbl.to_csv(path, index=False)
        print(
            f"{name:6s} rows={len(tbl):6d} ids={tbl.id.nunique():4d} "
            f"items={tbl.item.nunique():3d} "
            f"resp={sorted(tbl.resp.unique())} -> {path}"
        )

    checks(raw)


if __name__ == "__main__":
    main()