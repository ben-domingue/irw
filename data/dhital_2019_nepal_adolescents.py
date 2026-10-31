#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0223046
# DOI: 10.1371/journal.pone.0223046
# Paper: Dhital, R., Shibanuma, A., Miyaguchi, M., Kiriya, J., & Jimba, M.
#   (2019). Effect of psycho-social support by teachers on improving mental
#   health and hope of adolescents in an earthquake-affected district in
#   Nepal: A cluster randomized controlled trial. PLOS ONE 14(10): e0223046.
# Data: figshare 10.6084/m9.figshare.9860750 ("Effect of psychosocial support
#   intervetion on adolescent mental health-Nepaldata.sav"), reached from the
#   article's Data Availability statement. 1,272 adolescents in grades 6-8 at
#   15 government secondary schools in Dhading district, Nepal; baseline
#   August 2016 and follow-up February 2017 (6 months).
# License: CC BY 4.0 -- verified on the figshare DEPOSIT (which is what
#   governs an off-site file), and the same as the article's.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30, worked from
# leads/plos_leads_2026-10-30.csv on 2026-10-31 (BATCH_LOG.md).
#
# THREE output tables, each longitudinal (`wave` 1 = baseline, 2 = follow-up)
# with the trial design carried as `treat` (1 = intervention school, 0 =
# control) and `cluster_id` (the school, 1-15, the unit of randomisation):
#   dhital_2019_cpss    PTSD1..17, 0-3: the Child PTSD Symptom Scale, "a
#                       17-item measure ... minimum score 0, maximum 52".
#   dhital_2019_dsrs    DEPRESSION1..18, 0-2: the Depression Self-Rating
#                       Scale, "an 18-item self-report ... scores range from
#                       0 to 36".
#   dhital_2019_chs     HOPE1..6, 1-6: the Children's Hope Scale, six items.
# The .sav has no variable labels on the items (5 of 80 columns are
# labelled, all covariates) and no value labels on them; the identification
# is the column-name prefix plus the paper's instrument list, and the item
# counts and ranges match each instrument exactly.
#
# STRAY OUT-OF-RANGE VALUES ARE DATA-ENTRY ERRORS AND BECOME MISSING: on the
# 0-2 DSRS, single cells of 3 (items 1, 4, 6, 7 -- one to three rows each),
# 9 (items 14, 16, one row each) and 3/4/6 on item 18 (10 rows); on the 1-6
# CHS, two cells of 0 on item 1. Each is isolated to a handful of rows on one
# item against ~2,280 in-range responses, which is the shape the standard's
# "data entry errors at known values" rule names. 23 cells in all; counted
# and printed.
#
# Three rows carry a school dummy that contradicts the arm every other row at
# that school has (two at school 13, one at 15); their cluster_id is NaN.
#
# Not shipped: the deposit's eight DEPRESSIONkreversed columns (the paper's
# reverse-scoring of the positively worded DSRS items -- derived from the
# shipped raw columns, proved exactly 2-x), the three totals, and the
# *reversed copies of followup/schooltype/gender.
#
# `id` is the deposit's studyidno (1,272 distinct; 1,018 appear at both
# waves, 200 at baseline only, 48 at follow-up only, plus 6 whose single row
# is a follow-up). The paper reports 1,220 recruited and 1,070 followed up;
# the file carries 1,272 ids, and ships as deposited.
#
# Covariates: age in years, gender (deposit labels), grade (6-8), family
# size. A few rows carry grade 2-4 (11 rows), kept as deposited.
#
# Item text: NOT SHIPPED. Both label levels are empty for every item column,
# so no administered wording (Nepali) is in the deposit. The three instruments
# are third-party (Foa et al.'s CPSS; Birleson's DSRS; Snyder et al.'s CHS);
# register rows added as holds pending their terms.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("DHITAL_RAW",
                     "Effect of psychosocial support intervetion on adolescent mental health-Nepaldata.sav")
N_ROWS, N_IDS = 2290, 1272

BLOCKS = {
    "dhital_2019_cpss": ([f"PTSD{i}" for i in range(1, 18)], 0, 3),
    "dhital_2019_dsrs": ([f"DEPRESSION{i}" for i in range(1, 19)], 0, 2),
    "dhital_2019_chs": ([f"HOPE{i}" for i in range(1, 7)], 1, 6),
}


def convert():
    df, meta = pyreadstat.read_sav(RAW, apply_value_formats=False)
    vl = meta.variable_value_labels
    assert len(df) == N_ROWS, len(df)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert not txt
    assert vl["status"] == {1.0: "Baseline", 2.0: "Followup"}
    assert vl["schooltype"] == {0.0: "control", 1.0: "Intervention"}
    assert vl["q2gender"] == {1.0: "Male", 2.0: "Female"}

    df["id"] = df["studyidno"].astype(int)
    assert df["id"].nunique() == N_IDS
    assert not df.duplicated(["id", "status"]).any()
    assert (df.groupby("id")["schooltype"].nunique() == 1).all()
    schools = [f"School{i}" for i in range(1, 15)] + ["Schools15"]
    assert (df[schools].sum(axis=1) <= 1).all()
    cluster = (df[schools].values.argmax(axis=1) + 1)
    cluster = pd.Series(cluster, index=df.index).where(df[schools].sum(axis=1) == 1)
    print(f"school dummies: {int(df[schools].sum(axis=1).eq(0).sum())} row(s) with no school -> cluster_id NaN")
    # arm is constant within school, the unit of randomisation -- except for
    # three rows (two at school 13, one at school 15) whose school dummy
    # contradicts the arm every other row at that school carries. Their
    # cluster_id is nulled rather than guessed; printed.
    arm_of_school = df.groupby(cluster)["schooltype"].agg(lambda s: s.mode().iloc[0])
    clash = cluster.notna() & (df["schooltype"] != cluster.map(arm_of_school))
    print(f"school/arm clashes: {int(clash.sum())} row(s) at school(s) {sorted(cluster[clash].unique())} -> cluster_id NaN")
    assert int(clash.sum()) == 3, int(clash.sum())
    cluster = cluster.where(~clash)
    assert (df.groupby(cluster)["schooltype"].nunique() == 1).all()
    print("arm by school:", arm_of_school.astype(int).to_dict())

    for k in (1, 3, 6, 7, 8, 10, 11, 12, 15):   # the eight reversed copies are 2 - raw
        raw, rev = df[f"DEPRESSION{k}"], df[f"DEPRESSION{k}reversed"]
        ok = raw.between(0, 2) & rev.notna()
        assert ((2 - raw[ok]) == rev[ok]).all(), k

    base = pd.DataFrame({
        "id": df["id"], "wave": df["status"].astype(int),
        "treat": df["schooltype"].astype(int), "cluster_id": cluster.astype("Int64"),
        "cov_age": df["q1age"].astype("Int64"), "cov_gender": df["q2gender"].map({1: "male", 2: "female"}),
        "cov_grade": df["q3grade"].astype("Int64"), "cov_family_size": df["familysize"].astype("Int64"),
    })
    cov_cols = ["cov_age", "cov_gender", "cov_grade", "cov_family_size"]

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, (cols, lo, hi) in BLOCKS.items():
        wide = df[["id", "status"] + cols].copy()
        bad = 0
        for c in cols:
            out = wide[c].notna() & ~wide[c].between(lo, hi)
            if out.any():
                print(f"  {name} {c}: {int(out.sum())} out-of-range cell(s) {sorted(wide.loc[out, c].unique())} -> NaN")
            bad += int(out.sum())
            wide[c] = wide[c].where(~out)
        print(f"{name}: {bad} data-entry cells dropped")
        long = wide.rename(columns={"status": "wave"}).melt(
            id_vars=["id", "wave"], value_vars=cols, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) == set(range(lo, hi + 1)), (name, sorted(long["resp"].unique()))
        long = long.merge(base, on=["id", "wave"], how="left")
        long = long[["id", "item", "resp", "wave", "treat", "cluster_id"] + cov_cols]
        assert long["id"].nunique() == N_IDS and long["item"].nunique() == len(cols)
        assert not long.duplicated(["id", "item", "wave"]).any()
        checks = run_qc(long, permitted_values={c: list(range(lo, hi + 1)) for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"waves={sorted(long['wave'].unique())} resp={lo}-{hi}")
    print(f"TOTAL responses: {total}")


if __name__ == "__main__":
    convert()
