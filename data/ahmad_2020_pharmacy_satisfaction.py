#!/usr/bin/env python3

# Source: https://zenodo.org/records/4116133
# DOI: 10.5061/dryad.q573n5th1
#   Ahmad, N., Ismail, A., & Gan, Y. N. (2020). Factors associated with
#   patient satisfaction towards pharmacy services among out-patients
#   attending public health clinics: Questionnaire development and its
#   application [Dataset]. Dryad, mirrored on Zenodo (record 4116133,
#   published 2020-10-21).
# Data: "Dryad_Data_PHC_PSQ.sav" -- 400 outpatients at three randomly
#   selected Malaysian public health clinics, recruited by systematic random
#   sampling, each answering the 22-item Public Health Clinic Patient
#   Satisfaction Questionnaire (PHC-PSQ) about pharmacy services.
# License: CC0 1.0 (the Zenodo record reports license id "cc-zero",
#   verified 2026-10-20).
#
# Item text: NOT shipped. Both label levels checked. The variable-label level
#   is populated for all 22 items but holds terse one- or two-word keys
#   ("Directions", "Comfort WA", "Time QN", "Side Effects"), which name the
#   topic rather than reproducing what was asked -- they are not stems, so
#   shipping them would invent wording. The value-label level carries nothing
#   for any item: only four covariates (edugp, empgp, incgp, freqgp) have
#   value labels, and the 1-10 satisfaction scale has none, so the anchors
#   are not in the file either. The full wording is one hop away and cheap
#   for a later pass: the instrument is study-authored (the paper's whole
#   point is developing the PHC-PSQ, so there is no third-party rights
#   question here, unlike most tables from this pipeline) and the 22 items
#   are printed in the open-access paper that this deposit supports.
#
# ONE table: the PHC-PSQ, asked of every respondent. The paper's factor
# analysis gives it three domains -- administrative competency (A1-A9),
# technical competency (B1-B10) and convenience of location (C1-C3) -- but
# they are three subscales of one instrument administered as one form on one
# response scale, not three instruments, so they stay in one file. The
# A/B/C prefixes are preserved in the item codes, so a user can recover the
# domain structure without the file being split.
#
# id: the deposit's own "id" column, 400 unique values over 400 rows, one row
#   per respondent. Study-assigned sequence, not PII.
#
# resp: 1-10 satisfaction rating, integer, complete -- no missing cells
#   across all 8,800 respondent-item pairs and no fractional values. The
#   paper reports a total mean score of 7.56 (SD 1.32) on this scale, which
#   is consistent with the observed values. Individual items do not all span
#   the full 1-10 range (A2 is observed 3-8, A7 is 1 and 4-8); that is
#   category non-use on a 10-point scale with 400 respondents, not evidence
#   of different scales, so no item is split or recoded.
#
# Covariates: the deposit's full documented set. agegp (1-6 age band) and hs
#   ("Raw Health Status", 1-5) have no value labels in the file, so they are
#   carried as the source's own codes rather than guessed at. The four that
#   do have value labels are mapped to those labels. "know" is the paper's
#   pharmacy-knowledge score (0-10); it is a respondent attribute measured
#   alongside the questionnaire, not one of the PHC-PSQ items, so it is a
#   covariate and not part of the melt.
#
# Rights-register hit, checked and dismissed: irw-validate warns that item
#   codes C1, C2 and C3 match the register's Connor-Davidson Resilience Scale
#   row (verdict: block). That is a false positive of the kind the register's
#   own short patterns are known to produce. C1, C2 and C3 here are the
#   PHC-PSQ's convenience-of-location items -- the file's variable labels for
#   them are "Parking", "Public Transport" and "Home" -- and this deposit has
#   no resilience measure in it at all. They are also the source's own column
#   names rather than item wording, so the warning's rename advice does not
#   apply and nothing needs renaming before publication. Checked by name
#   against the register as well as by running the gate, per the standing
#   rule that a `ship` verdict is invisible to the gate and a hit is a lead
#   rather than a verdict.
#
# PII: none. Zero string-dtype columns -- the screen is run with
#   pd.api.types.is_string_dtype (never dtype == object, which reports zero
#   on a pyreadstat frame whose text columns are StringDtype) over every
#   column, and the denominator is printed below. Every column is a numeric
#   code: an id sequence, grouped demographics (age band, education,
#   employment, income and visit-frequency as binary groups), a health-status
#   rating, a knowledge score and the 22 items. No name, email, date of
#   birth, postal code, phone number, address or free-text field exists in
#   the file, so there is no column whose job is to collect an identifier.
import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s5"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "zenodo" / "4116133"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 4116133, "Dryad_Data_PHC_PSQ.sav"
TABLE = "ahmad_2020_pharmacy_satisfaction"

ITEMS = ([f"A{i}" for i in range(1, 10)]
         + [f"B{i}" for i in range(1, 11)]
         + [f"C{i}" for i in range(1, 4)])
COVS = {"agegp": "cov_age_group", "edugp": "cov_education",
        "empgp": "cov_employment", "incgp": "cov_income",
        "freqgp": "cov_visit_frequency", "hs": "cov_health_status",
        "know": "cov_pharmacy_knowledge"}
LABELLED = {"edugp", "empgp", "incgp", "freqgp"}
SCALE = set(range(1, 11))
N_RESP = 400


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://zenodo.org/api/records/{RECORD}/files/{FNAME}/content"
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()))
    expected = {"id", *COVS, *ITEMS}
    assert set(df.columns) == expected, set(df.columns) ^ expected
    assert len(df) == N_RESP, len(df)
    assert df["id"].nunique() == N_RESP, "id is not unique per respondent"

    # PII screen -- print the denominator so an empty selection is visible.
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"[pii] columns examined for PII: {len(df.columns)} total, "
          f"{len(text_cols)} of them string-dtype")
    assert len(df.columns) > 0, "PII screen selected no columns"

    # Apply the file's own value labels where it has them.
    for raw in LABELLED:
        labels = meta.variable_value_labels.get(raw)
        assert labels, f"expected value labels on {raw}"
        df[raw] = df[raw].map(labels)
        assert df[raw].notna().all(), f"unmapped code in {raw}"

    df = df.rename(columns=COVS)
    cov_cols = list(COVS.values())

    t = (df[["id", *cov_cols, *ITEMS]]
         .melt(id_vars=["id", *cov_cols], value_vars=ITEMS,
               var_name="item", value_name="resp")
         .dropna(subset=["resp"]))
    assert len(t) == N_RESP * len(ITEMS), (len(t), N_RESP * len(ITEMS))
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the documented 1-10 scale: {bad}"
    t["id"] = t["id"].astype(int)

    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any(), "duplicate id/item"
    assert t["id"].nunique() == N_RESP and t["item"].nunique() == len(ITEMS)

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
