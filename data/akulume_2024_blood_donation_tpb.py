#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/27934290
# DOI: 10.6084/m9.figshare.27934290.v1 (data)
#   Akulume M (2024). Blood Donation TPB data_Published.dta [Data set]. figshare.
# License: CC BY 4.0 (figshare)
# Data: "De-dentified Blood Donation TPB data_Published.dta", 336 secondary-school students in four
#   schools in East-central Uganda who completed the theory-of-planned-behaviour items (of 559).
#   Self-administered questionnaire. Value labels on every item: 1 Strongly Agree, 2 Agree,
#   3 Neither Agree nor Disagree, 4 Disagree, 5 Strongly Disagree -- shipped as stored (lower =
#   more agreement).
#
# Tables (item = the Stata variable name; membership verified: each table's items average to the
#   deposit's own composite in all 336 rows):
#   akulume_2024_donation_intention -- N30-N33 (Intention)
#   akulume_2024_donation_pbc       -- N34-N39 (PBC, perceived behavioural control)
#   akulume_2024_donation_norms     -- N40-N49 (Subjectivenorms)
# Not shipped: the attitude items N50-N57 (9; composite Attitudes). N54 "Donating blood affects my
#   health negatively", N56 "...is a waste of time" and both N57 items are negatively worded yet
#   correlate positively with the rest, so they were reversed before deposit while their value
#   labels still read 1 = Strongly Agree; which coding the stored values carry cannot be confirmed.
#   Eligibility/knowledge yes-no items are recoded and summarised as percentages; composites.
# id: row number (Questionnairecode repeats for 12 rows, on rows that differ elsewhere).
# Covariates: cov_age, cov_sex, cov_education (Senior 3-6, labels), cov_school_location (rural/urban).
# Item text: not shipped -- the Stata variable labels carry the statements but truncated at ~45
#   characters ("N30Iintendtodonatebloodinthenextbloo"); the questionnaire is not in the deposit.
import io
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://ndownloader.figshare.com/files/50896149"


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".dta") as f:
        f.write(r.content)
        f.flush()
        d, meta = pyreadstat.read_dta(f.name)
    assert len(d) == 336
    items = [c for c in d.columns if c.lower().startswith("newn") and c[4:6].isdigit()]
    assert len(items) == 29
    vl = meta.variable_value_labels
    for c in items:
        assert vl[c][1].startswith("Strongly Agree") and vl[c][5].startswith("Strongly Disagree"), c
    blocks = {"intention": (items[0:4], "Intention"), "pbc": (items[4:10], "PBC"),
              "norms": (items[10:20], "Subjectivenorms")}
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = d["Age"]
    d["cov_sex"] = d["NewSex"].map(vl["NewSex"])
    d["cov_education"] = d["NewHighesteducationlevelacieved"].map(vl["NewHighesteducationlevelacieved"])
    d["cov_school_location"] = d["UrbanRural"].map(vl["UrbanRural"]).str.lower()
    covs = ["cov_age", "cov_sex", "cov_education", "cov_school_location"]
    for name, (cols, comp) in blocks.items():
        assert ((d[cols].mean(axis=1) - d[comp]).abs() < 1e-4).all(), name
        t = d[["id"] + covs + cols].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(1, 5).all()
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t) if c.status == "fail"]
        assert not fails, (name, fails)
        out = f"akulume_2024_donation_{name}"
        t.to_csv(OUT / f"{out}.csv", index=False)
        print(out, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
