#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0329103
# DOI: 10.1371/journal.pone.0329103
# Paper: Hu S, Jabor MK, Fang H, et al. (2025). Big five personality traits and
#   employability: The mediating role of internship attitudes among Chinese
#   vocational students. PLOS ONE 20(8): e0329103.
# Data: S1 File (journal.pone.0329103.s001, "Main Dataset"), 381 accounting
#   students at vocational colleges in Sichuan and Chongqing, China.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 4, BATCH_LOG.md).
#
# THREE output tables, all 1-5 as deposited:
#   hu_2025_big5                 20 items, four per trait: A1-4 agreeableness,
#     C1-4 conscientiousness, Ext1-4 extraversion, O1-4 openness, ES1-4
#     emotional stability (each trait column in the deposit is the raw mean
#     of its four items).
#   hu_2025_internship_attitude  IA1..IA24
#   hu_2025_employability        29 items in five dimensions: SS1-8 soft skills,
#     GBR1-6 general business requirements, AA1-6 audit and assurance, CK1-4
#     conceptual knowledge, STA1-5 special topics in accounting.
# RESPONSE DIRECTION IS NOT ESTABLISHED. The paper says both "1 for 'strongly
#   agree' to 5 for 'strongly disagree'" (its pilot) and "1 indicates
#   'strongly disagree' and 5 indicates 'strongly agree'" (its results), and
#   in the same sentence that every item mean is above the midpoint of 3. In
#   the deposit every one of the 73 item means is BELOW 3 (2.15-2.82), which
#   fits only the first reading (1 = strongly agree). Shipped as deposited;
#   the descriptions say so.
# Covariate: gender (1 male / 2 female: 183/198 reproduces the paper's 48.03%
#   male / 51.97% female).
# Dropped: 序号 (row number), Age, Grade, School Name, Professional Name,
#   Student origin, Duration of internship (bare codes; the categories are in
#   Table 1, an image), and the 13 derived trait/dimension/total columns.
# `id` is the row index.
#
# Item text: NOT SHIPPED. Column codes only (no labels at any level); the
#   questionnaire was translated into Chinese and neither language's wording
#   is in the article or SI.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("HU_RAW", "journal.pone.0329103.s001.xlsx")
BLOCKS = {
    "big5": [("A", 4), ("C", 4), ("Ext", 4), ("O", 4), ("ES", 4)],
    "internship_attitude": [("IA", 24)],
    "employability": [("SS", 8), ("GBR", 6), ("AA", 6), ("CK", 4), ("STA", 5)],
}


def convert():
    df = pd.read_excel(RAW)
    assert df.shape == (381, 94), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    assert df["Gender"].value_counts().to_dict() == {2: 198, 1: 183}
    df["id"] = range(1, len(df) + 1)
    df["cov_gender"] = df["Gender"].map({1: "male", 2: "female"})
    used = {"Gender"}
    total, all_items = 0, []
    for block, parts in BLOCKS.items():
        items = [f"{p}{i}" for p, k in parts for i in range(1, k + 1)]
        all_items += items
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
        name = f"hu_2025_{block}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert (df[all_items].mean() < 3).all()  # the direction evidence cited above
    dropped = [c for c in df.columns if c not in used and c not in ("id", "cov_gender")]
    assert len(dropped) == 7 + 13, dropped
    assert not any(re.fullmatch(r"[A-Za-z]+\d+", str(c)) for c in dropped), dropped
    print(f"total responses {total}; dropped: {dropped}")


if __name__ == "__main__":
    convert()
