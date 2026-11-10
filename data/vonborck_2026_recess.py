#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0361479
# DOI: 10.1371/journal.pone.0361479
# Paper: von Borck HG, Esposito P, Braun-Trocchio R, Wagner LM, Rhea DJ (2026).
#   Comparing the impact of recess duration on motor coordination and
#   psychological variables: An exploratory study. PLOS ONE.
# Data: S1 File (XLSX, "Data Information"), 218 rows x 61 columns, attached to
#   the article itself.
# License: CC BY 4.0 (the article's licence covers its SI file).
#
# Found by the PLOS monthly run of 2026-11-09 (leads/plos_leads_2026-11-09.csv,
# step-2b recoverable_format).
#
# TWO output tables, each with two waves (Time 1 = September, Time 2 =
# February of the 2024-25 school year), 218 fourth/fifth graders:
#   vonborck_2026_kidkindl_selfesteem -- KID-KINDL self-esteem subscale,
#       4 items, "5-point Likert scale ranging from 1 (never) to 5 (all of the
#       time), with no items reversed" (paper, 2.2.3).
#   vonborck_2026_ppasc -- Perceived Physical Ability Scale for Children,
#       6 items, "4-point Likert scale ranging from 1 ... to 4" (paper, 2.2.3).
#       The deposit calls this block SEE_; the paper calls it PPASC. Items
#       Q2R/Q4R/Q6R carry the deposit's R suffix (reverse-keyed in the source);
#       they are shipped as deposited, not recoded.
# Item codes are the deposit's own headers with the PRE_/POST_ wave prefix
# stripped (PRE_SES_Q3 -> SES_Q3 at wave 1).
#
# DROPPED, not items: KTK motor-coordination subtest scores (RAWWB etc. are
# trial sums, MQ* are norm-converted quotients), body-fat (BIA), the
# SES_SUM / SEE_TOTAL composites, and the MQ classification columns.
#
# SOURCE DEFECT -- WAVE 1 FOR 46 CHILDREN IS EXCLUDED. For the last 46 rows of
# the file (IDs D253-D298, all but one in the control district), the Time 1
# block is shifted: PRE_SES_Q1 equals SEX and PRE_SES_Q2 equals the race code
# (RCE) in 41 of those 46 rows, against 1 of the first 172 rows (chance).
# The same rows carry every out-of-range Time 1 value in the file (PRE_SES_Q3
# = 0 or 6; PPASC = 5 on a 4-point scale) and most rows whose items do not
# sum to the deposit's own PRE_SES_SUM / PRE_SEE_TOTAL. The true Time 1
# answers for those children cannot be recovered, so their Time 1 rows are
# dropped for BOTH scales; their Time 2 rows are clean (POST sums match the
# deposit's totals in all 218 rows) and ship. Every other row ships both waves.
#
# Design columns: `treat` = 1 for the modified LiiNK recess intervention
#   (GROUD 1, District 1, n=120), 0 for the control district (GROUD 2, n=98).
#   NON-RANDOMISED: "group membership was determined by the district and school
#   recess practices already in place" (2.1.1).
# Covariates: cov_sex (SEX, 1/2), cov_grade (GRCN, 4/5), cov_race (RCE, codes
#   1-5). The deposit ships no codebook, so the sex and race codes are not
#   labelled; they are carried as the source's numeric codes.
# `id`: the deposit's IDs are strings (D11...); replaced by the row index per
#   datastandard step 2. Verified unique (218/218) first.
#
# Imputation: the article text has no imputation language ("imput", "MICE",
#   "mean substitution" all absent); every shipped value is an integer.
#
# Item text: not shipped -- no labels in the XLSX (headers are codes) and no
#   questionnaire in the SI. The KID-KINDL self-esteem items are in the
#   published KINDL-R manual (Ravens-Sieberer & Bullinger); the 6-item PPASC
#   revision is in Colella et al. 2008 (paper ref 19). Neither has a row in
#   itemtext/instrument_rights_register.csv.
#
# PII: screened over all 61 columns; the only string column is the ID
#   (D-prefixed study codes), which is not shipped.

import os
import re
import socket
import sys
import tempfile

import pandas as pd
import requests
import urllib3.util.connection as _uc

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = ("https://journals.plos.org/plosone/article/file?type=supplementary"
       "&id=10.1371/journal.pone.0361479.s001")
RAW = os.environ.get("VONBORCK_RAW", "")

N_ROWS = 218
SCALES = {
    "SES": ("vonborck_2026_kidkindl_selfesteem", ["SES_Q1", "SES_Q2", "SES_Q3", "SES_Q4"], 1, 5),
    "SEE": ("vonborck_2026_ppasc",
            ["SEE_Q1", "SEE_Q2R", "SEE_Q3", "SEE_Q4R", "SEE_Q5", "SEE_Q6R"], 1, 4),
}
COVS = {"SEX": "cov_sex", "GRCN": "cov_grade", "RCE": "cov_race"}


def fetch():
    if RAW:
        return RAW
    _uc.allowed_gai_family = lambda: socket.AF_INET  # IPv6 stalls here
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=120)
    r.raise_for_status()
    path = os.path.join(tempfile.mkdtemp(), "vonborck_s1.xlsx")
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


def screen_for_pii(df):
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])
               or df[c].dtype == object]
    print(f"PII screen: {len(df.columns)} columns examined, {len(strings)} "
          f"string column(s): {strings}")
    assert len(df.columns) > 0
    assert strings == ["ID"], strings
    assert df["ID"].astype(str).str.fullmatch(r"D\d+").all()


def convert():
    df = pd.read_excel(fetch(), sheet_name=0)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)
    assert df["ID"].nunique() == N_ROWS

    # locate the shifted Time 1 block and check it is what the header says
    shifted = (df["PRE_SES_Q1"] == df["SEX"]) & (df["PRE_SES_Q2"] == df["RCE"])
    idnum = df["ID"].str[1:].astype(int)
    bad_t1 = idnum.between(253, 298)
    assert bad_t1.sum() == 46
    assert shifted[bad_t1].sum() == 41 and shifted[~bad_t1].sum() == 1, \
        (shifted[bad_t1].sum(), shifted[~bad_t1].sum())
    print(f"Time 1 excluded for {bad_t1.sum()} children (D253-D298): shifted "
          f"columns in {shifted[bad_t1].sum()} of them")

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df["treat"] = (df["GROUD"] == 1).astype(int)
    assert set(df["GROUD"]) == {1, 2} and df["treat"].sum() == 120
    df = df.rename(columns=COVS)
    cov_cols = list(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    names = set()
    for key, (name, items, lo, hi) in SCALES.items():
        assert name not in names and len(name) <= 40
        names.add(name)
        parts = []
        for wave, prefix in ((1, "PRE_"), (2, "POST_")):
            src = [prefix + i for i in items]
            sub = df if wave == 2 else df[~bad_t1]
            w = sub[["id", "treat"] + cov_cols + src].rename(
                columns=dict(zip(src, items)))
            long = w.melt(id_vars=["id", "treat"] + cov_cols, value_vars=items,
                          var_name="item", value_name="resp")
            long["wave"] = wave
            parts.append(long)
        # every source column of this scale is either shipped or a composite
        src_all = [c for c in df.columns if re.match(rf"(PRE|POST)_{key}_", c)]
        comp = [c for c in src_all if c.endswith(("_SUM", "_TOTAL"))]
        assert len(src_all) == 2 * len(items) + len(comp) and len(comp) == 2, src_all
        long = pd.concat(parts, ignore_index=True)
        long["resp"] = pd.to_numeric(long["resp"], errors="raise")
        assert long["resp"].notna().all()
        assert (long["resp"] % 1 == 0).all()
        assert long["resp"].between(lo, hi).all(), \
            (name, sorted(long["resp"].unique()))
        long["resp"] = long["resp"].astype(int)
        assert not long.duplicated(["id", "item", "wave"]).any()
        long = long[["id", "item", "resp", "wave", "treat"] + cov_cols]

        checks = run_qc(long, permitted_values=list(range(lo, hi + 1)))
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-"
              f"{long['resp'].max()} waves={sorted(long['wave'].unique())}")


if __name__ == "__main__":
    convert()
