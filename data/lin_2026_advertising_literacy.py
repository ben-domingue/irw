#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0348505
# DOI: 10.1371/journal.pone.0348505
# Paper: Lin, Y.-E. C., Chang, F.-C., Huang, T.-F., Chiang, S. C., Chiu, C.-H.,
#   & Chen, P.-H. (2026). Effects of social media sponsorship disclosure on
#   adolescents' advertising literacy and purchase intention. PLOS ONE 21(5).
# Data: figshare 30304291 -- "Supporting_Information_DATA_Set.xls", one sheet
#   'DATA_final_Set', 3,275 rows x 23 columns. Downloaded from
#   https://ndownloader.figshare.com/files/58652731
#
# LICENCE verified on the DEPOSIT: the Data Availability statement points
# off-site to figshare, so the article's CC BY cannot grant the data's licence.
# api.figshare.com/v2/articles/30304291 reports CC BY 4.0. Fourth deposit in
# this batch needing that separate check.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# ONE output table. It IS an experiment, but it deliberately does NOT carry a
# `treat` column -- see "THE ARM COLUMN IS NOT SHIPPABLE AS `treat`" below.
# 3,275 Taiwanese high-school students (10th-12th grade) drawn from 36 schools
# in 2022 by probability-proportional-to-size sampling, randomly assigned to
# one of three sponsorship-disclosure conditions.
#
# THE CONDITION AND THE CLUSTER ARE BOTH RECOVERABLE, which is what makes this
# shippable rather than a lead. Neither column is documented -- the deposit
# ships no codebook and the columns are named No1..No5 -- so each was
# identified against the paper and the identification is asserted:
#   No1 = the randomised arm. The paper: "Adolescents were randomly assigned
#          to one of the three experimental conditions, full disclosure,
#          partial disclosure, and no disclosure (control)." No1 takes exactly
#          three values in near-equal cells (1,108 / 1,086 / 1,081), which is
#          what random assignment to three arms looks like and what no other
#          column here looks like. Asserted: three levels, none departing from
#          a third of the sample by more than 3%.
#   No3 -> `cluster_id`. The paper: "recruited from 36 schools". No3 has
#          exactly 36 distinct values. Asserted. `cluster_id` rather than a
#          `cov_` column because datastandard.md reserves it for "the group a
#          focal unit is nested in -- classroom, teacher, school" and says
#          never to `cov_`-prefix it. Note that randomisation here was at the
#          individual level, not by school, so `treat` is NOT constant within
#          a cluster in this design. A school code is an institution rather
#          than geography, so the 2026-10-20 geographic ruling does not reach
#          it.
#
# THE ARM COLUMN IS NOT SHIPPABLE AS `treat`, and this table omits it rather
# than bending the standard. datastandard.md defines `treat` as exactly
# "`1` = treatment, `0` = control" and tells scripts to "Map whatever coding
# the source uses (e.g., 1/2) to the standard 0/1 encoding". That cannot be
# done honestly here, for two independent reasons:
#   * there are THREE arms, two of which are treatments (full and partial
#     disclosure), so a 0/1 column cannot represent the design without
#     collapsing two distinct manipulations into one; and
#   * the deposit never says which of the codes 1/2/3 is the control. Guessing
#     would mislabel the control group, and a downstream tool that assumes
#     0/1 would then compute an effect against the wrong baseline.
# Shipping 1/2/3 in `treat` would be worse than omitting it -- it looks
# conformant and is not -- and `cov_group` is explicitly ruled out by the
# standard for a treatment. So the arm is left out, the responses still ship,
# and the open question is recorded in TODO.md: whether IRW wants a
# convention for multi-arm designs, and whether the code-to-arm mapping is
# worth recovering from the paper's reported per-arm means (the same
# reconstruct-from-published-statistics route used for
# trusz_2022_iieq in the 2026-10-29f batch).
#
# THE 14 ITEMS SPAN THREE CONSTRUCTS AND THE BOUNDARIES ARE NOT RECOVERABLE.
# This is the honest limitation of this table and it is in the description.
# SD_A3..SD_A16 are 14 items all on the paper's 4-point scale ("from 1
# (strongly disagree) to 4 (strongly agree)"), and the paper's own validity
# table names three constructs -- conceptual advertising literacy, attitudinal
# advertising literacy and purchase intention -- with attitudinal measured by
# four items and purchase intention by two. That accounts for 4 + 2 + 8 = 14.
# But NOTHING in the deposit or the article maps a construct to an SD_A code,
# and the obvious guess (A3-A10 conceptual, A11-A14 attitudinal, A15-A16
# purchase) is only an ordering assumption.
#
# So they ship as ONE table rather than three guessed ones. Two reasons beyond
# caution: a wrong split would silently assign items to the wrong construct,
# which is unrecoverable downstream; and purchase intention has only two items,
# so the correct split would itself produce a table below the three-item floor.
# One table of 14 items on one scale, with the construct mix stated, is the
# truthful object here.
#
# Not shipped:
#   SD_A1 (1-2), SD_A2 (1-3)   on different scales from the 14-item battery and
#                              undocumented; SD_A1's binary form matches the
#                              paper's ad-recognition measure ("Is the post an
#                              ad or not an ad?"), but that is an inference
#                              about an outcome variable, and two items on two
#                              different scales are not a battery
#   No2, No4, No5              undocumented. No5's four levels cannot be the
#                              paper's three grades (10th/11th/12th), and No4's
#                              two levels are not gender either -- Ssex already
#                              carries that. Rather than invent meanings for
#                              covariates, they are dropped. This is the
#                              deposit's documentation gap, not a data problem.
#   ID                         a 7-digit code whose first digits track No3, so
#                              it encodes the school. Discarded; `id` is the
#                              row index, for the same reason the Kendall 2018
#                              serial was discarded in this batch.
#
# N DIFFERS FROM THE PAPER, deliberately, and the shape of the difference is
# worth stating. The paper analyses 3,149 valid responses "after excluding
# questionnaires with missing data"; the deposit holds 3,275 rows, i.e. it is
# the pre-exclusion file. Of those, 8 respondents answered NONE of the 14
# items -- they contribute no row to a long table at all, so they are dropped
# and the count is asserted at exactly 8. The remaining 3,267 are kept: 3,220
# answered all 14, 44 skipped one, 2 skipped two and 1 skipped ten. Their
# responses are real, and excluding a respondent for an unrelated blank is the
# paper's analytic choice rather than a property of the data -- which is why
# this table has 3,267 ids rather than the paper's 3,149.
#
# cov_sex: the deposit codes 1/2 with 3 zeros and 25 blanks. A 0 against a
# documented male/female dichotomy is an undeclared missing code, so the zeros
# are blanked rather than shipped as a third sex category.
#
# Item text: NOT SHIPPED. The paper quotes six of the fourteen items verbatim
# (the four attitudinal ones and the two purchase-intention ones), so some
# wording is in hand -- but it cannot be attached to a column code for exactly
# the reason above, and shipping text for 6 of 14 items against a guessed
# mapping is the failure mode an itemtext table must avoid. The instrument is
# adapted from the Persuasion Knowledge Model literature, not study-authored,
# so a register row is written with verdict hold as well.
#
# PII: screened over all 23 columns. Every one is numeric; no names, emails,
# dates, free text or row-level geography. The school identifier is a code.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LIN_RAW", "Supporting_Information_DATA_Set.xls")

TABLE = "lin_2026_advertising_literacy"
N_ROWS = 3275
N_KEPT = 3267   # less the 8 who answered none of the 14 items
LO, HI = 1, 4
N_SCHOOLS = 36

ITEMS = [f"SD_A{i}" for i in range(3, 17)]
DROP = {
    "ID": "7-digit code that encodes the school (its lead digits track No3)",
    "SD_A1": "different scale (1-2), undocumented",
    "SD_A2": "different scale (1-3), undocumented",
    "No2": "undocumented covariate",
    "No4": "undocumented covariate",
    "No5": "undocumented covariate (4 levels; the paper's grades are 3)",
}


def screen_for_pii(df):
    txt = [c for c in df.columns
           if pd.api.types.is_string_dtype(df[c])
           and pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert not txt, f"unexpected text column(s) -- screen them: {txt}"
    print("  every column is numeric; no name, email, date, free text or "
          "row-level geography (the school is a code)")


def identify_design(df):
    """No1 and No3 are undocumented. Identify each against the paper and assert
    the identification, so a different file cannot quietly take their place."""
    arms = df["No1"].value_counts()
    assert len(arms) == 3, f"No1 has {len(arms)} levels, expected 3 arms"
    share = arms / len(df)
    assert (share - 1 / 3).abs().max() < 0.03, (
        f"No1's cells are not near-equal thirds ({share.to_dict()}), so it is "
        f"probably not the randomised condition after all")
    print(f"No1 identified as the randomised arm: 3 near-equal cells "
          f"{arms.sort_index().to_dict()} -- the paper's full / partial / no "
          f"disclosure randomisation. NOT shipped as `treat`: three arms "
          f"cannot be a 0/1 column and the deposit never says which code is "
          f"the control (see header)")

    schools = df["No3"].nunique()
    assert schools == N_SCHOOLS, (
        f"No3 has {schools} distinct values, but the paper reports "
        f"{N_SCHOOLS} schools -- do not ship it as cov_school")
    print(f"cluster_id = No3: exactly {schools} distinct values, matching the "
          f"paper's 36 sampled schools")


def convert():
    df = pd.read_excel(RAW, sheet_name=0)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)
    identify_design(df)

    accounted = set(ITEMS) | set(DROP) | {"No1", "No3", "Ssex"}
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    assert len(ITEMS) == 14

    vals = pd.to_numeric(df[ITEMS].stack(), errors="coerce").dropna()
    assert vals.between(LO, HI).all(), sorted(vals.unique())
    assert (vals % 1 == 0).all(), "a fractional value reached the item set"
    # 8 respondents answered none of the 14 items: they cannot contribute a
    # row, so they go. Asserted at exactly 8 so a file where whole-battery
    # nonresponse is widespread fails here instead of quietly shrinking.
    empty = ~df[ITEMS].notna().any(axis=1)
    assert int(empty.sum()) == 8, int(empty.sum())
    df = df[~empty].copy()
    print(f"dropped {int(empty.sum())} respondents who answered none of the 14 "
          f"items (the deposit is the paper's pre-exclusion file)")
    skipped = int(df[ITEMS].isna().sum().sum())

    # 0 against a documented male/female dichotomy is an undeclared missing code
    zeros = int((df["Ssex"] == 0).sum())
    df.loc[df["Ssex"] == 0, "Ssex"] = pd.NA
    print(f"cov_sex: blanked {zeros} cells coded 0 against a documented "
          f"male/female dichotomy (undeclared missing code), plus "
          f"{int(df['Ssex'].isna().sum()) - zeros} already blank")

    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    # No1 (the arm) is deliberately not carried -- see the header
    df = df.rename(columns={"No3": "cluster_id", "Ssex": "cov_sex"})
    keep = ["id", "cluster_id", "cov_sex"]

    long = df.melt(id_vars=keep, value_vars=ITEMS,
                   var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    assert long["id"].nunique() == N_KEPT, long["id"].nunique()
    assert long["item"].nunique() == 14
    assert "treat" not in long.columns, "the 3-arm condition must not ship as treat"
    assert long["cluster_id"].nunique() == N_SCHOOLS
    assert not long.duplicated(["id", "item"]).any()
    assert len(long) == 14 * N_KEPT - skipped, len(long)
    assert len(TABLE) <= 40, TABLE

    long = long[["id", "item", "resp", "cluster_id", "cov_sex"]]

    # gate before writing -- the contract check requires the validator to run
    # in-script, not just on the output file
    checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                            for i in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:175]}")

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()} "
          f"({skipped} cells skipped, {long['cluster_id'].nunique()} school "
          f"clusters; the 3-arm condition is NOT shipped -- see header)")


if __name__ == "__main__":
    convert()
