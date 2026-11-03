#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0262744
# DOI: 10.1371/journal.pone.0262744
# Paper: Salih MH, Wettergren L, Lindgren H, et al. (2022). Translation and
#   psychometric evaluation of chronic illness anticipated stigma scale
#   (CIASS) among patients in Ethiopia. PLOS ONE 17(1): e0262744.
# Data: S1 Data "Anticipated stigma tool validation main data"
#   (journal.pone.0262744.s002, .xlsx; also on Mendeley Data
#   10.17632/gvrk8njd76.1), 173 adults with a chronic illness at three
#   referral hospitals in Amhara region, Ethiopia, interviewed in Amharic.
# Questionnaire: S1 File (English version).
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 5, BATCH_LOG.md).
#
# THREE output tables, anchors from S1 File:
#   salih_2022_ciass  Chronic Illness Anticipated Stigma Scale, Amharic,
#     Item_1..Item_12 (S1 File items 301-312: friends/family 1-4,
#     work 5-8, healthcare workers 9-12), 1 very unlikely .. 5 very likely.
#   salih_2022_k10    Kessler Psychological Distress Scale, N601..N610
#     (S1 File Part IV, items 401-410), 1 none of the time .. 5 all of the
#     time. The deposit's K10 column is the item mean (correlation 1.0).
#   salih_2022_whoqol_bref  WHOQOL-BREF, QOL1..QOL26 (S1 File Part V, items
#     501-526), each 1-5 on the instrument's own anchor sets (very poor ..
#     very good, very dissatisfied .. very satisfied, not at all ..
#     extremely/completely, never .. always). RAW answers: the three
#     negatively framed items (3, 4, 26) are not reversed in the file.
# Composites QOLBREF, K10, Domain_1-3, "total mean of AS" not shipped.
# Covariate: primary chronic diagnosis (labelled in the cell). Every other
#   deposit column is a numeric code or a medication/media yes-no flag whose
#   1/2 orientation the file does not state; dropped. The questionnaire also
#   asked for a phone number and a town -- neither is in the deposit.
# `id` is the deposit's UniqueKey.
#
# Item text: NOT SHIPPED. English stems for all three instruments are in S1
#   File; the administered Amharic wording is not in the deposit, and K10 and
#   WHOQOL-BREF are third-party instruments (WHOQOL-BREF under WHO terms).

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("SALIH_RAW", "journal.pone.0262744.s002.xlsx")
BLOCKS = {"ciass": [f"Item_{i}" for i in range(1, 13)], "k10": [f"N6{i:02d}" for i in range(1, 11)],
          "whoqol_bref": [f"QOL{i}" for i in range(1, 27)]}
COMPOSITES = {"QOLBREF", "K10", "Domain_1", "Domain_2", "Domain_3", "total mean of AS"}


def convert():
    df = pd.read_excel(RAW)
    assert df.shape == (173, 81), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == ["N201Medicaldx"]
    print("  N201Medicaldx values:", sorted(df["N201Medicaldx"].unique()))
    assert df["UniqueKey"].is_unique
    assert (df[BLOCKS["k10"]].mean(axis=1) - df["K10"]).abs().max() < 1e-9
    df["id"] = df["UniqueKey"]
    df["cov_diagnosis"] = df["N201Medicaldx"].str.replace(r"^\d+\s*-\s*", "", regex=True).str.strip()
    covs = ["cov_diagnosis"]
    used = COMPOSITES | {"UniqueKey", "N201Medicaldx"}
    used |= {c for c in df.columns if c.startswith(("N1", "N2"))}
    names, total = [], 0
    for block, items in BLOCKS.items():
        used |= set(items)
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        assert set(long["resp"]) <= {1, 2, 3, 4, 5}
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"salih_2022_{block}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert len(set(names)) == len(names)
    left = set(df.columns) - used - {"id"} - set(covs)
    assert not left, left
    print(f"total responses {total}")


if __name__ == "__main__":
    convert()
