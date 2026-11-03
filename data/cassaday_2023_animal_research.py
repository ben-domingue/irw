#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0290232
# DOI: 10.1371/journal.pone.0290232
# Paper: Cassaday HJ, Cavenagh L, Aluthgamage H, et al. (2023). Attitudes to
#   the use of animals in biomedical research: Effects of stigma and selected
#   research project summaries. PLOS ONE 18(8): e0290232.
# Data: S2 Appendix (journal.pone.0290232.s002, "All data", .sav), 598 UK
#   adults (online). Also deposited at the University of Nottingham Research
#   Data Repository (10.17639/nott.7305).
# License: CC BY 4.0 (the article; the data is its Supporting Information).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 3, BATCH_LOG.md).
#
# Design: participants were randomised to read no summary (N=215), a lay
# summary (182) or a technical summary (201) of a research project before
# answering. The randomised arm (SUMMARY_TYPE) is NOT shipped: it is a
# three-arm design, the same open multi-arm `treat` question as
# lin_2026_advertising_literacy and hazell_2022. Every response below was
# given after the manipulation.
#
# Three output tables:
#   cassaday_2023_aas  AAS1..AAS10, Herzog's Animal Attitude Scale, 10-item
#                      brief form. 1 strongly disagree .. 5 strongly agree, in
#                      SCORED direction: the paper reverse-scores items 2, 3,
#                      4, 7, 8, and the deposit's AAS_TOTAL equals the plain
#                      sum of the stored items, so they are already reversed.
#   cassaday_2023_apq  Animal Purpose Questionnaire, adapted: agreement with
#                      using each of 5 species (PIG, RAT, MICE, FISH, MONK) in
#                      each of 4 kinds of research (ADD addiction, SZ
#                      schizophrenia, OBS obesity, CVD cardiovascular
#                      disease); 20 items coded <purpose>_<species>.
#                      1 strongly agree .. 5 strongly disagree (paper).
#   cassaday_2023_bam  Belief in Animal Mind, 4 questions x 5 species = 20
#                      items, BAM_<question>_<species>. 1-7 in SCORED
#                      direction (higher = greater belief in animal mind):
#                      the paper's raw coding was 1 strongly agree .. 7
#                      strongly disagree with questions 2 and 3 reversed, and
#                      the deposit's BAM_TOTAL equals the plain sum.
# Covariates: gender (value labels), age, relevant degree (yes/no).
# Dropped: SUMMARY_TYPE (see above); the composites AAS_TOTAL, APQ_TOTAL,
#   APQ_AV, BAM_TOTAL, EQ_TOTAL (the Empathy Quotient is deposited as a total
#   only), ADDTOT, SZTOT, OBSTOT, CVDTOT; GENDEREXC and EATINGCOMB (recodes of
#   GENDERALL/EATINGALL); EATINGALL (codes 5-6 unlabelled); and six follow-up
#   questions answered by ~55% (LESS_JUST, *_INDCON, DIS_FAM) whose wording and
#   scale the paper does not give.
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. No variable labels and no value labels on any item
#   (both levels checked); the item wording is not in the article or its SI.
#   The AAS (Herzog et al.) and BAM (Hills 1995) are third-party instruments.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("CASSADAY_RAW", "journal.pone.0290232.s002.sav")
SPECIES = ["PIG", "RAT", "MICE", "FISH", "MONK"]


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
    df, meta = pyreadstat.read_sav(RAW)
    assert df.shape == (598, 72)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    vl = meta.variable_value_labels
    aas = [f"AAS{i}" for i in range(1, 11)]
    apq = [f"{p}_{s}" for p in ["ADD", "SZ", "OBS", "CVD"] for s in SPECIES]
    bam = [f"BAM_{q}_{s}" for q in range(1, 5) for s in SPECIES]
    # scored direction, verified against the deposit's own totals
    assert (df[aas].sum(axis=1) - df["AAS_TOTAL"]).abs().max() == 0
    assert (df[apq].sum(axis=1) - df["APQ_TOTAL"]).abs().max() == 0
    ok = df["BAM_TOTAL"].notna()
    assert (df.loc[ok, bam].sum(axis=1) - df.loc[ok, "BAM_TOTAL"]).abs().max() == 0
    df["id"] = range(1, len(df) + 1)
    df["cov_gender"] = df["GENDERALL"].map(vl["GENDERALL"])
    df["cov_age"] = df["AGE"]
    df["cov_relevant_degree"] = df["DEGREE"].map(vl["DEGREE"])
    cov_cols = ["cov_gender", "cov_age", "cov_relevant_degree"]
    os.makedirs(OUT_DIR, exist_ok=True)
    names = [emit("cassaday_2023_aas", df, aas, cov_cols, [1, 2, 3, 4, 5]),
             emit("cassaday_2023_apq", df, apq, cov_cols, [1, 2, 3, 4, 5]),
             emit("cassaday_2023_bam", df, bam, cov_cols, [1, 2, 3, 4, 5, 6, 7])]
    assert len(set(names)) == len(names)
    dropped = ["SUMMARY_TYPE", "AAS_TOTAL", "APQ_TOTAL", "APQ_AV", "BAM_TOTAL", "EQ_TOTAL", "ADDTOT", "SZTOT",
               "OBSTOT", "CVDTOT", "GENDEREXC", "EATINGCOMB", "EATINGALL", "LESS_JUST", "ADD_INDCON", "SZ_INDCON",
               "OBS_INDCON", "CVD_INDCON", "DIS_FAM"]
    assert set(meta.column_names) == set(aas) | set(apq) | set(bam) | {"GENDERALL", "AGE", "DEGREE"} | set(dropped)
    print("dropped:", dropped)


if __name__ == "__main__":
    convert()
