#!/usr/bin/env python3

# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/D155SP
# DOI: 10.7910/DVN/D155SP
#   Kam, C. D., Archer, A. M., & Geer, J. G. (2016). Replication Data for:
#   Courting the Women's Vote: The Emotional, Cognitive, and Persuasive
#   Effects of Gender-Based Appeals in Campaign Advertisements [Dataset].
#   Harvard Dataverse.
# Data: "Kam Archer Geer replication file.dta" -- 17,400 US survey
#   respondents, each shown one of 29 ads aired in the 2012 election campaign
#   and then asked how the ad made them feel.
# License: CC0 1.0 (verified on the Dataverse record, 2026-10-19).
# Item text: NOT shipped, but it is IN THE FILE and extraction-solved for a
#   later pass: the five Stata variable labels carry the stem and the emotion
#   ("Feelings from ad - Disgusted"). The response anchors are not in the
#   deposit, so a text pass needs the paper's appendix for those.
#
# ONE table: the five-emotion battery, 1-5, all five items asked of every
#   respondent about the ad they saw.
#
# NOT SHIPPED, and why:
#   q5c  -- "Opinion on the ad - memorable", a single 1-5 item of its own
#           construct; a one-item table is not an instrument.
#   q10  -- current presidential vote preference, 1-4; a behavioural intention
#           item, again alone.
#   weight_ct -- the survey weight. Not a response and not a respondent
#           attribute; a weight belongs with the analysis, not the table.
#   wordcount -- the length of the respondent's open-ended answer, which this
#           deposit does not include. An artefact of a text the file lacks.
#
# The file's last row is entirely blank (17,401 rows, 17,400 respondents) --
#   a trailing record, dropped on the all-missing test rather than by position.
#
# id: the row index. `caseid` is the survey platform's own respondent id, so
#   under the 2026-09-20 narrowing it is replaced by the row index, never
#   hashed.
# cov_ad: which of the 29 ads the respondent saw. It is the study's
#   experimental assignment, but `treat` is reserved for 0/1 and 29 arms do
#   not fit it, so it ships as a covariate with the deposit's own codes.
# Covariates: cov_ad, cov_birth_year, cov_gender, cov_party_id7,
#   cov_party_id3, cov_race, cov_education, cov_marital_status,
#   cov_family_income. All ship as the deposit's own codes; it documents no
#   value labels. `faminc` 97 is the survey's "prefer not to say" sentinel
#   and is set to missing (16 brackets plus 31, the top bracket, are kept).
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "dvn_batch" / "d155sp" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID, FNAME = 2809496, "Kam Archer Geer replication file.dta"
ITEMS = ["q2_disgusted", "q2_angry", "q2_worried", "q2_happy", "q2_hopeful"]
COVS = {"video": "cov_ad", "birthyr": "cov_birth_year", "gender": "cov_gender",
        "pid7": "cov_party_id7", "pid3": "cov_party_id3", "race": "cov_race",
        "educ": "cov_education", "marstat": "cov_marital_status",
        "faminc": "cov_family_income"}
NOT_SHIPPED = ["caseid", "weight_ct", "q5c", "q10", "wordcount"]
SCALE = set(range(1, 6))
FAMINC_REFUSED = 97
TABLE = "kam_2016_ad_emotions"


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = ("https://dataverse.harvard.edu/api/access/datafile/"
               f"{FILE_ID}?format=original")
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    path = fetch()
    df = pd.read_stata(path, convert_categoricals=False)
    labels = pd.io.stata.StataReader(path).variable_labels()
    expected = set(ITEMS) | set(COVS) | set(NOT_SHIPPED)
    assert set(df.columns) == expected, set(df.columns) ^ expected
    print(f"not shipped: {NOT_SHIPPED}")

    # The five items' stems live in the labels; refuse a renamed column.
    for c in ITEMS:
        assert (labels.get(c) or "").startswith("Feelings from ad - "), \
            (c, labels.get(c))

    blank = df.isna().all(axis=1)
    assert blank.sum() == 1 and blank.iloc[-1], \
        f"expected exactly one all-blank trailing row, got {blank.sum()}"
    df = df[~blank].reset_index(drop=True)
    assert len(df) == 17400, len(df)

    df = df.rename(columns=COVS)
    df["id"] = range(1, len(df) + 1)
    cov_cols = list(COVS.values())
    df["cov_family_income"] = df["cov_family_income"].replace(
        FAMINC_REFUSED, pd.NA)
    for cov in cov_cols:
        v = pd.to_numeric(df[cov])
        assert (v.dropna() % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")
    assert FAMINC_REFUSED not in set(df["cov_family_income"].dropna())
    assert set(df["cov_ad"].dropna()) == set(range(1, 30))

    t = (df[["id", *cov_cols, *ITEMS]]
         .melt(id_vars=["id", *cov_cols], value_vars=ITEMS,
               var_name="item", value_name="resp")
         .dropna(subset=["resp"]))
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all()
    t["resp"] = t["resp"].astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the documented 1-5 scale: {bad}"
    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 17000 and t["item"].nunique() == 5

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:170]}")
    report = irw_validate.validate_frame(t, label=TABLE, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
