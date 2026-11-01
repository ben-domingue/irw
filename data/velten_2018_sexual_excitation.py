#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0193080
# DOI: 10.1371/journal.pone.0193080
# Paper: Velten, J., Scholten, S., & Margraf, J. (2018). Psychometric
#   properties of the Sexual Excitation/Sexual Inhibition Inventory for Women
#   and Men (SESII-W/M) and the Sexual Excitation Scales/Sexual Inhibition
#   Scales-Short Form (SIS/SES-SF) in a population-based sample in Germany.
#   PLOS ONE 13(3): e0193080.
# Data: journal.pone.0193080.s002 (S1 File, "Dataset", .sav). 2,708 adults
#   from a population-based German sample (random residential sample aged
#   18-75, telephone screening, then online or paper-pencil questionnaire).
# License: CC BY 4.0 (the article; the data is its own Supporting Information
#   file. The Data Availability statement withholds a DIFFERENT dataset, the
#   U.S. comparison sample, which is not in this file.)
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30, worked from
# leads/plos_leads_2026-10-30.csv on 2026-10-31 (BATCH_LOG.md).
#
# TWO output tables:
#   velten_2018_sesii_wm   sesiiwm1..30, 1-4 (Lehne stark ab .. Stimme stark
#                          zu), the SESII-W/M's 30 items as administered in
#                          German; the deposit also carries the authors'
#                          derived subscale means for both the original
#                          30-item and the revised 24-item scoring, which are
#                          not shipped.
#   velten_2018_sis_ses_sf sisses1..14, 1-4 (Trifft überhaupt nicht zu ..
#                          Trifft genau zu), the SIS/SES-SF's 14 items.
# 99 ("keine Angabe", no answer) and -2 ("Filter") become missing.
#
# The item columns' variable labels are just their own names (checked: both
# label levels read; the value labels carry the German anchors, the variable
# labels carry no stem), so the codes are the deposit's column names and the
# item order is the only tie to wording.
#
# Not shipped: the FSFI, IIEF, SOI-R, PHQ and SWLS -- present only as derived
# scale means (fractional values), not items; the derived SESII/SIS subscale
# means and totals.
#
# `id` is the row index (no respondent id in the file).
#
# Covariates: gender, age in years, relationship status, partnership
# duration in years, number of children, sexual orientation code, steady
# partner (yes/no), survey mode (online vs paper), couple-study flag (both
# partners interviewed), high-school degree, net household income band.
#
# Item text: NOT SHIPPED. The variable labels carry no stems, and both
# instruments are third-party (SESII-W/M: Milhausen, Graham, Sanders, Yarber
# & Maitland 2010; SIS/SES-SF: Carpenter, Janssen, Graham, Vorst & Wicherts
# 2011), translated into German by these authors; register rows added, hold.

import os
import re
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("VELTEN_RAW", "S1_File.sav")
N_ROWS = 2708
MISSING = [99, -2]
ANCHORS = {   # the German anchors on every item of each block, 1-4
    "velten_2018_sesii_wm": {1.0: "Lehne stark ab", 2.0: "Lehne ab", 3.0: "Stimme zu", 4.0: "Stimme stark zu"},
    "velten_2018_sis_ses_sf": {1.0: "Trifft überhaupt nicht zu", 2.0: "Trifft nicht zu", 3.0: "Trifft zu", 4.0: "Trifft genau zu"},
}
BLOCKS = {
    "velten_2018_sesii_wm": [f"sesiiwm{i}" for i in range(1, 31)],
    "velten_2018_sis_ses_sf": [f"sisses{i}" for i in range(1, 15)],
}


def convert():
    df, meta = pyreadstat.read_sav(RAW, apply_value_formats=False)
    labels, vl = meta.column_names_to_labels, meta.variable_value_labels
    assert len(df) == N_ROWS, len(df)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert not txt
    extra = [c for c in df.columns if re.fullmatch(r"(sesiiwm|sisses)\d+", c)]
    assert sorted(extra) == sorted(BLOCKS["velten_2018_sesii_wm"] + BLOCKS["velten_2018_sis_ses_sf"])

    df["id"] = range(1, N_ROWS + 1)
    cov = pd.DataFrame({
        "id": df["id"],
        "cov_gender": df["gender"].map({1: "male", 2: "female"}),
        "cov_age": df["age"].astype("Int64"),
        "cov_relationship_status": df["rel_status"].astype("Int64"),
        "cov_relationship_years": df["rel_dur"],
        "cov_n_children": df["kids"].astype("Int64"),
        "cov_sexual_orientation": df["sex_orient"].astype("Int64"),
        "cov_steady_partner": df["rel_group"].map({1: 1, 2: 0}).astype("Int64"),
        "cov_survey_mode": df["mode"].map({1: "online", 2: "paper"}),
        "cov_couple_study": df["couple"].astype(int),
        "cov_high_school_degree": df["highschool"].astype("Int64"),
        "cov_income_band": df["income"].astype("Int64"),
    })
    assert vl["gender"] in ({1.0: "male", 2.0: "female"}, {1.0: "männlich", 2.0: "weiblich"}) or set(df["gender"]) == {1, 2}
    assert vl["mode"].get(1.0, "").lower().startswith("online") or set(df["mode"]) == {1, 2}
    assert vl["rel_group"] == {1.0: "yes", 2.0: "no"} or set(df["rel_group"]) == {1, 2}
    print("gender labels:", vl.get("gender"), "| mode:", vl.get("mode"), "| rel_group:", vl.get("rel_group"))
    cov_cols = [c for c in cov.columns if c != "id"]

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, cols in BLOCKS.items():
        wide = df[["id"] + cols].copy()
        for c in cols:
            assert labels[c] == c, (c, labels[c])            # no stem in the variable label
            anchors = {k: v for k, v in vl[c].items() if 1 <= k <= 4}
            assert anchors == ANCHORS[name], (c, vl[c])
            wide[c] = wide[c].where(~wide[c].isin(MISSING))
        long = wide.melt(id_vars=["id"], value_vars=cols, var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) == {1, 2, 3, 4}, sorted(long["resp"].unique())
        long = long.merge(cov, on="id", how="left")[["id", "item", "resp"] + cov_cols]
        assert long["item"].nunique() == len(cols) and not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4] for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} resp=1-4")
    print(f"TOTAL responses: {total}")


if __name__ == "__main__":
    convert()
