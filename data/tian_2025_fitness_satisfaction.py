#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0317551
# DOI: 10.1371/journal.pone.0317551
# Paper: Tian, F., Zhou, J., & Liu, F. (2025). Construction of the national
#   fitness public service satisfaction model in China based on American
#   Customer Satisfaction Index. PLOS ONE 20(1): e0317551.
# Data: journal.pone.0317551.s001 (S1 Dataset, .xls, sheet "questionnaire
#   data"), 1,133 Guangzhou residents, December 2020 (438 online, 695 paper).
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# SIX output tables, one per latent variable of the paper's ACSI-based
# measurement model (41 indicators). The column prefixes match the model
# one-for-one:
#   tian_2025_fitness_expectation    PE1-PE3   public expectation, 1-7
#   tian_2025_fitness_quality        PQ1-PQ25  perceived quality, 1-7
#   tian_2025_fitness_value          PV1-PV2   perceived value, 1-7
#   tian_2025_fitness_satisfaction   PS1-PS3   public satisfaction, 1-7
#   tian_2025_fitness_complaint      PC1-PC3   public complaints, 1-7
#   tian_2025_fitness_trust          PT1-PT5   public trust, 1-7
# Paper: expectation and quality on a seven-point scale from "very low" to
# "very high"; the other four on a seven-point scale from "very disapprove"
# to "very approve".
#
# Covariates: NONE. The six demographic columns (Gender, Age group,
# Educational level, Professional, Income, Address) are bare integer codes;
# their categories are given only in Table 2, which is an image, and the
# deposit has no codebook. Shipping guessed labels would be worse than none.
# `id` is the row index (the sheet has no id column).
#
# Item text: NOT SHIPPED. The sheet carries item codes only (no labels at
#   any level -- .xls has none); the Chinese wording is not in the article
#   or its SI (Table 1 lists item sources, not stems).

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("TIAN_RAW", "journal.pone.0317551.s001.xls")
N_ROWS = 1133
DEMOS = ["Gender", "Age group", "Educational level", "Professional", "Income", "Address"]
BLOCKS = {
    "expectation": ("PE", 3),
    "quality": ("PQ", 25),
    "value": ("PV", 2),
    "satisfaction": ("PS", 3),
    "complaint": ("PC", 3),
    "trust": ("PT", 5),
}


def convert():
    df = pd.read_excel(RAW, sheet_name="questionnaire data")
    assert len(df) == N_ROWS, len(df)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 47 and txt == []
    df["id"] = range(1, N_ROWS + 1)
    used = set(DEMOS)
    names = []
    total = 0
    for block, (pfx, k) in BLOCKS.items():
        items = [f"{pfx}{i}" for i in range(1, k + 1)]
        used |= set(items)
        long = df[["id"] + items].melt(id_vars=["id"], var_name="item", value_name="resp")
        assert long["resp"].notna().all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(range(1, 8)), set(long["resp"])
        long = long[["id", "item", "resp"]]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(range(1, 8)) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"tian_2025_fitness_{block}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert len(set(names)) == len(names)
    assert used | {"id"} == set(df.columns), set(df.columns) - used
    print(f"total responses {total}; dropped (no codebook): {DEMOS}")


if __name__ == "__main__":
    convert()
