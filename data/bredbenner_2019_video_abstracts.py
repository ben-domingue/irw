#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0224697
# DOI: 10.1371/journal.pone.0224697
# Paper: Bredbenner, K., & Simon, S. M. (2019). Video abstracts and plain
#   language summaries are more effective than graphical abstracts and
#   published abstracts. PLOS ONE 14(11): e0224697.
# Data: journal.pone.0224697.s007 (S7 File, .xlsx), 538 rows x 64 columns.
# License: CC BY 4.0 -- Supporting Information of the article itself.
# 538 respondents (research scientists, adults in science-related and
# non-science careers, undergraduates) randomised across 12 conditions.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# SEVEN output tables, 32 items, 16,470 responses. A randomised experiment,
# which is rarer in this batch than the survey deposits around it: each
# respondent saw ONE of twelve summary formats and then answered comprehension
# questions about two real papers.
#
# `cov_condition` IS THE EXPERIMENT: 4 formats (Abstract, Graphic, PLS = plain
# language summary, Video) x 3 versions (N, R, S), 26-61 respondents each. It
# ships as the deposit's own label rather than as `treat`, because there is no
# control arm to code 0 against -- all twelve arms are summary formats, and
# the paper's comparison is between them. Same reasoning that kept the arm
# out of lin_2026_advertising_literacy, reached differently because here the
# labels are self-describing.
#
# THE SCORED COMPREHENSION COLUMNS ARE UNNAMED, AND THE DEPOSIT'S OWN TOTALS
# PROVE WHICH THEY ARE. Each paper's block is a topic question plus five
# true/false statements, scored 0/1 into six columns pandas calls
# "Unnamed: 31, 33-37" (Cohn) and "Unnamed: 47, 49-53" (Takata). Summing each
# six reproduces the deposit's own Total-Cohn on 538 of 538 rows and
# Total-Takata on all 446 rows that have a complete Takata block. So the
# identification is proven, not guessed, and both sums are asserted below.
#
# 92 RESPONDENTS HAVE NO TAKATA BLOCK AT ALL, and this is ATTRITION, not a
# planned design: the second paper was the second half of the survey and the
# dropouts are uneven within format (every "-S" arm is complete, every "-N"
# and "-R" arm loses 8-16 people). So the Takata tables carry 446 ids against
# the Cohn tables' 538, and that difference is informative rather than random.
# Stated in the descriptions.
#
# TWO OF THE SEVEN TABLES CARRY 201 ids, NOT 538, AND THAT IS ROUTING RATHER
# THAN MISSINGNESS. The nine "where do you get research updates" items were
# shown to research scientists only: all 201 of them answered, and of the 337
# non-scientists exactly one has a partial row. Asserted below, and distinct
# from the Takata attrition above, which is real dropout.
#
# A TEXT-ONLY BATTERY IS RECOVERED FROM A LEARNED MAPPING. The deposit stores
# the first preference battery TWICE -- once as words ("Highest Preference",
# "Slightly Prefer", "Average", "A bit", "Not at all") and once as 0-4 -- but
# the second battery, nine items on where people get research updates, only as
# words. The five labels map one-to-one onto 0-4 in the twinned columns, with
# no label ever taking two numbers, so the mapping is learned from the
# deposit's own twins and applied to the untwinned battery. The script asserts
# the bijection before using it. Nothing is invented: the numbers come from
# the authors' own coding of the same five words.
#
# `cov_career` IS LABELLED BUT COLLAPSES TWO CATEGORIES, which is the sort of
# thing a bare code hides. Cross-tabulating the deposit's text column against
# its numeric one: 1 = research scientist (201), 3 = adult in a
# science-related career (156), and 2 = BOTH "adult in a non-science career"
# (134) AND "undergraduate student" (47). So code 2 is "not a scientist",
# 181 people of two quite different kinds. Said in the description.
#
# TWO COLUMNS WITH FREE TEXT ARE NOT SHIPPED IN ANY FORM: the self-described
# gender field (34 distinct self-descriptions) and the free-text comments.
# The deposit also holds a 0/1 recoding of gender by the authors, whose rule
# is not stated anywhere, so that is dropped too rather than shipped with an
# unknown direction.
#
# ALSO DROPPED: two standalone attitude items ("I enjoy learning about new
# scientific research", "I generally find research papers easy to
# understand"), each on its own 1-5 scale with no companion -- two items do
# not make a table and they measure different things.
#
# Item text: SHIPPED for five of the seven tables, read off the column
# headers. NOT for the two comprehension tables: the deposit stores the five
# true/false statements only as a concatenated free-text "check all that
# apply" answer, so no statement can be tied to a particular scored column.
#
# PII: screened. The free-text columns are dropped unexamined beyond
# confirming what they are; no names, emails or dates ship.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("BREDBENNER_RAW", "journal.pone.0224697_S7_File.xlsx")

N_ROWS = 538
PREF_LABELS = {"Not at all": 0, "A bit": 1, "Average": 2,
               "Slightly Prefer": 3, "Highest Preference": 4}
# positional, because the deposit gives these columns no usable names
COHN = [31, 33, 34, 35, 36, 37]
TAKATA = [47, 49, 50, 51, 52, 53]
PREF_TWINS = [(8, 9), (10, 11), (12, 13), (14, 15), (16, 17)]
PREF_NUM = ["Video", "Graphic", "Research Paper", "Audio", "Written"]
UPDATES = list(range(19, 28))      # 4 "outside your field" then 5 "in"
REACT = {"cohn": ["Enjoy-Cohn", "Understand-Cohn", "Updates-Cohn"],
         "takata": ["Enjoy-Takata", "Understand-Takata", "Updates-Takata"]}


def learn_label_map(df, c):
    """The deposit codes the same five words as 0-4 in its twinned columns."""
    seen = {}
    for t, n in PREF_TWINS:
        for a, b in zip(df[c[t]], df[c[n]]):
            if pd.notna(a) and pd.notna(b):
                seen.setdefault(str(a).strip(), set()).add(int(b))
    assert all(len(v) == 1 for v in seen.values()), (
        f"a preference label takes more than one number: "
        f"{ {k: sorted(v) for k, v in seen.items() if len(v) > 1} }")
    got = {k: v.pop() for k, v in seen.items()}
    assert got == PREF_LABELS, f"the learned label map is {got}"
    print(f"learned the deposit's own label->number map from its twinned "
          f"columns, a clean bijection: {PREF_LABELS}")
    return got


def convert():
    df = pd.read_excel(RAW, sheet_name="Sheet1")
    assert len(df) == N_ROWS, len(df)
    c = list(df.columns)
    label_map = learn_label_map(df, c)

    # the unnamed scored columns, proven by the deposit's own totals
    for name, idx, total in (("Cohn", COHN, "Total-Cohn"),
                             ("Takata", TAKATA, "Total-Takata")):
        cols = [c[i] for i in idx]
        complete = df[cols].notna().all(axis=1)
        assert (df.loc[complete, cols].sum(axis=1) ==
                df.loc[complete, total]).all(), (
            f"summing {name}'s six unnamed columns no longer reproduces "
            f"{total}; the whole identification of those columns rests on "
            f"it, so stop")
        vals = df[cols].stack().dropna()
        assert set(vals.unique()) == {0, 1}, (name, sorted(vals.unique()))
        print(f"{name}: six unnamed 0/1 columns sum to {total} on all "
              f"{int(complete.sum())} complete rows -- identification proven")

    career = df[c[4]]
    assert sorted(career.dropna().unique()) == [1, 2, 3], \
        sorted(career.dropna().unique())
    print("cov_career: 1 research scientist, 3 adult in a science-related "
          "career, 2 BOTH adult in a non-science career AND undergraduate "
          "student -- the deposit's code collapses two labels into one")

    # the nine "research updates" items were ROUTED, not dropped: every one
    # of the 201 research scientists answered them and essentially nobody
    # else did (one non-scientist has a partial row). So those two tables
    # carry 201 ids against 538, by design of the questionnaire rather than
    # by attrition -- a different thing from the Takata dropout below.
    upd = df[[c[i] for i in UPDATES]].notna().any(axis=1)
    assert int(upd.sum()) == 202 and int((upd & (career == 1)).sum()) == 201, (
        f"the updates battery was answered by {int(upd.sum())} people, "
        f"{int((upd & (career == 1)).sum())} of them research scientists -- "
        f"the routing this script documents has changed")
    print("the nine 'research updates' items were routed to research "
          "scientists only: 201 of 201 answered, plus one non-scientist with "
          "a partial row. Those two tables carry 201 ids by design")

    base = pd.DataFrame({
        "id": df[c[0]].astype(str),
        "cov_condition": df["Survey"].astype(str),
        "cov_career": career,
    })
    assert base["id"].nunique() == N_ROWS, "the id is not unique"
    assert df["Survey"].nunique() == 12, df["Survey"].nunique()

    def emit(name, cols, codes, lo, hi, label, numeric=True):
        sub = base.copy()
        for col, code in zip(cols, codes):
            v = df[col]
            if not numeric:
                v = v.map(lambda x: label_map.get(str(x).strip())
                          if pd.notna(x) else None)
            sub[code] = pd.to_numeric(v, errors="coerce")
        long = sub.melt(id_vars=["id", "cov_condition", "cov_career"],
                        value_vars=codes, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(lo, hi).all(), \
            (name, sorted(long["resp"].unique()))
        assert long["item"].nunique() == len(codes)
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name
        long = long[["id", "item", "resp", "cov_condition", "cov_career"]]

        checks = run_qc(long, permitted_values={i: list(range(lo, hi + 1))
                                                for i in codes})
        fails = [(x.name, x.detail) for x in checks if x.status == "fail"]
        assert not fails, (name, fails)
        for x in checks:
            if x.status == "warn":
                print(f"  [qc warn] {name} {x.name}: {x.detail[:135]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}  [{label}]")
        return len(long)

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    total += emit("bredbenner_2019_format_preference", PREF_NUM,
                  [re.sub(r"\W+", "_", p.lower()) for p in PREF_NUM], 0, 4,
                  "Preference for five ways of getting new scientific "
                  "information")
    total += emit("bredbenner_2019_updates_outside_field",
                  [c[i] for i in UPDATES[:4]],
                  [f"OUT{i}" for i in range(1, 5)], 0, 4,
                  "Preference for ways of getting research updates OUTSIDE "
                  "one's field", numeric=False)
    total += emit("bredbenner_2019_updates_in_field",
                  [c[i] for i in UPDATES[4:]],
                  [f"IN{i}" for i in range(1, 6)], 0, 4,
                  "Preference for ways of getting research updates IN one's "
                  "field", numeric=False)
    total += emit("bredbenner_2019_comprehension_cohn",
                  [c[i] for i in COHN], [f"COHN{i}" for i in range(1, 7)],
                  0, 1, "Comprehension of the Cohn et al. paper, 6 scored "
                        "true/false items")
    total += emit("bredbenner_2019_comprehension_takata",
                  [c[i] for i in TAKATA], [f"TAKATA{i}" for i in range(1, 7)],
                  0, 1, "Comprehension of the Takata et al. paper, 6 scored "
                        "true/false items")
    total += emit("bredbenner_2019_reactions_cohn", REACT["cohn"],
                  ["enjoy", "understand", "want_updates"], 0, 4,
                  "Reactions to the Cohn summary (enjoyment, understanding, "
                  "wanting more updates)")
    total += emit("bredbenner_2019_reactions_takata", REACT["takata"],
                  ["enjoy", "understand", "want_updates"], 0, 4,
                  "Reactions to the Takata summary")
    print(f"7 tables, {total} responses across {N_ROWS} respondents in 12 "
          f"randomised conditions")


if __name__ == "__main__":
    convert()
