#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/AKVGXJ
# DOI (data): 10.7910/DVN/AKVGXJ
# Data: Du, M. (2026). raw data (paper: Technology acceptance and professional
#   identity: multi-path associations with K-12 teachers' engagement with AI).
#   Harvard Dataverse. File "The primary dataset for analysis(1).sav"
#   (Dataverse original format), 714 K-12 teachers.
#   No article is linked from the deposit (checked 2026-11-07).
# License: CC0 1.0, verified on the deposit (Dataverse API, latestVersion.license).
#
# Found by the repos sweep of 2026-11-07 (Step 2b worth_retrying).
#
# The file holds 37 integer items, all 1-5, no missing values, and nothing
# else: no id, no covariates, no variable or value labels. Split by the item
# prefixes into FOUR output tables:
#   du_2026_utaut            PE1-4, EE1-4, FC1-4, SI1-4: the four UTAUT
#                            constructs (performance expectancy, effort
#                            expectancy, facilitating conditions, social
#                            influence), named in the deposit title as
#                            "technology acceptance".
#   du_2026_teacher_identity TPI1-8: teacher professional identity.
#   du_2026_ai_use_intention AIUI1-4: AI use intention.
#   du_2026_aiab             AIAB1-9: AI engagement items; the deposit never
#                            expands "AIAB", so the name is kept as given.
# The construct readings of the prefixes follow the deposit title; the
# deposit itself documents none of them. 1-5 with no extra category is read
# as a plain five-point scale; the anchors are not documented.
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. Not in the deposit, and no article is linked.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("DU_RAW", "The primary dataset for analysis(1).sav")
BLOCKS = {"utaut": [f"{p}{i}" for p in ("PE", "EE", "FC", "SI") for i in range(1, 5)],
          "teacher_identity": [f"TPI{i}" for i in range(1, 9)],
          "ai_use_intention": [f"AIUI{i}" for i in range(1, 5)],
          "aiab": [f"AIAB{i}" for i in range(1, 10)]}


def convert():
    df, _ = pyreadstat.read_sav(RAW)
    assert df.shape == (714, 37), df.shape
    assert sum(BLOCKS.values(), []) == list(df.columns)
    df["id"] = range(1, len(df) + 1)
    for block, items in BLOCKS.items():
        long = df[["id"] + items].melt(id_vars=["id"], var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {1, 2, 3, 4, 5}, set(long["resp"])
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"du_2026_{block}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
