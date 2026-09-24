#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC9756449
# DOI: 10.1186/s12889-022-14834-x
# "Association of anticipated HIV testing stigma and provider mistrust on
# preference for HIV self-testing among cisgender men who have sex with men in
# the Philippines" (Sison et al., 2022), BMC Public Health.
# Data: Harvard Dataverse doi:10.7910/DVN/PFUMZM (Sison, Olivia), file
#       "PLOSONE_OSison HIVST data 2022-1.tab" fetched with format=original
#       (the deposited Stata .dta), plus the deposit's "Coding manual.docx".
# License: CC0 1.0 -- the Dataverse dataset record's own licence field
#          (api/datasets/:persistentId -> latestVersion.license = "CC0 1.0").
#          The data sit in a separate deposit linked from the Data
#          Availability statement, so the deposit licence governs. (The
#          article itself is CC BY 4.0 with BMC's CC0 data waiver.)
#
# Item text: shipped for both tables (the deposit's "Coding manual.docx"
#   pairs every variable name q16..q23 with its statement and the seven
#   0-6 anchors; the .dta itself carries no variable labels, but its value
#   label set "q15" carries the same seven anchors). The survey was offered in
#   English and Tagalog; only the English wording is in the deposit.
#
# Multi-scale split. The questionnaire carries one 7-point agreement block,
# q16 and q18-q23, which the paper's Methods ("Independent variables") divide
# into two constructs, each with its own Cronbach alpha:
#   anticipated HIV testing stigma  q16, q22, q23      (alpha = 0.80)
#   provider mistrust               q18, q19, q20, q21 (alpha = 0.89)
# (matched item by item: the paper's statement wording equals the coding
# manual's for each q-code). One table per construct. Every other q-column is
# a single demographic/testing question and ships as a covariate; the rest of
# the file is the authors' own recodes/dichotomisations of those columns.
#
# The paper analyses 803 cisgender MSM; the deposit holds all 899 respondents
# (q1 = 0 male 845, 2 transgender woman 13, 4 other 41). All 899 ship, with
# gender identity and sexual orientation carried as covariates, so the paper's
# analytic sample can be re-derived.

import sys
from io import BytesIO
from pathlib import Path

import pandas as pd
import pyreadstat
import requests
import tempfile

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
import irw_validate  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
# Dataverse file id for the .dta; format=original, never the .tab conversion.
DTA_URL = "https://dataverse.harvard.edu/api/access/datafile/6081970?format=original"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# Coding manual: each is a single question, so each is a covariate.
COV = {
    "q1": "cov_gender_identity",       # 0 male,1 female,2 transgender woman,3 transgender man,4 other
    "q2": "cov_sexual_orientation",    # 0 het male ... 6 other
    "q3": "cov_relationship_status",   # 0-5
    "q7": "cov_hiv_status",            # 0 no HIV,1 HIV,2 unsure,3 rather not answer
    "q10": "cov_knows_where_to_test",  # 0 no,1 yes
    "q12": "cov_preferred_test_method",  # 0 hospital ... 4 self-testing (paper's DV)
    "q13": "cov_last_hiv_test",        # 0 never ... 5 >5 years ago
    "q36": "cov_age",                  # years
    "q38": "cov_education",            # 0-8
    "q39": "cov_employment",           # 0-12
    "q40": "cov_income",               # 0-6 (6 = don't want to disclose)
}
STIGMA = ["q16", "q22", "q23"]
MISTRUST = ["q18", "q19", "q20", "q21"]
AGREE7 = {0, 1, 2, 3, 4, 5, 6}  # coding manual: 0 strongly disagree .. 6 strongly agree

SKIP = {
    "ID": "used as id",
    "Date": "carried as the response-level `date` column (Unix seconds)",
    "Consent": "constant 'Yes/ Oo' (consent gate)",
    "q4": "constant 1 (eligibility screen: ever had sex with a man)",
}
# Everything else in the file is labelled 'RECODE of qN' or is a derived
# dichotomy/composite (stigma, mistrust, outness, hivstatus...) of the
# columns above -- not an item, not new information.
DERIVED = ["agegroup", "agegrp", "q3new", "relationship", "sexual_orientation",
           "q38_2", "q38new", "educ", "employ", "q40new", "income", "hivtest",
           "hivtestnew", "test_status", "hivstatus", "q10new", "q12new",
           "self_test", "q2new", "mistrust", "stigma", "mistrust2", "stigma2",
           "outness", "hivstatus2", "agegroup2", "hivstatus0"] + \
          [f"q{i}new" for i in (16, 18, 19, 20, 21, 22, 23)] + \
          [f"q{i}new2" for i in (16, 18, 19, 20, 21, 22, 23)]


def load() -> pd.DataFrame:
    r = requests.get(DTA_URL, headers=UA, timeout=180)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".dta") as fh:
        fh.write(r.content)
        fh.flush()
        df, _ = pyreadstat.read_dta(fh.name)
    return df


def finish(df, items, table, construct):
    d = df[["ID", "Date"] + list(COV) + items].rename(columns={"ID": "id", **COV})
    d["date"] = (pd.to_datetime(d.pop("Date"), format="%Y-%m-%d")
                 - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")
    covs = list(COV.values())
    long = d.melt(id_vars=["id", "date"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    assert (long["resp"] % 1 == 0).all(), f"{table}: fractional resp (imputation?)"
    long["id"] = long["id"].astype(int)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "date"] + sorted(covs)]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    assert set(long["resp"]).issubset(AGREE7), f"{table}: resp outside 0-6"
    assert not long.duplicated(["id", "item"]).any(), f"{table}: duplicate id/item"
    assert long["id"].nunique() >= 100, f"{table}: below the 100-id floor"
    assert long["item"].nunique() == len(items) > 1, f"{table}: item count"
    report = irw_validate.validate_frame(
        long, label=table, profile="upload",
        context={"permitted_values": {i: AGREE7 for i in items},
                 "item_constructs": {i: construct for i in items}})
    print(report)
    assert report.conforms and not report.errors, \
        [(f.name, f.detail) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{table}.csv", index=False)
    print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert() -> None:
    df = load()
    used = set(COV) | set(STIGMA) | set(MISTRUST) | set(SKIP) | set(DERIVED)
    unaccounted = [c for c in df.columns if c not in used]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    print(f"  [skip] {len(DERIVED)} derived recode columns: {', '.join(DERIVED)}")

    tables = [("sison_2022_hiv_testing_stigma", STIGMA, "anticipated HIV testing stigma"),
              ("sison_2022_provider_mistrust", MISTRUST, "provider mistrust")]
    names = [t for t, _, _ in tables]
    assert len(names) == len(set(names)), "duplicate output filenames"
    for table, items, construct in tables:
        finish(df, items, table, construct)


if __name__ == "__main__":
    convert()
