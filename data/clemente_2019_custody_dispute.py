#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0213662
# DOI: 10.1371/journal.pone.0213662
# Paper: Clemente, M., Espinosa, P., & Padilla, D. (2019). Moral
#   disengagement and willingness to behave unethically against ex-partner in
#   a child custody dispute. PLOS ONE 14(3): e0213662.
# Data: figshare 10.6084/m9.figshare.7597700 ("Moral disengagement and child
#   custody dispute.sav"), reached from the article's Data Availability
#   statement. 1,097 Spanish adults, all parents of underage children who had
#   been through a couple break-up, surveyed online (incidental sample).
# License: CC BY 4.0 -- verified on the figshare DEPOSIT, and the same as the
#   article's.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30, worked from
# leads/plos_leads_2026-10-30.csv on 2026-10-31 (BATCH_LOG.md).
#
# FOUR output tables, the blocks whose item count and response range match
# what the paper documents:
#   clemente_2019_pmd          PMD1..24, 1-7: Moore et al.'s Propensity to
#                              Morally Disengage scale, "24 items in a 7-point
#                              Likert scale".
#   clemente_2019_npi          N1..40, 1-6: the Spanish NPI, "40 items on a
#                              6-point Likert scale".
#   clemente_2019_lying_court  Lying1..11, 1-4: the authors' custody-dispute
#                              vignette, eleven false statements the
#                              respondent rates their willingness to make in
#                              court (variable labels "Vignette 1-1".."1-11").
#   clemente_2019_retaliation  Retaliation1..7, 1-4: the same vignette's seven
#                              retaliatory acts against the ex-partner
#                              (labels "Vignette 2-1".."2-7").
# The deposit's own Lying and Retaliation means reproduce from these blocks
# (asserted), which is what ties the two vignette blocks to the paper's two
# outcomes.
#
# NOT SHIPPED, because the deposit contradicts the paper: M1..M33 (33 columns,
# 1-5) where the paper's Mach-IV is "20 items on a 7-point Likert format";
# and P1..P26 (26 columns, 1-6) where the paper's Levenson scale (LPSP) has
# 26 items on "a 5-point Likert-type" scale. The item counts or the ranges
# fail to match on both, and the .sav carries no labels on either block (both
# label levels read: no variable labels, no value labels on any M, N, P or
# PMD column), so neither can be identified from the file. Recorded here so
# the next reader does not re-derive it. The deposit's derived subscale means
# (Mach_*, Narcissism_*, Psychopathy_*, PMD*) are not shipped either.
#
# `id` is the row index (no respondent id in the file).
#
# Covariates: sex (1/2, unlabelled in the file; the paper says the sample is
# "evenly divided", the file is 511/586 -- shipped as the deposit's code,
# cov_sex_code), age
# band 1-5 (cov_age_band), number of underage children 1-5
# (cov_n_children_band).
#
# Item text: NOT SHIPPED. No stems anywhere in the deposit (variable labels
# are "Vignette 1-1" style or absent). PMD is Moore et al. 2012's instrument
# and the NPI-40 is Raskin & Terry's; register rows added, hold. The two
# vignette blocks are the authors' own and would ship under CC BY if their
# wording were in hand -- it is in the article's Methods only as a summary.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("CLEMENTE_RAW", "Moral disengagement and child custody dispute.sav")
N_ROWS = 1097
BLOCKS = {
    "clemente_2019_pmd": ([f"PMD{i}" for i in range(1, 25)], 1, 7),
    "clemente_2019_npi": ([f"N{i}" for i in range(1, 41)], 1, 6),
    "clemente_2019_lying_court": ([f"Lying{i}" for i in range(1, 12)], 1, 4),
    "clemente_2019_retaliation": ([f"Retaliation{i}" for i in range(1, 8)], 1, 4),
}


def convert():
    df, meta = pyreadstat.read_sav(RAW, apply_value_formats=False)
    labels, vl = meta.column_names_to_labels, meta.variable_value_labels
    assert len(df) == N_ROWS, len(df)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert not txt
    # the two blocks the paper contradicts, recorded rather than guessed
    m_cols = [c for c in df.columns if c.startswith("M") and c[1:].isdigit()]
    p_cols = [c for c in df.columns if c.startswith("P") and c[1:].isdigit()]
    print(f"M block: {len(m_cols)} cols, values {sorted(set(df[m_cols].stack().unique()))} (paper: Mach-IV 20 items, 1-7) -> not shipped")
    print(f"P block: {len(p_cols)} cols, values {sorted(set(df[p_cols].stack().unique()))} (paper: LPSP 26 items, 1-5) -> not shipped")
    assert len(m_cols) == 33 and len(p_cols) == 26
    # the deposit's vignette means reproduce from the item blocks
    assert (df[[f"Lying{i}" for i in range(1, 12)]].mean(axis=1) - df["Lying"]).abs().max() < 1e-6
    assert (df[[f"Retaliation{i}" for i in range(1, 8)]].mean(axis=1) - df["Retatiation"]).abs().max() < 1e-6
    assert labels["Lying1"] == "Vignette 1-1" and labels["Retaliation1"] == "Vignette 2-1"

    df["id"] = range(1, N_ROWS + 1)
    cov = pd.DataFrame({
        "id": df["id"],
        "cov_sex_code": df["Sex"].astype(int),
        "cov_age_band": df["AgeR"].astype(int),
        "cov_n_children_band": df["Child"].astype(int),
    })
    assert abs((df["Sex"] == 1).mean() - 0.5) < 0.05   # 511 vs 586; the paper rounds to 50/50
    cov_cols = ["cov_sex_code", "cov_age_band", "cov_n_children_band"]

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, (cols, lo, hi) in BLOCKS.items():
        for c in cols:
            assert not vl.get(c), c
        wide = df[["id"] + cols]
        assert int(wide[cols].isna().sum().sum()) == 0
        long = wide.melt(id_vars=["id"], value_vars=cols, var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) == set(range(lo, hi + 1)), (name, sorted(long["resp"].unique()))
        long = long.merge(cov, on="id", how="left")[["id", "item", "resp"] + cov_cols]
        assert long["id"].nunique() == N_ROWS and long["item"].nunique() == len(cols)
        checks = run_qc(long, permitted_values={c: list(range(lo, hi + 1)) for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} resp={lo}-{hi}")
    print(f"TOTAL responses: {total}")


if __name__ == "__main__":
    convert()
