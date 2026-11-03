#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0294244
# DOI: 10.1371/journal.pone.0294244
# Paper: Xiong S, Zhang T (2024). Enhancing tourist loyalty through
#   location-based service apps: Exploring the roles of digital literacy,
#   perceived ease of use, perceived autonomy, virtual-content congruency, and
#   tourist engagement. PLOS ONE 19(1): e0294244.
# Data: S1 Dataset (journal.pone.0294244.s004), 319 Chinese tourists who used
#   location-based service apps, 2023.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 4, BATCH_LOG.md).
#
# SIX output tables, the paper's six measures, all on a 5-point Likert scale
# (items translated into Chinese), as deposited:
#   xiong_2024_digital_literacy  DL1-7 (Rodriguez-de-Dios, Igartua et al.;
#     includes a negatively worded item, not re-keyed)
#   xiong_2024_peou              PEOU1-4 perceived ease of use (Kim & Lee)
#   xiong_2024_autonomy          PA1-3 perceived autonomy (Lunardo & Ponsignon)
#   xiong_2024_congruency        IEC1-4 information-experience congruency
#     (O'Cass & Grace)
#   xiong_2024_engagement        II1-3 immersed involvement + NS1-4 novelty
#     seeking, the paper's 7-item two-dimension tourist engagement scale
#     (Huang & Choi)
#   xiong_2024_loyalty           TL1-6 tourist loyalty (Loureiro & Gonzalez)
# Covariate: gender (1 male / 2 female: 167/152 reproduces the paper's 52.4% /
#   47.6%).
# Dropped: Age, Income (five codes each; the paper's age bands are reported
#   out of code order and income not at all).
# `id` is the row index.
#
# Item text: NOT SHIPPED. Column codes only (no labels at any level); the
#   Chinese wording is not in the article, and S1 File (.s003) is an image-only
#   PDF.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("XIONG_RAW", "journal.pone.0294244.s004.xlsx")
BLOCKS = {
    "digital_literacy": [("DL", 7)], "peou": [("PEOU", 4)], "autonomy": [("PA", 3)],
    "congruency": [("IEC", 4)], "engagement": [("II", 3), ("NS", 4)], "loyalty": [("TL", 6)],
}


def convert():
    df = pd.read_excel(RAW)
    assert df.shape == (319, 34), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    assert df["Gender"].value_counts().to_dict() == {1: 167, 2: 152}
    df["id"] = range(1, len(df) + 1)
    df["cov_gender"] = df["Gender"].map({1: "male", 2: "female"})
    used = {"Gender", "Age", "Income"}
    total = 0
    for block, parts in BLOCKS.items():
        items = [f"{p}{i}" for p, k in parts for i in range(1, k + 1)]
        used |= set(items)
        long = df[["id", "cov_gender"] + items].melt(id_vars=["id", "cov_gender"], var_name="item", value_name="resp")
        assert long["resp"].notna().all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {1, 2, 3, 4, 5}
        long = long[["id", "item", "resp", "cov_gender"]]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"xiong_2024_{block}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert used | {"id", "cov_gender"} == set(df.columns), set(df.columns) - used
    print(f"total responses {total}; dropped: Age, Income")


if __name__ == "__main__":
    convert()
