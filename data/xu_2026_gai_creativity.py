#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0358186
# DOI: 10.1371/journal.pone.0358186
# Paper: Xu, J., & Zeng, Y. (2026). How Generative Artificial Intelligence
#   (GAI) reshapes students' creativity in higher education: a chain path
#   modeling study from "Exploration-Exploitation" to "Co-Creation-
#   Reflection". PLOS ONE 21(9): e0358186.
# Data: journal.pone.0358186.s001 (S1 File, .xlsx), 424 rows x 49 columns.
# License: CC BY 4.0 -- Supporting Information of the article itself, so the
#   article's licence reaches it; no off-site deposit.
# 424 undergraduate, master's and doctoral students at Chinese universities
# with GAI experience, surveyed online April-June 2025.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# EIGHT output tables, 40 items (Q5..Q44), 16,960 responses, zero missing
# cells. Five-point Likert, 1 "Strongly Disagree" to 5 "Strongly Agree".
#
# THE BLOCK STRUCTURE IS EXPLICIT, NOT INFERRED. Appendix A of S3 File prints
# all 44 questionnaire items in a table keyed BY Q-CODE, each under its
# construct heading and with its literature source. So Q5..Q9 are Exploration,
# Q10..Q14 Exploitation, and so on in blocks of five -- stated by the authors
# against the same codes the data uses, with no positional step anywhere.
#
# AND THE DATA CONFIRMS IT INDEPENDENTLY, which matters here more than usual
# (see the covariate problem below). Each five-item block's Cronbach alpha,
# computed from the deposit, lands on the paper's reported composite
# reliability for the constructs the text names:
#     Exploration      alpha 0.874   paper CR 0.874
#     Self-efficacy    alpha 0.870   paper CR 0.874
#     Flow             alpha 0.873   paper CR 0.871
#     Co-Creation      alpha 0.858   paper CR 0.857
# and all eight fall inside the paper's stated CR range 0.850-0.874. The
# highest inter-construct correlation is Exploration-Exploitation at 0.502,
# matching the paper's "Exploration's highest correlation is with
# Exploitation" (0.575 latent, so 0.502 observed is what attenuation predicts).
# These are asserted below. The item data IS the analysed data.
#
# EVERY DEMOGRAPHIC COLUMN IS DROPPED, AND NOT FOR THE USUAL REASON. They are
# not opaque -- Appendix A names them exactly (Q1 gender, Q2 student level,
# Q3 duration of GAI use, Q4 a five-box "commonly used GAI tools" multi-select
# in the order ChatGPT / Wenxin Yiyan / Deepseek / Doubao / Other). The problem
# is that NONE of the four published distributions reproduces in the file:
#     gender      paper 218 male, 206 female      file 242 / 181 / 1
#     level       paper 102 / 163 / 159           file  62 / 174 / 188
#     duration    paper 21 / 16 / 178 / 162 / 47  file  21 /  48 / 119 / 162 / 74
#     tools       paper 367 / 287 / 212 / 203     file 336 / 323 / 291 / 153 / 2
# Each set sums to 424 and the item data checks out, so this is not a different
# sample -- but whatever the demographic columns of this export are, they are
# not the demographics the paper describes, and nothing here says which is
# right. A covariate that contradicts its own paper is worse than no covariate,
# so all eight demographic columns are dropped and the discrepancy is recorded
# rather than quietly resolved in the file's favour. The checks below assert
# the mismatch, so if a corrected S1 File is ever deposited the script fails
# loudly and the covariates can be reconsidered.
#
# `id` is the deposit's `Code`, 1..424, verified unique.
#
# Item text: SHIPPED, all 40 items, from Appendix A of S3 File. See
# xu_2026_gai_itemtext.py. The mapping is code-level and explicit, which is
# rare in this batch -- the appendix labels each wording with the same Q-number
# the data column carries, so there is no within-block ordering assumption at
# all.
#
# PII: screened over all 49 columns. Every one is numeric; no names, emails,
# dates, free text or geography.

import os
import sys

import numpy
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("XU_RAW", "journal.pone.0358186_S1_File.xlsx")

N_ROWS = 424
LO, HI = 1, 5

# (first Q, last Q, table name, construct label) -- blocks of five, from
# Appendix A of S3 File, keyed by the same codes the data uses
BLOCKS = [
    (5, 9, "xu_2026_gai_exploration", "Exploration"),
    (10, 14, "xu_2026_gai_exploitation", "Exploitation"),
    (15, 19, "xu_2026_gai_cocreation", "Co-Creation"),
    (20, 24, "xu_2026_gai_reflection", "Reflection"),
    (25, 29, "xu_2026_gai_cognitive_stimulation",
     "Perceived Cognitive Stimulation"),
    (30, 34, "xu_2026_gai_flow", "Flow Experience"),
    (35, 39, "xu_2026_gai_creative_self_efficacy",
     "Self-efficacy in Creativity"),
    (40, 44, "xu_2026_gai_student_creativity", "Student Creativity"),
]

# the paper's reported composite reliabilities, for the four constructs its
# TEXT names (the rest are in an image-only table)
PAPER_CR = {"xu_2026_gai_exploration": 0.874,
            "xu_2026_gai_creative_self_efficacy": 0.874,
            "xu_2026_gai_flow": 0.871,
            "xu_2026_gai_cocreation": 0.857}
CR_RANGE = (0.850, 0.874)

# what the paper says the demographics look like, against what the file holds
PAPER_DEMOGRAPHICS = {
    "Q1": [218, 206],                 # gender: male, female
    "Q2": [102, 163, 159],            # undergraduate, master's, doctoral
    "Q3": [21, 16, 178, 162, 47],     # duration bands
}
PAPER_TOOLS = [367, 287, 212, 203]    # ChatGPT, Deepseek, Ernie Bot, Doubao
DEMOGRAPHIC_COLS = ["Q1", "Q2", "Q3"] + [f"Q4_Choice{i}" for i in range(1, 6)]


def screen_for_pii(df):
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(strings)} string column(s) of {len(df.columns)}")
    assert not strings, f"unexpected string column(s) -- screen them: {strings}"
    print("  every column is numeric; no name, email, date, free text or "
          "geographic column in this file")


def cronbach_alpha(X):
    k = X.shape[1]
    return k / (k - 1) * (1 - X.var(ddof=1).sum() / X.sum(axis=1).var(ddof=1))


def check_demographics(df):
    """Assert the MISMATCH -- see the header. If a corrected S1 File is ever
    deposited this fails, and the covariates can be reconsidered."""
    for col, counts in PAPER_DEMOGRAPHICS.items():
        got = df[col].value_counts().sort_index().tolist()
        assert got != counts, (
            f"{col} now reproduces the paper's published distribution "
            f"({counts}); the header says it does not, so the covariates "
            f"should be reconsidered rather than dropped")
        print(f"  {col}: file {got} vs paper {counts} -- does not reproduce")
    tools = [int(df[f"Q4_Choice{i}"].sum()) for i in range(1, 6)]
    assert tools[:4] != PAPER_TOOLS, "the tool counts now reproduce; recheck"
    print(f"  Q4_Choice1-5: file {tools} vs paper {PAPER_TOOLS} (+ no 'Other' "
          f"count published) -- does not reproduce")
    print(f"dropped all {len(DEMOGRAPHIC_COLS)} demographic columns: they are "
          f"NAMED in Appendix A, not opaque, but not one of the four published "
          f"distributions reproduces in this file")


def convert():
    df = pd.read_excel(RAW)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)
    check_demographics(df)

    accounted = {"Code"} | set(DEMOGRAPHIC_COLS)
    for a, b, *_ in BLOCKS:
        accounted |= {f"Q{i}" for i in range(a, b + 1)}
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"

    assert df["Code"].nunique() == len(df), "Code is not unique"
    df = df.rename(columns={"Code": "id"})

    # the item data IS the analysed data: each block's alpha reproduces the
    # paper's reported CR
    comps = {}
    for a, b, name, label in BLOCKS:
        cols = [f"Q{i}" for i in range(a, b + 1)]
        alpha = cronbach_alpha(df[cols])
        comps[name] = df[cols].mean(axis=1)
        assert CR_RANGE[0] - 0.01 <= alpha <= CR_RANGE[1] + 0.01, (
            f"{name} alpha {alpha:.3f} is outside the paper's CR range "
            f"{CR_RANGE}")
        if name in PAPER_CR:
            assert abs(alpha - PAPER_CR[name]) < 0.01, (
                f"{name} alpha {alpha:.3f} no longer matches the paper's "
                f"reported CR {PAPER_CR[name]}")
        print(f"  {label:<32} alpha={alpha:.3f}" +
              (f"  (paper CR {PAPER_CR[name]})" if name in PAPER_CR else ""))

    C = pd.DataFrame(comps).corr()
    off = C.mask(pd.DataFrame(numpy.eye(len(C), dtype=bool),
                              index=C.index, columns=C.columns))
    top = off.stack().idxmax()
    assert set(top) == {"xu_2026_gai_exploration", "xu_2026_gai_exploitation"}, (
        f"the highest inter-construct correlation is now {top}, not "
        f"Exploration-Exploitation as the paper reports")
    print(f"  highest inter-construct correlation: Exploration-Exploitation "
          f"r={off.stack().max():.3f} (paper: Exploration's highest is with "
          f"Exploitation, 0.575 latent)")

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for a, b, name, label in BLOCKS:
        cols = [f"Q{i}" for i in range(a, b + 1)]
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all(), (name, "a non-numeric response")
        assert vals.between(LO, HI).all(), (name, sorted(vals.unique()))
        assert (vals % 1 == 0).all(), (name, "a fractional response")

        long = df.melt(id_vars=["id"], value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)

        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == len(cols)
        assert not long.duplicated(["id", "item"]).any()
        assert len(long) == len(cols) * N_ROWS, (name, len(long))
        assert len(name) <= 40, name

        long = long[["id", "item", "resp"]]

        # gate before writing -- the contract check requires the validator to
        # run in-script, not just on the output file
        checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                                for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:145]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}  [{label}]")

    assert total == 40 * N_ROWS, total
    print(f"8 tables, {total} responses (40 items x {N_ROWS} respondents, no "
          f"missing cells, no covariates -- see the header)")


if __name__ == "__main__":
    convert()
