#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0272699
# DOI: 10.1371/journal.pone.0272699
# Paper: Belita E, Fisher K, Yost J, Squires JE, Ganann R, Dobbins M (2022).
#   Validity, reliability, and acceptability of the Evidence-Informed
#   Decision-Making (EIDM) competence measure. PLOS ONE 17(8): e0272699.
# Data: Borealis (Scholars Portal Dataverse) 10.5683/SP3/SE3YUP, "EIDM
#   Competence Measure", CC0 1.0 (verified on the dataset record itself).
#   File "EIDM Competence Measure.tab", downloaded as format=original (the
#   CSV), plus the "Study Coding Dictionary" PDF that gives every code. 201
#   public health nurses, Ontario, Canada, November 2019 - March 2020.
# License: CC0 1.0 (deposit; the article is CC BY 4.0).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 5, BATCH_LOG.md).
#
# TWO output tables. Anchors are the coding dictionary's:
#   belita_2022_eidm_competence  the EIDM Competence Measure itself, 40
#     items in four attributes, all 1-7: K1-K11 knowledge (1 poor .. 7
#     excellent), S1-S10 skills (1 beginner .. 7 expert), A1-A7
#     attitudes/beliefs (1 strongly disagree .. 7 strongly agree), B1-B12
#     behaviours (1 not competent .. 7 highly competent). RAW answers: the
#     item sums equal the deposit's totals for K, S and B, and for A once A7
#     is reverse-scored -- so A7 is stored as answered and reversed only in
#     the deposit's totalAttitude.
#   belita_2022_eidm_org_factors  organizational factors indicating
#     commitment to EIDM, OrgFactorsSQ001..SQ012, 1 none at all, 2 a little,
#     3 somewhat, 4 moderately, 5 very much (sums equal totalOrgFactors).
#     S1 File cites these items to the OCRSIEP scale (Fineout-Overholt &
#     Melnyk, ARCC llc Publishing, 2006), "EBP" reworded as "EIDM".
# Composites totalOrgFactors, totalKnowledge, totalskills, totalAttitude,
#   totalBehaviours not shipped.
# Covariates (coding dictionary): years as an RN, highest degree, completed
#   EBP/EIDM training (yes/no), involved in EIDM activities (yes/no).
# `id` is the row index.
#
# Item text: NOT SHIPPED. S1 File (journal.pone.0272699.s001, CC BY 4.0 with
#   the article) is the English participant survey and prints every stem in
#   order, but numbered within each block (1., 2., ...) rather than with the
#   deposit's codes, so the tie would be positional and needs its own
#   verification; the organizational-factor items are a commercial scale's
#   (OCRSIEP). Not attempted in this response-data batch.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("BELITA_RAW", "EIDM Competence Measure.csv")
COMP = ([f"K{i}" for i in range(1, 12)] + [f"S{i}" for i in range(1, 11)] + [f"A{i}" for i in range(1, 8)]
        + [f"B{i}" for i in range(1, 13)])
ORG = [f"OrgFactorsSQ{i:03d}" for i in range(1, 13)]
TOTALS = {"totalOrgFactors", "totalKnowledge", "totalskills", "totalAttitude", "totalBehaviours"}
DEGREE = {1: "diploma", 2: "bachelor's degree", 3: "master's degree", 4: "doctoral degree"}
YESNO = {1: "yes", 2: "no"}


def convert():
    df = pd.read_csv(RAW, encoding="latin1")
    df.columns = [c.replace(" ", "").strip() for c in df.columns]
    assert df.shape == (201, 61), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    a = [f"A{i}" for i in range(1, 8)]
    scored = df[a[:6]].sum(axis=1, min_count=6) + (8 - df["A7"])
    assert (scored - df["totalAttitude"]).dropna().abs().max() == 0 and scored.notna().sum() > 190
    df["id"] = range(1, len(df) + 1)
    df["cov_years_rn"] = df["YearsRN"]
    df["cov_degree"] = df["Education.Highestearneddegree"].map(DEGREE)
    df["cov_eidm_training"] = df["EIDMTraining"].map(YESNO)
    df["cov_eidm_activity"] = df["EIDMActivity"].map(YESNO)
    covs = ["cov_years_rn", "cov_degree", "cov_eidm_training", "cov_eidm_activity"]
    names = []
    for name, items, ok in [("belita_2022_eidm_competence", COMP, range(1, 8)),
                            ("belita_2022_eidm_org_factors", ORG, range(1, 6))]:
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        assert set(long["resp"]) <= set(ok)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(ok) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert len(set(names)) == len(names)
    used = set(COMP) | set(ORG) | TOTALS | {"YearsRN", "Education.Highestearneddegree", "EIDMTraining", "EIDMActivity"}
    left = set(df.columns) - used - {"id"} - set(covs)
    assert not left, left


if __name__ == "__main__":
    convert()
