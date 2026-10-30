#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0291876
# DOI: 10.1371/journal.pone.0291876
# Paper: Mahajan, P., & Patil, V. (2023). 'College choice' under the COVID-19
#   pandemic: sustainability of engineering campuses for future enrollments.
#   PLOS ONE 18(9): e0291876.
# Data: figshare 10.6084/m9.figshare.23521551, "SPSS DATA FOR MANUSTRIPT.sav",
#   516 rows x 21 columns.
#
# LICENCE verified on the DEPOSIT, not the article: the data is hosted
# off-site on figshare. api.figshare.com/v2/articles/23521551 reports
# CC BY 4.0.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# ONE output table, 12 items, 6,192 responses, zero missing cells. 516
# first-year engineering students aged 17-19 at colleges in North
# Maharashtra, India, who chose their college in January 2021; surveyed by
# email and WhatsApp in February 2021.
#
# ONE BATTERY, AND THE COLUMN NAMES ARE THE FACTORS. Twelve 1-5 columns name
# the college-choice factor each rates -- proximity, location, image and
# reputation, faculty profile, alumni profile, campus placements, quality of
# engineering education, infrastructure, the safety/security/hygiene
# environment, curriculum delivery, value for money and sustainability. No
# block inference was needed; the remaining eight columns are categorical
# demographics and influence sources, which is what separates them.
#
# THE SCALE'S DIRECTION IS WEAKLY STATED AND SHIPS AS DEPOSITED. The article
# says only that respondents used "a 5-point Likert scale" where 1 is the
# "minimum value" and 5 the "maximum value", and gives no verbal anchors. So
# 5 is the high end of whatever the factor measures, which for an importance
# battery means most important -- but the article never says the word, and
# the description records that rather than asserting it. Same treatment as
# li_2024_vr_* and wang_2023_eco_* in this batch.
#
# `id` is the deposit's `SN`, which is stored as a STRING and is verified
# unique over all 516 rows -- worth noting because a column of '1'..'516'
# read as text is the kind of thing a numeric-column selector misses.
#
# EIGHT COVARIATES SHIP AS THE DEPOSIT'S OWN LABELS, not codes, which removes
# the pinning problem entirely: gender ('Male'/'Female'), social class ('BC',
# 'OBC', 'General' -- India's reserved-category classifications), native place
# ('District'/'Taluka'/'Village'), pre-college performance ('DC'/'FC'/'SC' --
# distinction, first and second class), major ('Computer'/'Non Compu'),
# curriculum delivery mode ('Online'/'Onsite'/'Semi.Mode'), and the two
# influence sources (who influenced the choice, and which information channel).
# The article does not define BC/OBC/General or DC/FC/SC, so those ship as
# the abbreviations the deposit uses.
#
# THE GENDER SPLIT PINS THE FILE AS THE ANALYSED ONE: 348 male and 168
# female against the article's "348 male (67.4%), 168 female (32.6%)",
# asserted below.
#
# Item text: NOT SHIPPED. The column names are factor LABELS, not the
# questions as asked; the article says the questionnaire was closed-ended and
# describes the questions "in narrative form" without reproducing them.
# Shipping a label as item_text would put a paraphrase where readers expect
# transcription.
#
# PII: screened over all 21 columns. The string columns are the id and the
# eight categorical covariates, each a closed vocabulary of 2-8 levels.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("MAHAJAN_RAW", "SPSS DATA FOR MANUSTRIPT.sav")

TABLE = "mahajan_2023_college_choice_factors"
N_ROWS = 516
LO, HI = 1, 5
GENDER = {"Male": 348, "Female": 168}

ITEMS = ["Proximity", "Location.Locality", "Image.Reputation",
         "Faculty.Profile", "Alumni.Profile", "Campus.Placements",
         "Quality.EE", "Infrastructure.Facility", "SSH.Environment",
         "Curriculum.Delivery", "Value.for.money", "Sustainability"]
COVS = {"Gender": "cov_gender", "Social.Class": "cov_social_class",
        "Native.Place": "cov_native_place",
        "Precollege.Performance": "cov_precollege_performance",
        "Major.Choice": "cov_major", "Curri.Delivery.Mode": "cov_delivery_mode",
        "Human.Influence": "cov_human_influence",
        "Information.Influence": "cov_information_source"}


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert len(df) == N_ROWS, len(df)

    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert set(strings) == {"SN"} | set(COVS), sorted(strings)
    for c in COVS:
        assert df[c].nunique() <= 8, (c, df[c].nunique())
    print(f"PII screen: {len(strings)} string columns -- the id and the eight "
          f"categorical covariates, each a closed vocabulary of 2-8 levels. "
          f"No names, emails, dates or free text")

    left_out = [c for c in df.columns
                if c not in set(ITEMS) | set(COVS) | {"SN"}]
    assert not left_out, f"unaccounted source columns: {left_out}"

    got = df["Gender"].value_counts().to_dict()
    assert got == GENDER, (
        f"the gender split is {got}, not the article's {GENDER} -- this may "
        f"not be the analysed file")
    print(f"gender split {got} matches the article exactly, so this is the "
          f"analysed file")

    assert df["SN"].nunique() == len(df), "SN is not unique"
    d = df.rename(columns={"SN": "id", **COVS})
    cov_cols = sorted(COVS.values())

    assert int(d[ITEMS].isna().sum().sum()) == 0, "missing cells"
    vals = pd.to_numeric(d[ITEMS].stack(), errors="coerce")
    assert vals.notna().all() and vals.between(LO, HI).all(), \
        sorted(vals.unique())
    assert (vals % 1 == 0).all(), "a fractional response"

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(int)
    assert long["id"].nunique() == N_ROWS
    assert long["item"].nunique() == len(ITEMS)
    assert not long.duplicated(["id", "item"]).any()
    assert len(long) == len(ITEMS) * N_ROWS, len(long)
    assert len(TABLE) <= 40, TABLE
    long = long[["id", "item", "resp"] + cov_cols]

    checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                            for i in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:150]}")

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
