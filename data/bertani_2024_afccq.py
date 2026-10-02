#!/usr/bin/env python3
# Source: https://zenodo.org/records/11084903
# DOI: 10.1007/s10823-025-09532-1
#   Bertani, M., van Hoof, J., & Dikken, J. (2025). "Getting Older People's
#   Voices Heard: A Quantitative Study Using the Validated Italian
#   Age-Friendly Cities and Communities Questionnaire in Venice, Verona and
#   Palermo." Journal of Cross-Cultural Gerontology, 40, 209-234.
#   (PMC12137376, CC BY.) Cited as the data's paper in the Zenodo
#   description.
#   Dataset: Bertani, M. (2024). The Age-Friendly Cities and Communities
#   Questionnaire (AFCCQ) - Data collection ITALY 2023. Zenodo.
# Data: Zenodo 11084903, AFCCQ-IT_dataset.sav (1,213 rows x 54 columns;
#       adults aged 65+ in Verona, Venice and Palermo, random sample from the
#       municipal population registers, CATI interviews, 2023).
# License: CC BY 4.0 (Zenodo record metadata).
#
# Item text: not shipped. Both label levels checked: the variable labels hold
#   full ENGLISH item stems for A1-A23, and the value labels hold English
#   anchors keyed 1-5 (the data are stored -2..+2; see below). The survey
#   was administered in Italian; the Italian AFCCQ-IT wording is the paper's
#   Supplementary Material 1 (Springer), not in the deposit. A later pass
#   could ship the English labels as a translated_substitute (language =
#   Italian) or the Italian from that supplement.
#
# Table (item codes are the source column names):
#   bertani_2024_afccq  A1-A23  Age-Friendly Cities and Communities
#                       Questionnaire, Italian version (Dikken et al. 2020;
#                       23 items, nine WHO domains). The paper: "Responses
#                       are recorded on a 5-point Likert scale", and the
#                       total runs -46 to +46 (domain scores -4 to +4), i.e.
#                       each item is scored -2 .. +2. The file stores exactly
#                       that (-2 totally disagree .. +2 totally agree; its
#                       value labels 1-5 are the same five anchors before
#                       centring), and it is kept as stored. A7 and A8 (age
#                       remarks / age discrimination) are kept in their raw,
#                       as-asked direction.
#
# Dropped:
#   - A7_rev, A8_rev: reverse-coded copies (A_rev == -A, asserted).
#   - ident: an agency respondent number -> replaced by the row index.
#   - d2 (year of birth): redundant with age (age + d2 == 2023 in every row,
#     asserted) and finer-grained than needed.
#   - d3_other, d9s: free-text country of birth / "please specify".
#   - d91_4 (help from a volunteer association): 0 in every answered row.
# id: row index.
# Covariates: cov_city (ISTAT municipality code: 23091 Verona, 27042
#   Venezia, 82053 Palermo), cov_gender (1 male, 2 female), cov_age,
#   cov_born_italy (1 Italy, 2 other), cov_education (1 primary/lower
#   secondary .. 4 master/doctorate), cov_district (d5: city district code,
#   50 = other), cov_years_in_city, cov_housing (1 owner, 2 social housing,
#   3 rent), cov_lives_alone (1 alone, 2 with someone), cov_help_at_home
#   (1 yes, 2 no), cov_help_family / _friend / _paid / _municipal / _other
#   (0/1, asked only when help_at_home = 1), cov_n_chronic (number of
#   chronic diseases, decoded from D10's reversed value labels 4='8' ..
#   12='0'), cov_diabetes / _kidney / _respiratory / _heart / _cancer /
#   _liver (1 yes, 2 no), cov_walking_aid (1 yes, 2 no),
#   cov_life_satisfaction (1-10).

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/11084903/files/"
       "AFCCQ-IT_dataset.sav/content")

TABLE = "bertani_2024_afccq"
ITEMS = [f"A{i}" for i in range(1, 24)]
ALLOWED = {-2, -1, 0, 1, 2}
REVERSED = {"A7_rev": "A7", "A8_rev": "A8"}
DROPPED = {"ident", "d2", "d3_other", "d9s", "d91_4"}
COVS = {"comune": "cov_city", "d1": "cov_gender", "age": "cov_age",
        "d3": "cov_born_italy", "d4": "cov_education", "d5": "cov_district",
        "d6": "cov_years_in_city", "d7": "cov_housing",
        "d8": "cov_lives_alone", "d9": "cov_help_at_home",
        "d91_1": "cov_help_family", "d91_2": "cov_help_friend",
        "d91_3": "cov_help_paid", "d91_5": "cov_help_municipal",
        "d91_6": "cov_help_other", "D10": "cov_n_chronic",
        "d10_1": "cov_diabetes", "d10_2": "cov_kidney",
        "d10_3": "cov_respiratory", "d10_4": "cov_heart",
        "d10_5": "cov_cancer", "d10_6": "cov_liver",
        "d11": "cov_walking_aid", "d12_1": "cov_life_satisfaction"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (1213, 54), d.shape

    # Balance the books.
    known = set(ITEMS) | set(REVERSED) | DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known

    for alt, src in REVERSED.items():
        assert (d[alt] == -d[src]).all(), alt
    assert (d["age"] + d["d2"] == 2023).all()
    assert set(d["d91_4"].dropna()) == {0}
    assert d["ident"].is_unique
    anchors = {1.0: "Totaly disagree", 2.0: "Disagree", 3.0: "neutral",
               4.0: "agree", 5.0: "Totaly agree"}
    for c in ITEMS:
        assert meta.variable_value_labels[c] == anchors, c

    # D10's value labels run backwards: code 4 = '8' diseases .. 12 = '0'.
    lab = meta.variable_value_labels["D10"]
    assert all(int(v) == 12 - k for k, v in lab.items()), lab
    d["D10"] = 12 - d["D10"]

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert len(long) == 1213 * 23  # the paper: no missing AFCCQ-IT values
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - ALLOWED
        assert not bad, (it, bad)
    pv = {i: ALLOWED for i in ITEMS}
    long = long[["id", "item", "resp"] + cov_cols]
    for c in cov_cols:
        long[c] = long[c].astype("Int64")
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == len(ITEMS)
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(
        str(out), profile="upload", context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
