#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0228859
# DOI: 10.1371/journal.pone.0228859
# Paper: Weeldenburg G, Borghouts LB, Slingerland M, Vos S (2020). Similar but
#   different: Profiling secondary school students based on their perceived
#   motivational climate and psychological need-based experiences in physical
#   education. PLoS ONE 15(2): e0228859.
# Data: PLOS Supporting Information S1 File (journal.pone.0228859.s001,
#   "Dataset profiling secondary school students"), 2,562 secondary school
#   students aged 12-18 in 24 schools, the Netherlands. No missing cells.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 2.
#
# FOUR output tables, one per instrument, item codes the deposit's own; every
# item on the paper's 5-point scale, 1 "not at all true for me" to 5 "very
# true for me":
#   weeldenburg_2020_bpnsfs  Basic Psychological Need Satisfaction and
#     Frustration Scale, shortened to 3 items per construct (18 items):
#     AUTs/AUTf, COMs/COMf, RELs/RELf (s = satisfaction, f = frustration)
#   weeldenburg_2020_mcsys   Motivational Climate Scale for Youth Sports,
#     adapted to PE: MAS1-6 (mastery climate), PER1-6 (performance climate)
#   weeldenburg_2020_agpeq   2x2 Achievement Goal in PE Questionnaire, 12
#     items: MAp/MAv/PAp/PAv 1-3 (mastery/performance, approach/avoidance)
#   weeldenburg_2020_brpeq   Behavioural Regulations in PE Questionnaire,
#     shortened to 12 items: IM1-2 (intrinsic), IDR1-2 (identified), INR1-2
#     (introjected), EXR1-2 (external), AM1-4 (amotivation)
# `cluster_id` is the school (1-24).
# Covariates: sex (1 = boy, 2 = girl: 1,138 of 2,562 are coded 1 and the paper
#   reports 44% boys), age.
# Dropped: LTSP (leisure-time sport participation, codes 1-3 with no stated
#   labels) and "Valuation PE" (a single 1-10 grade for PE class).
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. Header codes only; the article quotes one example
#   item per construct, not the full shortened item sets.

import io
import os
import re
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0228859.s001"
RAW = os.environ.get("WEELDENBURG_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SCALES = {"bpnsfs": r"(AUT|COM|REL)[sf]\d", "mcsys": r"(MAS|PER)\d", "agpeq": r"(MA|PA)[pv]\d",
          "brpeq": r"(IM|IDR|INR|EXR|AM)\d"}
N_ITEMS = {"bpnsfs": 18, "mcsys": 12, "agpeq": 12, "brpeq": 12}


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=120)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_excel(src, sheet_name=0)


def convert():
    df = load()
    assert df.shape == (2562, 59), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and not txt
    items = {k: [c for c in df.columns if re.fullmatch(p, c)] for k, p in SCALES.items()}
    assert {k: len(v) for k, v in items.items()} == N_ITEMS, {k: len(v) for k, v in items.items()}
    used = {"Sex", "Age", "School", "LTSP", "Valuation PE"} | {c for v in items.values() for c in v}
    assert used == set(df.columns), set(df.columns) ^ used
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df["cluster_id"] = df["School"].astype(int)
    df["cov_sex"] = df["Sex"].map({1: "boy", 2: "girl"})
    assert df["cov_sex"].notna().all()
    df["cov_age"] = df["Age"]
    covs = ["cov_sex", "cov_age"]
    for key, cols in items.items():
        long = df[["id", "cluster_id"] + covs + cols].melt(id_vars=["id", "cluster_id"] + covs, var_name="item",
                                                          value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {1, 2, 3, 4, 5}
        long = long[["id", "item", "resp", "cluster_id"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {key} {c.name}: {c.detail[:150]}")
        out = f"weeldenburg_2020_{key}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
