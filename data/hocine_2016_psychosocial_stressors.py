#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0157078
# DOI: 10.1371/journal.pone.0157078
# Paper: Hocine, M. N., Ait Bouziad, K., Legeron, P., Dab, W., & Saporta, G.
#   (2016). How to Identify and Prioritize Psychosocial Factors Impacting
#   Stress Level. PLOS ONE 11(6): e0157078.
# Data: figshare 10.6084/m9.figshare.3156154 -- Database.xlsx, one sheet
#   'Data_corr', 10,000 rows x 61 columns.
#   (md5 of the downloaded file is not pinned here because figshare serves the
#   same single file at https://ndownloader.figshare.com/files/4916737.)
#
# LICENCE -- verified on the DEPOSIT, not on the article. The article is CC BY
# 4.0, but the data is not a Supporting Information file: the Data Availability
# statement points off-site to figshare, and a figshare deposit carries its own
# licence that an article's cannot grant. Checked via
# api.figshare.com/v2/articles/3156154, which reports
# {"value": 1, "name": "CC BY 4.0", "url": ".../licenses/by/4.0/"}. Both layers
# are CC BY 4.0, so this one agrees -- but it had to be asked.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md);
# the largest `good` lead of that run by response count.
#
# ONE output table: the 58-item psychosocial stressors questionnaire.
#
# THE SAMPLE IS REAL, which was worth confirming before anything else -- a
# dataset of exactly 10,000 rows with no missing cells at all looks synthetic.
# It is not. The paper: "A sample of 10 000 employees was drawn according to a
# simple random sampling scheme from hundred thousands of individual's data,
# collected between 2011 and 2012", from French employees surveyed during a
# routine interview with their occupational physician. The roundness is the
# sampling design, not simulation. (The paper then splits those 10,000 into
# 5,000 for fitting and 5,000 for validation; both halves are in this file and
# the file carries no column marking the split, so the table is the 10,000.)
#
# resp = 0 IS A REAL ANCHOR HERE, unlike three of the five deposits in the
# 2026-10-29f batch, and the paper says so outright: "Participants give their
# degree of agreement with each of the 58 items on a 6-points Likert scale,
# ranging from 0 (strongly disagree) to 5 (strongly agree)." Three independent
# checks in the data agree and are asserted below: the observed domain is
# exactly {0,1,2,3,4,5} across all 58 items, every one of the 58 items has all
# six values present, and the file has ZERO missing cells -- so 0 cannot be
# this export's no-answer code, because there is no nonresponse to encode.
#
# ONE table, not five. The 58 items are grouped into five blocks associated
# with latent variables (work context, job control, relationships at work, type
# of performed tasks, recognition), but they are one instrument administered on
# one 0-5 agreement scale, so they ship as one table per the
# collapse-same-instrument rule. The column names (nsp01..nsp58) do not encode
# the blocks and the paper's block membership is given in a DOCX table, so no
# itemcov_ column for block is written rather than one being guessed at.
#
# Item text: NOT shipped. The wording of all 58 items is in the deposit's
# companion S2 Table (DOCX, "Psychosocial factor measurements"), so the text is
# in hand -- but the instrument is not the authors'. The paper attributes it to
# Stimulus, a French occupational-health consultancy: "In order to measure
# psychosocial risk factors at work, Stimulus has developed a 58-item
# questionnaire". A CC BY article does not relicense a third party's
# proprietary instrument reproduced inside it, and the questionnaire is
# Stimulus's commercial product. Register row written with this batch, verdict
# hold. Administered in French; `language` is French for the response table.
#
# PII: screened over every column. The file holds only ID (a sequential record
# number), gender, the 58 item columns and compagny -- no names, emails, dates,
# free text, or geography. ID is unique per row and is used as `id`.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("HOCINE_RAW", "Database.xlsx")

TABLE = "hocine_2016_psychosocial_stressors"
ITEMS = [f"nsp{i:02d}" for i in range(1, 59)]
COVS = {"gender": "cov_gender", "compagny": "cov_company"}
DROP = {"ID": "sequential record number -- becomes id"}

LO, HI = 0, 5

PII_PAT = (r"[\w.+-]+@[\w-]+\.[a-z]{2,}"
           r"|\+?\d{9,}"
           r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")


def screen_for_pii(df):
    """Report the denominator so a zero is visible rather than silent. This
    file is entirely numeric, so the text-column selector legitimately finds
    nothing -- which is itself the finding, and is asserted as such instead of
    being allowed to look like a screen that ran and passed."""
    txt = [c for c in df.columns
           if pd.api.types.is_string_dtype(df[c])
           and pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    if txt:
        hits = [(c, v) for c in txt
                for v in df[c].dropna().astype(str).unique()
                if pd.Series([v]).str.contains(PII_PAT, regex=True,
                                               case=False).any()]
        assert not hits, f"PII screen hit: {hits[:5]}"
    else:
        # every column parses as a number: no free text exists to screen
        assert all(pd.to_numeric(df[c], errors="coerce").notna().all()
                   for c in df.columns), "a non-numeric column escaped the screen"
        print("  all 61 columns parse as numbers -- there is no free text, "
              "name, email, date or geography column in this file at all")
    print("PII screen: clean")


def convert():
    df = pd.read_excel(RAW, sheet_name="Data_corr")
    screen_for_pii(df)

    accounted = set(ITEMS) | set(COVS) | set(DROP)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    assert len(ITEMS) == 58

    # the paper states 0 (strongly disagree) .. 5 (strongly agree); these three
    # checks are what make that a verified anchor rather than a trusted caption
    domain = set()
    for c in ITEMS:
        domain |= set(df[c].dropna().unique().tolist())
    assert domain == set(range(LO, HI + 1)), sorted(domain)
    assert all(df[c].nunique() == HI - LO + 1 for c in ITEMS), \
        "an item is missing one of the six documented levels"
    assert int(df[ITEMS].isna().sum().sum()) == 0, "unexpected missing cells"
    zero = float((df[ITEMS] == 0).sum().sum()) / (len(df) * len(ITEMS))
    print(f"resp domain is exactly {sorted(domain)} on all 58 items, all six "
          f"levels present on every item, zero missing cells; "
          f"resp=0 is {zero:.1%} of responses and is the documented "
          f"'strongly disagree' anchor")

    assert df["ID"].nunique() == len(df), "ID is not unique"
    df = df.rename(columns={"ID": "id", **COVS})
    cov_cols = sorted(COVS.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                   var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(int)

    assert long["resp"].between(LO, HI).all(), long["resp"].unique()
    assert long["id"].nunique() >= 100, long["id"].nunique()
    assert long["item"].nunique() == 58, long["item"].nunique()
    assert not long.duplicated(["id", "item"]).any()
    assert len(long) == 10000 * 58, len(long)

    long = long[["id", "item", "resp"] + cov_cols]

    # gate before writing -- the contract check requires the validator to run
    # in-script, not just on the output file
    checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                            for i in ITEMS})
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
