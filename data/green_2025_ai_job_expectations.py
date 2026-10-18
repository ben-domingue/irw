#!/usr/bin/env python3
# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/G1JVQ4
# DOI: 10.7910/DVN/G1JVQ4
# Data: AIpaper_Data_R&Pclean.dta  -- the ORIGINAL Stata 14 file, fetched with
#   ?format=original, NOT the .tab conversion Dataverse serves by default.
# License: CC0 1.0 (verified on the Dataverse record)
# Reference: Green, J., Grant, Z., Evans, G., & Inglese, G. (2025).
#   Replication Data for: Linking Artificial Intelligence Job Exposure to
#   Expectations. British Election Study internet panel.
#
# 4,249 respondents, one row each. Two item batteries ship:
#
#   longjobimpact{1,2,3,6,7,8}   job impact, 1-5 ordinal  -> _job_impact
#   polpreferences{1,4,6}        policy support, 1-5      -> _policy_preferences
#
# WHY `format=original` MATTERED HERE, concretely. The .tab conversion shows
# `jobimpact1_technology..jobimpact8_recession` as a tidy six-item block with
# values 1-4 and no missingness -- it looks like the better of the two blocks
# and it is what the triage counted. The original's value labels show what it
# actually is:
#
#   jobimpact*      {1: 'No Impact', 2: 'Worsen', 3: 'Improve', 4: "Don't Know"}
#   longjobimpact*  {1: 'Worsen my job prospects a lot' ... 5: 'Improve my job
#                    prospects a lot', 99: "Don't know",
#                    999: 'NA - Not asked (aged 70+)'}
#
# `jobimpact*` is a NOMINAL collapse of the same question -- 2='Worsen' sorts
# below 3='Improve' with 1='No Impact' beneath both, so it is not ordinal and
# cannot be `resp` -- and its category 4 folds the don't-knows into the scale.
# The labels are also explicit that the two blocks are the "4 Cat Version" and
# "6 Cat Version" of one battery, so shipping both would put the same answers
# in the corpus twice. Only the ordinal version ships. None of this is visible
# in the .tab.
#
# SENTINELS INSIDE THE RANGE. 99 ("Don't know") and 999 ("NA - Not asked, aged
# 70+") are non-responses, not scale steps, and 99 also appears in
# polpreferences. Those item-responses are FILTERED OUT per row -- not recoded
# to a scale value and not grounds for dropping the respondent, who answers
# other items fine.
#
# RIGHTS: both batteries are British Election Study questionnaire items, not a
# published psychometric instrument; no register row applies.
#
# PII: none. The file is a cleaned replication extract -- `ES_id` is a panel
# serial, and the only geography is region/province codes.
#
# Item text: NOT shipped. Value labels give every response option verbatim,
# but the variable labels are topic descriptors ("Job Impact: Artificial
# Intelligence (6 Cat Version)", "How Much Support - Gov redistributing
# incomes from better-off ...") rather than the administered question stem.
# Shipping option_text with a descriptor standing in for a stem would be
# inventing the stem. Where the text is: the BES internet panel questionnaire
# for the relevant wave.

import os

import pandas as pd
import pyreadstat

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "automated_finding", "runs", "hr5", "raw",
                   "g1jvq4__AIpaper_Data_R&Pclean.dta")

JOB = [f"longjobimpact{i}_{n}" for i, n in
       [(1, "technology"), (2, "AI"), (3, "immigration"), (6, "greentax"),
        (7, "imports"), (8, "recession")]]
POL = ["polpreferences1_redistribution", "polpreferences4_immigration",
       "polpreferences6_education"]
NOMINAL = [f"jobimpact{i}_{n}" for i, n in
           [(1, "technology"), (2, "AI"), (3, "immigration"), (6, "greentax"),
            (7, "imports"), (8, "recession")]]
SENTINEL = {99.0, 999.0}

COVS = {"age": "cov_age", "female_dummy": "cov_female",
        "degree_dummy": "cov_degree", "employmentstatus": "cov_employment",
        "employsector": "cov_employment_sector",
        "isco08_5group": "cov_isco08_5group",
        "equivincomeHHquintile_HBAI_imp": "cov_income_quintile",
        "profile_leftrightplacement": "cov_left_right",
        "aiexposure_pizzinelli": "cov_ai_exposure_pizzinelli",
        "aiexposure_gmyrek": "cov_ai_exposure_gmyrek"}

BLOCKS = {"job_impact": JOB, "policy_preferences": POL}


def convert():
    df, meta = pyreadstat.read_dta(RAW)
    vlabs = meta.variable_value_labels or {}
    print(f"raw: {df.shape}")
    assert df["ES_id"].nunique() == len(df), "ES_id is not unique"
    df = df.rename(columns={"ES_id": "id"})

    # State the nominal-collapse finding in the run output, with the evidence.
    jl = vlabs.get(NOMINAL[0]) or {}
    assert set(str(v) for v in jl.values()) >= {"No Impact", "Worsen", "Improve"}, \
        "jobimpact value labels changed -- re-check whether it is ordinal now"
    print(f"dropping {NOMINAL[0]}..{NOMINAL[-1]}: value labels are "
          f"{jl} -- a nominal collapse of the same question longjobimpact asks "
          f"ordinally, and labelled '4 Cat Version' against '6 Cat Version'")

    cov_src = {k: v for k, v in COVS.items() if k in df.columns}
    accounted = set(["id"]) | set(cov_src) | set(JOB) | set(POL) | set(NOMINAL)
    skipped = {}
    for c in df.columns:
        if c in accounted:
            continue
        if c in NOMINAL:
            skipped[c] = "nominal collapse, see above"
        elif c == "w":
            skipped[c] = "survey weight"
        elif c.startswith("aiexposure") or c.startswith("std_"):
            skipped[c] = "external AI/routine-task exposure measure merged in"
        elif c.endswith(("_worsen", "_improve", "_directionworse")):
            skipped[c] = "binary recode derived from the jobimpact block"
        elif c.endswith(("_3group", "_10group")) or c in ("age_3group",):
            skipped[c] = "banded recode of a covariate already carried"
        elif c in ("pid", "rank"):
            skipped[c] = "party id / rank, single categorical, not an item"
        else:
            skipped[c] = "not an item or covariate"
    for c, why in sorted(skipped.items()):
        print(f"  skip {c:34} {why}")
    assert accounted | set(skipped) == set(df.columns), "books do not balance"

    written = set()
    for name, cols in BLOCKS.items():
        long = (df[["id"] + cols].melt(id_vars="id", var_name="item",
                                       value_name="resp")
                .dropna(subset=["resp"]))
        long["resp"] = long["resp"].astype(float)

        n_before = len(long)
        long = long[~long["resp"].isin(SENTINEL)]
        dropped = n_before - len(long)
        print(f"  {name}: filtered {dropped} sentinel item-responses "
              f"(99 don't know / 999 not asked)")

        # Every remaining value must be a labelled, non-sentinel category.
        for c in cols:
            permitted = set(float(k) for k in (vlabs.get(c) or {})) - SENTINEL
            obs = set(long.loc[long["item"] == c, "resp"].unique())
            assert permitted, f"{c}: no value labels"
            bad = obs - permitted
            assert not bad, f"{c}: {sorted(bad)} outside {sorted(permitted)}"

        long = long.merge(df[["id"] + list(cov_src)].rename(columns=cov_src),
                          on="id", how="left")
        assert long["item"].nunique() > 1, f"{name}: single item"
        assert long["id"].nunique() >= 100, f"{name}: N={long['id'].nunique()}"
        long = long[["id", "item", "resp"] + list(cov_src.values())]

        out_name = f"green_2025_{name}"
        assert out_name not in written, f"duplicate output name {out_name}"
        written.add(out_name)
        long.to_csv(os.path.join(OUT_DIR, f"{out_name}.csv"), index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
