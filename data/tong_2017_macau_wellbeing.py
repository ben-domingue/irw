#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0181616
# DOI: 10.1371/journal.pone.0181616
# Paper: Tong KK, Wang YY (2017). Validation of the flourishing scale and
#   scale of positive and negative experience in a Chinese community sample.
#   PLOS ONE 12(8): e0181616.
# Data: DANS Data Station SSH, doi:10.17026/dans-z4j-vats ("Flourishing Scale
#   and Scale of Positive and Negative Experience (Chinese Community Sample)",
#   K.K. Tong). File "FS (Chinese version).csv" (datafile 181372), 1008 rows x
#   38 columns, ';'-separated with decimal commas. Documentation.pdf (datafile
#   181371) is the codebook.
# License: CC BY 4.0 (DANS record; rights holder University of Macau).
#
# Found by the PLOS monthly run of 2026-11-09 (leads/plos_leads_2026-11-09.csv,
# step-2b recoverable_format: the file is ';'-separated).
#
# THREE output tables, one per instrument, Traditional Chinese versions,
# administered by computer-assisted telephone interview to 1008 Macau
# residents (random-digit household sample, last-birthday rule):
#   tong_2017_swls     Satisfaction With Life Scale, SWLS_1-5, 1-7
#   tong_2017_flourishing  Flourishing Scale, FS_1-8, 1-7
#   tong_2017_spane    Scale of Positive and Negative Experience, 12 items
#                      (SPANE_P_* positive, SPANE_N_* negative), 1-5
# Codebook: SWLS and FS "7-point scale, 1 = strong disagreement, 7 = strong
#   agreement; 8 & 9 = missing"; SPANE "5-point scale, 1 = never, 5 = always;
#   8 & 9 = missing". 8 and 9 are therefore dropped as missing, not shipped.
#   SPANE positive and negative items share one 1-5 scale and are kept in one
#   table as the published instrument; item codes say which subscale.
# Item codes are the deposit headers.
#
# Covariates (Codebook codes, 8/9 = missing set to NA):
#   cov_physical_health (single item, 1 = very unhealthy .. 5 = healthy),
#   cov_social_class (1 = lower .. 5 = upper class; the Codebook omits the
#   "8 & 9 = missing" note for this one, but 22 cells hold 8/9 on a 1-5
#   code, so they are read as missing like every other column),
#   cov_gender (1 = male,
#   2 = female), cov_age (years), cov_marital (1 = single, 2 = married,
#   3 = separated, 4 = divorced, 5 = partner deceased), cov_education
#   (1 = uneducated .. 5 = college and above), cov_employment (1 = full time,
#   2 = part time, 3 = housework, 4 = retired, 5 = student, 6 = unemployed).
# DROPPED (derived): SWLS_MEAN, FS_MEAN, SPANE_P_MEAN, SPANE_N_MEAN,
#   SPANE_B_FROM_SUM, SPANE_B_FROM_MEAN.
# `id`: the deposit has no id column; row index 1-1008.
#
# Imputation: none -- missing answers are coded 8/9, and the deposit's own
#   means are #NULL! for respondents with one (no fill-in).
#
# Item text: not shipped -- headers are positional; the Codebook points to
#   Diener et al. (1985, 2010) for the stems, and the Traditional Chinese
#   wording is not in the deposit.
#
# PII: none -- every column is a coded item, demographic or derived mean.

import os
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
URL = "https://ssh.datastations.nl/api/access/datafile/181372"
RAW = os.environ.get("TONG_FS_RAW", "")
N_ROWS = 1008
MISSING = (8, 9)
SPANE = ["SPANE_P_1", "SPANE_N_2", "SPANE_P_3", "SPANE_N_4", "SPANE_P_5",
         "SPANE_N_6", "SPANE_P_7", "SPANE_N_8", "SPANE_N_9", "SPANE_P_10",
         "SPANE_N_11", "SPANE_P_12"]
TABLES = {
    "tong_2017_swls": ([f"SWLS_{i}" for i in range(1, 6)], 7),
    "tong_2017_flourishing": ([f"FS_{i}" for i in range(1, 9)], 7),
    "tong_2017_spane": (SPANE, 5),
}
COVS = {"Physical_Health": "cov_physical_health",
        "SOCIAL_CLASS": "cov_social_class", "GENDER": "cov_gender",
        "AGE": "cov_age", "MARRIAGE": "cov_marital",
        "EDUCATION": "cov_education", "EMPLOYMENT_STATUS": "cov_employment"}
DROPPED = ["SWLS_MEAN", "FS_MEAN", "SPANE_P_MEAN", "SPANE_N_MEAN",
           "SPANE_B_FROM_SUM", "SPANE_B_FROM_MEAN"]


def fetch():
    if RAW:
        return RAW
    _uc.allowed_gai_family = lambda: socket.AF_INET  # IPv6 stalls here
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=120)
    r.raise_for_status()
    path = os.path.join(tempfile.mkdtemp(), "fs_chinese.csv")
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


def convert():
    df = pd.read_csv(fetch(), sep=";")
    assert df.shape == (N_ROWS, 38), df.shape
    items_all = [c for cols, _ in TABLES.values() for c in cols]
    accounted = set(items_all) | set(COVS) | set(DROPPED)
    assert accounted == set(df.columns), set(df.columns) ^ accounted
    print(f"PII screen: {len(df.columns)} columns examined; all coded "
          f"items/demographics/derived means")

    for c in ["Physical_Health", "SOCIAL_CLASS", "MARRIAGE", "EDUCATION",
              "EMPLOYMENT_STATUS"]:
        df[c] = df[c].where(~df[c].isin(MISSING))
    df["id"] = range(1, N_ROWS + 1)
    df = df.rename(columns=COVS)
    cov_cols = list(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    for name, (cols, hi) in TABLES.items():
        assert df[cols].isin(list(range(1, hi + 1)) + list(MISSING)).all().all()
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        n_missing = int(long["resp"].isin(MISSING).sum())
        long = long[~long["resp"].isin(MISSING)].copy()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values=list(range(1, hi + 1)))
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-"
              f"{long['resp'].max()}; {n_missing} cells coded 8/9 dropped")
    print(f"dropped derived columns {DROPPED}; all source columns accounted for")


if __name__ == "__main__":
    convert()
