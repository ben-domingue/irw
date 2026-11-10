#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0357563
# DOI: 10.1371/journal.pone.0357563
# Paper: Chen J, Li X, Zhu C, Biryukova M (2026). Museum visitors' acceptance
#   of digital services in China and Russia: Extending UTAUT2 with
#   individual-level cultural values. PLOS ONE 21(11): e0357563.
# Data: S1 Data (XLSX, "De-identified item-level survey dataset for the Chinese
#   and Russian samples, with a variable codebook"): sheet "Data" 623 rows x 36
#   columns, sheet "Codebook" (every variable's meaning and coding), plus
#   "Demographic summary" and "README". S1 File (DOCX) is the questionnaire:
#   Chinese and Russian administered versions and an English reference
#   translation that "was not administered to participants". Both attached to
#   the article.
# License: CC BY 4.0 (the article's licence covers its SI files).
#
# Found by the PLOS monthly run of 2026-11-09 (leads/plos_leads_2026-11-09.csv,
# step-2b worth_retrying; its dup_id_item fail is Respondent_ID restarting at
# 1 in each country, not repeated measures).
#
# NINE output tables, one per construct, 3 items each, all 1-7 ("seven-point
# Likert scale ranging from 1 (strongly disagree) to 7 (strongly agree)";
# Codebook: "no reverse-scored items"). Item codes are the deposit's headers.
#   PE  performance expectancy        -> chen_2026_museum_performance_expectancy
#   EE  effort expectancy             -> chen_2026_museum_effort_expectancy
#   SI  social influence              -> chen_2026_museum_social_influence
#   FC  facilitating conditions       -> chen_2026_museum_facilitating_conditions
#   HM  hedonic motivation            -> chen_2026_museum_hedonic_motivation
#   BI  acceptance (behavioural) intention -> chen_2026_museum_behavioral_intention
#   COL collectivism orientation      -> chen_2026_museum_collectivism
#   UAI uncertainty avoidance         -> chen_2026_museum_uncertainty_avoidance
#   LTO long-term orientation         -> chen_2026_museum_long_term_orientation
#
# TWO SAMPLES MERGED, cov_country distinguishes them: 316 Chinese and 307
# Russian museum visitors answered the same 27 items (Chinese and Russian
# versions of one questionnaire, S1 File; identical item codes and 1-7 scale;
# the paper tests measurement invariance across the two with MICOM before
# its multigroup comparison). Per the same-instrument-across-samples rule,
# one table per construct, not one per country.
#
# Covariates (Codebook labels, carried as the source's codes):
#   cov_country (China / Russia), cov_gender (1 = Male, 2 = Female),
#   cov_age (Age_code_original: 1 = <=18, 2 = 18-35, 3 = 36-55, 4 = >55; the
#   README says retained code-1 respondents were all aged 18),
#   cov_education (1 = High school or below, 2 = University, 3 = Postgraduate+),
#   cov_occupation (1 = Student .. 5 = Other), cov_visit_mode (1 = Alone,
#   2 = With family/friends, 3 = Tour group, 4 = School/institution-organized).
# DROPPED: Age_group_analysis (derived from Age_code_original, per Codebook)
#   and Prior_digital_service_use_code (constant 1: an inclusion criterion).
# `id`: Respondent_ID restarts at 1 in each country (1-316, 1-307), so it is
#   not unique; replaced by the row index 1-623 (verified unique within
#   country first).
#
# Imputation: none. Incomplete responses were removed before deposit (paper,
#   "invalid responses ... or incomplete answers were removed"); no missing
#   cells; every item cell is an integer 1-7 (asserted).
#
# Item text: HELD. Label levels checked: S1 Data headers (codes PE1..LTO3) and
#   its Codebook (labels like "Performance expectancy item", no stems); S1 File
#   "Part 2. Measurement items" prints every stem beside its code in Chinese and
#   Russian (administered, split by cov_country) and English (a reference
#   translation the file says "was not administered"). Identification (S1 File
#   "Measurement sources and coding notes"): PE/EE/SI/FC/HM/BI "adapted and
#   contextualized" from UTAUT2 (Venkatesh, Thong & Xu 2012); COL/UAI/LTO from
#   CVSCALE (Yoo, Donthu & Lenartowicz 2011). Read against the UTAUT2 appendix:
#   BI1, FC1, HM2 are near noun-swaps, EE2/FC3 paraphrases, the other 13 are
#   museum-specific; UAI1/UAI3 resemble CVSCALE UA stems, COL/LTO do not. 17
#   verbatim searches matched no prior source. Register Chen2026-Museum-UTAUT2
#   and Chen2026-Museum-CVSCALE (hold, new 2026-11-09). Language, if ever
#   shipped: two administered languages in one table -> language "Chinese;
#   Russian", base fields hold one version, public_note says who read the other
#   (itemtext_standard.md "Administered language"); or a per-country split.
#   Rights: the paper declares the items adapted from named sources, so they
#   are held under the 2026-11-02 domain-swap ruling (silence holds). BUT the
#   stems read as freshly written under the cited construct labels; whether
#   that shape is the 11-02 'still the instrument' case or the 09-23 R16
#   'study-authored adaptation ships' class is a question for Ben.
#
# PII: README: "No names, email addresses, telephone numbers, free-text
#   responses, or other direct personal identifiers are included." Screened:
#   the only string columns are Country and the derived age band.

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
URL = ("https://journals.plos.org/plosone/article/file?type=supplementary"
       "&id=10.1371/journal.pone.0357563.s001")
RAW = os.environ.get("CHEN_MUSEUM_RAW", "")

N_ROWS = 623
N_BY_COUNTRY = {"China": 316, "Russia": 307}
LO, HI = 1, 7
CONSTRUCTS = {
    "PE": "chen_2026_museum_performance_expectancy",
    "EE": "chen_2026_museum_effort_expectancy",
    "SI": "chen_2026_museum_social_influence",
    "FC": "chen_2026_museum_facilitating_conditions",
    "HM": "chen_2026_museum_hedonic_motivation",
    "BI": "chen_2026_museum_behavioral_intention",
    "COL": "chen_2026_museum_collectivism",
    "UAI": "chen_2026_museum_uncertainty_avoidance",
    "LTO": "chen_2026_museum_long_term_orientation",
}
COVS = {"Country": "cov_country", "Gender_code": "cov_gender",
        "Age_code_original": "cov_age", "Education_code": "cov_education",
        "Occupation_code": "cov_occupation", "Visit_mode_code": "cov_visit_mode"}
DROPPED = ["Respondent_ID", "Age_group_analysis",
           "Prior_digital_service_use_code"]


def fetch():
    if RAW:
        return RAW
    _uc.allowed_gai_family = lambda: socket.AF_INET  # IPv6 stalls here
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=120)
    r.raise_for_status()
    path = os.path.join(tempfile.mkdtemp(), "chen_museum_s1.xlsx")
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


def convert():
    df = pd.read_excel(fetch(), sheet_name="Data")
    assert df.shape == (N_ROWS, 36), df.shape
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])
               or df[c].dtype == object]
    print(f"PII screen: {len(df.columns)} columns examined, {len(strings)} "
          f"string column(s): {strings}")
    assert len(df.columns) > 0
    assert sorted(strings) == ["Age_group_analysis", "Country"], strings
    assert df["Country"].value_counts().to_dict() == N_BY_COUNTRY
    assert not df.duplicated(["Country", "Respondent_ID"]).any()
    assert (df["Prior_digital_service_use_code"] == 1).all()
    assert int(df.isna().sum().sum()) == 0
    df["id"] = range(1, N_ROWS + 1)
    df = df.rename(columns=COVS)
    cov_cols = list(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    items_all = []
    total = 0
    for prefix, name in CONSTRUCTS.items():
        assert len(name) <= 40, name
        cols = [f"{prefix}{i}" for i in (1, 2, 3)]
        items_all += cols
        assert df[cols].isin(range(LO, HI + 1)).all().all(), name
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert not long.duplicated(["id", "item"]).any()
        long = long[["id", "item", "resp"] + cov_cols]
        checks = run_qc(long, permitted_values=list(range(LO, HI + 1)))
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-"
              f"{long['resp'].max()}")

    accounted = set(items_all) | set(cov_cols) | set(DROPPED) | {"id"}
    assert accounted == set(df.columns), set(df.columns) ^ accounted
    assert len(set(CONSTRUCTS.values())) == len(CONSTRUCTS)
    assert total == 27 * N_ROWS, total
    print(f"9 tables, {total} responses (27 items x {N_ROWS}); dropped "
          f"{DROPPED[1:]} and the per-country Respondent_ID; all source "
          f"columns accounted for")


if __name__ == "__main__":
    convert()
