#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0323712
# DOI: 10.1371/journal.pone.0323712
# Paper: Chhajer R, Bapat SR (2025). Exploring the impact of nature
#   connectedness on well-being and mental distress among urban youth:
#   Evidence from 25 most populated cities in India. PLOS ONE 20(5): e0323712.
# Data: figshare 10.6084/m9.figshare.27612366 ("wellbeing_final_data.csv"),
#   one file, wellbeing_final_copy.csv, 2282 rows x 25 columns, headers are the
#   questionnaire wording. No codebook in the deposit; the paper's Methods
#   document every column.
# License: CC BY 4.0 (figshare record).
#
# Found by the PLOS monthly run of 2026-11-09 (leads/plos_leads_2026-11-09.csv,
# step-2b recoverable_format: the reader kept only the WHO columns).
#
# ONE output table: chhajer_2025_who5 -- WHO-5 Well-Being Index, 5 items, 0-5
#   ("0 (at no time) ... 5 (all of the time)", paper, Well-being section).
#   Item codes are the deposit headers lower-cased with the space as "_"
#   ("WHO 1" -> who_1).
# DROPPED (derived): "WHO sum", "WHO avg", "who indicator" (WHO-5 sum < 13,
#   the paper's mental-distress flag) -- asserted to equal the recomputation.
# DROPPED (free text): "If working, your work experience (in years)" -- typed
#   free text (96 distinct values, some in Hindi), not a coded variable.
# NIS (Inclusion of Nature in Self, a single pictorial item, 0-6) is carried
#   as the covariate cov_nis rather than as a one-item table; the paper uses
#   it as a predictor.
# Covariates (categories as deposited, text): cov_city (one of 25 cities),
#   cov_gender, cov_age (18-25), cov_education, cov_occupation (student /
#   working professional), cov_income, cov_nature_access, cov_green_distance,
#   cov_blue_distance, cov_visits_nature, cov_visit_reason, cov_visit_freq,
#   cov_visits_other_cities, cov_other_city_freq, cov_time_indoors, cov_nis.
# `id`: the deposit has no id column; row index 1-2282.
#
# Imputation: none (incomplete responses removed before deposit, paper);
#   no missing item cells; every item cell an integer 0-5 (asserted).
#
# Item text: HELD. Label levels checked: the deposit's headers are positional
#   ("WHO 1".."WHO 5"), no value labels, no questionnaire in the deposit.
#   Instrument: the WHO-5 Well-Being Index (the article names it; 5 items,
#   0-5). Register WHO5 is `block` (WHO's CC BY-NC-SA 3.0 IGO) -- confirmed
#   2026-11-09; nothing to ship.
#
# PII: no names, emails, dates or locations finer than city. The one free-text
#   column (work experience) is dropped.

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
URL = "https://ndownloader.figshare.com/files/50217609"
RAW = os.environ.get("CHHAJER_WHO5_RAW", "")
TABLE = "chhajer_2025_who5"
N_ROWS = 2282
ITEMS = [f"WHO {i}" for i in range(1, 6)]
COVS = {
    "City": "cov_city",
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Education": "cov_education",
    "Are you a student or a working professional?": "cov_occupation",
    "Annual Income": "cov_income",
    "Do you have access to nature (green or blue spaces) around your residence?": "cov_nature_access",
    "Do you have access to green space near your residence?": "cov_green_distance",
    "Do you have access to blue space near your residence?": "cov_blue_distance",
    "Do you visit green or blue spaces for recreational purposes?": "cov_visits_nature",
    "If yes, why do you visit such spaces?": "cov_visit_reason",
    "If yes, how often do you visit green or blue spaces for recreational purposes? ": "cov_visit_freq",
    "Do you visit other cities for nature based recreation?": "cov_visits_other_cities",
    "If yes, how often do you visit other cities for such purposes?": "cov_other_city_freq",
    "How much time do you spend indoors during the day? ": "cov_time_indoors",
    "NIS": "cov_nis",
}
DROPPED = ["WHO sum", "WHO avg", "who indicator",
           "If working, your work experience (in years)"]


def fetch():
    if RAW:
        return RAW
    _uc.allowed_gai_family = lambda: socket.AF_INET  # IPv6 stalls here
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=120)
    r.raise_for_status()
    path = os.path.join(tempfile.mkdtemp(), "wellbeing_final_copy.csv")
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


def convert():
    df = pd.read_csv(fetch(), encoding="utf-8-sig")
    assert df.shape == (N_ROWS, 25), df.shape
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(df.columns)} columns examined, {len(strings)} "
          f"string column(s)")
    assert len(df.columns) > 0 and len(strings) == 15
    accounted = set(ITEMS) | set(COVS) | set(DROPPED)
    assert accounted == set(df.columns), set(df.columns) ^ accounted

    assert df[ITEMS].isin(range(0, 6)).all().all()
    total = df[ITEMS].sum(axis=1)
    assert (total == df["WHO sum"]).all()
    assert ((total < 13).astype(int) == df["who indicator"]).all()
    assert df["NIS"].isin(range(0, 7)).all()

    df["id"] = range(1, N_ROWS + 1)
    df = df.rename(columns=COVS)
    cov_cols = list(COVS.values())
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                   var_name="item", value_name="resp")
    long["item"] = long["item"].str.lower().str.replace(" ", "_")
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]
    assert not long.duplicated(["id", "item"]).any()
    assert len(long) == 5 * N_ROWS

    checks = run_qc(long, permitted_values=list(range(0, 6)))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:140]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-"
          f"{long['resp'].max()}; dropped {DROPPED}")


if __name__ == "__main__":
    convert()
