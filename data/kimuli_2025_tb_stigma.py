#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0313750
# DOI: 10.1371/journal.pone.0313750
# Paper: Kimuli, D., Nakaggwa, F., Namuwenge, N., Kamara, V., Nakawooya, M.,
#   Amanya, G., Tumwesigye, P., Mwehire, D., et al. (2025). Level of
#   tuberculosis-related stigma and associated factors in Ugandan communities.
#   PLOS ONE 20(1).
# Data: journal.pone.0313750.s003 (S1 Dataset, .xlsx), 33,349 rows x 31 columns.
# License: CC0 1.0 -- the PLOS article is CC0 (confirmed in Crossref's licence
#   record for the version of record,
#   https://creativecommons.org/publicdomain/zero/1.0/) and the dataset is a
#   Supporting Information file of that article, not a third-party deposit.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (see
# BATCH_LOG.md) -- the second-largest `good` lead of that run by response count.
#
# ONE output table: the 10-item TB stigma battery, asked of all 33,349
# respondents in three survey strata (youth, men, women).
#
# THE resp CODING, and why "Dont know" is DROPPED rather than scored.
# Each stigma item was recorded as one of four text labels: "Not true at all",
# "Somewhat true", "Very True", "Dont know". The deposit also ships its own
# tb_stigma_score, and that score pins the depositors' coding exactly: over all
# 24 possible assignments of {0,1,2,3} to the four labels, exactly ONE
# reproduces tb_stigma_score on all 33,349 rows --
#     Dont know = 0, Not true at all = 1, Somewhat true = 2, Very True = 3
# (asserted below, and the 23 rival mappings are checked and must all fail, so
# this is a unique solution rather than a plausible guess).
#
# That coding places "Dont know" BELOW "Not true at all" on a stigma scale,
# i.e. it treats not knowing as the least stigmatising answer available. It is
# not: a don't-know is a non-answer, and the three substantive labels are
# ordinal while the four together are not. Scoring it 0 would ship a nominal
# category wearing an ordinal mask, so the ~10% of cells labelled "Dont know"
# are dropped and resp carries the three substantive levels as 1-3. The
# consequence is stated in the table description: these are not missing at
# random (a don't-know rate of 9-12% per item, 11.6% of all cells), so the
# dropped cells are informative and anyone modelling these items should read
# the source. 2,012 of the 33,349 respondents answered "Dont know" to all ten
# items and so leave the table entirely, taking it to 31,337 ids -- asserted
# below. Those same 2,012 carry tb_stigma_score = 0, every one of them, which
# is the published score's floor: under the deposit's coding a respondent who
# knew nothing is indistinguishable from the least stigmatising respondent in
# Uganda. That is the concrete reason this table does not reuse that coding.
#
# NOT shipped, each for a reason:
#   tb_stigma_score, tbknowlegde, tbknowlegde_cat   composites
#   Q502HowisTBtransmitted1-3    a multi-select "how is TB transmitted" pick
#                                list (codes 1/2/3/99) -- nominal, and the
#                                three columns are picks, not items
#   tb_dransmit_dontknow, tbsymp_dontknow1, tbtrtconseq_dk1
#                                constant 0 for all 33,349 rows -- zero
#                                variance, no information
#   the 3 binary knowledge items (tb_transmit_exposuretbgerms,
#   drink_unpasterized_milk, isTBcurable)
#                                these would clear the 3-item floor, but
#                                tbknowlegde runs 0-15, so they are 3 surviving
#                                components of a 15-part knowledge score whose
#                                other parts are either constant or nominal in
#                                this file. Three-fifteenths of a scale, mixing
#                                a misconception item (unpasteurised milk) with
#                                a fact item (is TB curable), is not a
#                                coherent battery. Skipped on the
#                                err-on-exclusion rule; noted in BATCH_LOG.
#   agecat_report                a coarser recode of ageband (10-19/20-29/30+
#                                against 14-19...45-59); the finer one is kept
#
# Item text: NOT shipped with this batch. The ten stems are the Van Rie et al.
# (2008) TB stigma scale items as adapted for the Uganda Population-Based HIV
# Impact Assessment; the column names here are keywords ("behave_diff",
# "play_children"), not wording, and the article's Table 3 prints paraphrases
# rather than the administered question. A register row is written with this
# batch, verdict hold pending the administered wording.
#
# PII: screened over every column. No names, emails, phone numbers, dates or
# free text, and no geographic column at all -- not even district, which a
# national survey would usually carry. ObjectID is a sequential 1..33,349
# record number, unique per row, and is used as `id`.

import os
import sys
from itertools import permutations

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("KIMULI_RAW", "journal.pone.0313750_S1_Dataset.xlsx")

TABLE = "kimuli_2025_tb_stigma"

ITEMS = ["behave_diff", "feel_uncomfortable", "play_children", "feel_hurt",
         "lose_friends", "worried_AIDS", "fear_telling_people",
         "fear_telling_family", "carefully_choose", "fear_tb_clinic"]

LABELS = ["Not true at all", "Somewhat true", "Very True", "Dont know"]
# the mapping the reconstruction below proves is the depositors' own
DEPOSIT_CODING = {"Dont know": 0, "Not true at all": 1,
                  "Somewhat true": 2, "Very True": 3}
# what ships: the three substantive levels only
SHIP_CODING = {"Not true at all": 1, "Somewhat true": 2, "Very True": 3}

COVS = {"survey": "cov_survey_stratum", "ageband": "cov_age_band",
        "marital": "cov_marital_status", "education_report": "cov_education",
        "hhsize": "cov_household_size_band", "hivtb": "cov_hiv_tb",
        "Children014years": "cov_children_0_14"}

DROP = {
    "ObjectID": "the record number -- becomes id",
    "agecat_report": "coarser recode of ageband, which is kept",
    "Q502HowisTBtransmitted1": "multi-select transmission pick list -- nominal",
    "Q502HowisTBtransmitted2": "multi-select transmission pick list -- nominal",
    "Q502HowisTBtransmitted3": "multi-select transmission pick list -- nominal",
    "tb_transmit_exposuretbgerms": "3 of a 15-part knowledge score (see header)",
    "drink_unpasterized_milk": "3 of a 15-part knowledge score (see header)",
    "isTBcurable": "3 of a 15-part knowledge score (see header)",
    "tb_dransmit_dontknow": "constant 0 -- zero variance",
    "tbsymp_dontknow1": "constant 0 -- zero variance",
    "tbtrtconseq_dk1": "constant 0 -- zero variance",
    "tb_stigma_score": "composite (sum of the 10 items)",
    "tbknowlegde": "composite",
    "tbknowlegde_cat": "composite, dichotomised",
}

PII_PAT = (r"[\w.+-]+@[\w-]+\.[a-z]{2,}"
           r"|\+?\d{9,}"
           r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")


def screen_for_pii(df):
    """Match over the text columns, printing the denominator so a zero is
    visible rather than silent. Columns whose every value parses as a number
    are not text columns and are excluded before matching -- a long decimal
    otherwise trips the nine-or-more-digits phone pattern."""
    txt = [c for c in df.columns
           if pd.api.types.is_string_dtype(df[c])
           and pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: examined {len(txt)} of {len(df.columns)} text "
          f"column(s): {txt}")
    assert txt, "PII screen selected no columns -- the selector is wrong"
    hits = [(c, v) for c in txt for v in df[c].dropna().astype(str).unique()
            if pd.Series([v]).str.contains(PII_PAT, regex=True, case=False).any()]
    assert not hits, f"PII screen hit: {hits[:5]}"
    print("PII screen: clean -- no email, phone, date or free-text column, "
          "and no geographic column at all")


def prove_deposit_coding(df):
    """The deposit's own tb_stigma_score identifies the label->code mapping
    uniquely. Check all 24 permutations: exactly one must reproduce it on every
    row, and the other 23 must fail. A unique solution is what licenses the
    claim in the header about what the depositors did with "Dont know"."""
    target = df["tb_stigma_score"]
    exact = []
    for perm in permutations([0, 1, 2, 3]):
        m = dict(zip(LABELS, perm))
        recon = sum(df[c].map(m) for c in ITEMS)
        if recon.equals(target):
            exact.append(m)
    assert len(exact) == 1, f"coding is not uniquely identified: {exact}"
    assert exact[0] == DEPOSIT_CODING, exact[0]
    print(f"tb_stigma_score reconstructs on all {len(df)} rows under exactly "
          f"one of the 24 possible codings: {DEPOSIT_CODING}")
    print("  -- so 'Dont know' was scored 0, BELOW 'Not true at all'. Dropped "
          "here rather than shipped as an ordered category; see the header.")


def convert():
    df = pd.read_excel(RAW)
    screen_for_pii(df)

    accounted = set(ITEMS) | set(COVS) | set(DROP)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"

    for c in ITEMS:
        seen = set(df[c].dropna().unique())
        assert seen <= set(LABELS), (c, seen - set(LABELS))
    assert df["ObjectID"].nunique() == len(df), "ObjectID is not unique"

    prove_deposit_coding(df)

    for c in ("tb_dransmit_dontknow", "tbsymp_dontknow1", "tbtrtconseq_dk1"):
        assert df[c].nunique() == 1, (c, "expected constant -- recheck DROP")

    df = df.rename(columns={"ObjectID": "id", **COVS})
    cov_cols = sorted(COVS.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                   var_name="item", value_name="label")
    observed = len(long)
    long = long[long["label"].isin(SHIP_CODING)].copy()
    dk = observed - len(long)
    print(f"dropped {dk} of {observed} cells labelled 'Dont know' "
          f"({dk / observed:.1%}) -- a non-answer, not an ordered category")
    long["resp"] = long["label"].map(SHIP_CODING).astype(int)

    assert long["resp"].between(1, 3).all(), long["resp"].unique()
    assert long["id"].nunique() >= 100, long["id"].nunique()
    assert long["item"].nunique() == len(ITEMS), long["item"].nunique()
    assert not long.duplicated(["id", "item"]).any()

    # the respondents who answered "Dont know" to every item leave the table;
    # pinned here because it is a 6% loss of ids, and because all 2,012 of them
    # sit at tb_stigma_score = 0 in the deposit (the score's floor)
    gone = df["id"].nunique() - long["id"].nunique()
    assert gone == 2012, gone
    allna = df.loc[~df["id"].isin(long["id"]), "tb_stigma_score"]
    assert (allna == 0).all(), sorted(allna.unique())
    print(f"{gone} respondents answered 'Dont know' to all 10 items and are "
          f"absent from the table; all {gone} carry tb_stigma_score = 0 in the "
          f"deposit, the published score's floor")

    long = long[["id", "item", "resp"] + cov_cols]

    # gate before writing -- the contract check requires the validator to run
    # in-script, not just on the output file
    checks = run_qc(long, permitted_values={i: [1, 2, 3] for i in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:180]}")

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
