#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0323407
# DOI: 10.1371/journal.pone.0323407
# Paper: Zhao, W., et al. (2025). Exploring the influence of social media use
#   motivations on acculturation orientations and psychological adaptation
#   among Chinese students in Malaysia. PLOS ONE 20(5).
# Data: figshare 10.6084/m9.figshare.28379111 -- one .xlsx, 438 rows x 47
#   columns.
#
# LICENCE verified on the DEPOSIT, not the article: the data is hosted
# off-site on figshare, so the article's licence cannot grant it.
# api.figshare.com/v2/articles/28379111 reports CC BY 4.0.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# SEVEN output tables, 41 items, all on the paper's "five-point Likert scale
# ranging from 'strongly disagree (1)' to 'strongly agree (5)'". Zero missing
# cells. 438 Chinese international students in Malaysia.
#
# SIX CONSTRUCTS ARE NAMED BY THE PAPER AND ONE IS NOT, which is stated rather
# than guessed. The abstract names "social media use motivations (information
# seeking, social, and entertainment motivations)", "acculturation orientations
# (Malaysian and Chinese cultural orientations)" and "psychological
# adaptation" -- six constructs, matching six of the deposit's prefixes. The
# seventh block, EA (6 items), is NOT identified anywhere in the article's
# readable text: its Table 1 "provides a comprehensive list of all measurement
# items" but is published only as an IMAGE, and the running text never names a
# seventh scale. So EA ships with its construct recorded as unidentified. The
# alternative -- guessing from the initials (English Ability? Environmental
# Adaptation?) -- would put an invented construct name in the dictionary, and
# a wrong label is worse than an honest blank.
#
# `id` is the deposit's serial column, whose header is the Chinese for "serial
# number"; verified unique across all 438 rows.
#
# Covariates: gender, marital status, age, education and length of stay in
# Malaysia (the paper reports a mean stay of 14.58 months).
#
# Item text: NOT SHIPPED. The wording exists -- Table 1 lists every item with
# its literature source -- but it is an image in the HTML, and the items are
# "adapted from previous research" per-construct rather than study-authored,
# so the rights question would have to be answered source by source. No
# register row: this is the same adapted-from-the-literature shape already
# recorded for the UTAUT/TAM family in this batch, and the TODO item asking
# for a general ruling covers the pattern.
#
# PII: screened over all 47 columns. Every one is numeric; no names, emails,
# dates, free text or geography.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ZHAO_SM_RAW", "data_social_media.xlsx")

N_ROWS = 438
LO, HI = 1, 5

CONSTRUCTS = {
    "ISM": ("zhao_2025_sm_information_motivation", 3,
            "Information seeking motivation for social media use"),
    "SM": ("zhao_2025_sm_social_motivation", 4,
           "Social motivation for social media use"),
    "EM": ("zhao_2025_sm_entertainment_motivation", 4,
           "Entertainment motivation for social media use"),
    "CCO": ("zhao_2025_chinese_orientation", 8,
            "Chinese cultural orientation (heritage acculturation)"),
    "MCO": ("zhao_2025_malaysian_orientation", 8,
            "Malaysian cultural orientation (mainstream acculturation)"),
    "PA": ("zhao_2025_psychological_adaptation", 8,
           "Psychological adaptation"),
    "EA": ("zhao_2025_ea_unidentified", 6,
           "CONSTRUCT NOT IDENTIFIED -- see the script header"),
}
COVS = {"gender": "cov_gender", "marrage": "cov_marital_status",
        "age": "cov_age", "education": "cov_education",
        "length": "cov_months_in_malaysia"}


def screen_for_pii(df):
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(strings)} string column(s) of {len(df.columns)}: "
          f"{strings}")
    assert not strings, f"unexpected string column(s): {strings}"
    print("  every column is numeric; no name, email, date, free text or "
          "geographic column in this file")


def convert():
    df = pd.read_excel(RAW, sheet_name=0)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    found = {}
    for c in df.columns:
        m = re.fullmatch(r"([A-Z]+)(\d+)", str(c).strip())
        if m and m.group(1) in CONSTRUCTS:
            found.setdefault(m.group(1), []).append(c)
    got = {k: len(v) for k, v in found.items()}
    want = {k: v[1] for k, v in CONSTRUCTS.items()}
    assert got == want, f"construct counts are {got}, expected {want}"

    id_col = [c for c in df.columns
              if c not in COVS and not re.fullmatch(r"[A-Z]+\d+", str(c).strip())]
    assert len(id_col) == 1, f"expected one serial column, found {id_col}"
    assert df[id_col[0]].nunique() == len(df), "the serial column is not unique"
    print(f"id column is the deposit's serial column (header is the Chinese "
          f"for 'serial number'), unique across all {N_ROWS} rows")

    df = df.rename(columns={id_col[0]: "id", **COVS})
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, (name, n, label) in CONSTRUCTS.items():
        cols = sorted(found[prefix], key=lambda c: int(re.sub(r"\D", "", str(c))))
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        stacked = df[cols].stack().dropna()
        assert pd.to_numeric(stacked, errors="coerce").notna().all(), \
            (name, "non-numeric item value")
        vals = pd.to_numeric(stacked)
        assert vals.between(LO, HI).all(), (name, sorted(vals.unique()))

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name
        long = long[["id", "item", "resp"] + cov_cols]

        # gate before writing -- the contract check requires the validator to
        # run in-script, not just on the output file
        checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                                for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:135]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}  [{label}]")

    assert total == 41 * N_ROWS, total
    print(f"7 tables, {total} responses (41 items x {N_ROWS} respondents, "
          f"no missing cells)")


if __name__ == "__main__":
    convert()
