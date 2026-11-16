#!/usr/bin/env python3
# Source: https://zenodo.org/records/23623141
# DOI: 10.5281/zenodo.23623141 (data; no paper on the record)
#   Gray, A., & Young-Jones, A. (2026). "Empathy and Basic Psychological Need
#   Satisfaction Dataset." Zenodo.
# Data: "Empathy 10.22.sav" (398 students at a midwestern US public
#   university, 2022-2023), SPSS-labelled item columns for six instruments
#   plus the authors' reverse-keyed copies (*rev) and subscale sums.
# License: CC BY 4.0 (Zenodo record).
# Codebook: none beyond the SPSS labels (labels are "Basic Empathy Scale 1"
#   etc., no wording).
#
# Item text: not shipped -- the .sav labels are positional ("Basic Empathy
#   Scale 1"); the wording is in the published instruments.
#
# Tables (one per instrument, raw item columns, NOT the *rev copies):
#   gray_2026_bes    Basic Empathy Scale, BES1-BES20, 1-5
#   gray_2026_iri    Interpersonal Reactivity Index, IRI1-IRI28, stored 0-4
#                    (the SPSS value labels say 1-5 but every observed
#                    value is 0-4, the usual IRI scoring; kept as stored)
#   gray_2026_see    Scale of Ethnocultural Empathy, SEE1-SEE31, 1-6
#   gray_2026_efq    Empathy Formative Questionnaire, EFQ1-EFQ15, 1-5
#   gray_2026_bpns   Basic Psychological Need Satisfaction (general),
#                    BPNS1-BPNS21, 1-7
#   gray_2026_pwb    Ryff Psychological Well-Being, 18 items, PWB1-PWB18,
#                    1 = strongly agree .. 7 = strongly disagree (as labelled)
# Imputed values: 12 cells across IRI/SEE/EFQ/BPNS hold non-integer values
#   (e.g. 1.8, 2.4, 3.7) -- the deposit's mean imputation. Dropped
#   (datastandard: remove imputed values). Integer-valued imputations, if
#   any, cannot be told apart and stay.
# Not shipped: the six single "Q1-Q6" wellbeing statements (no scale), single-
#   item stress/satisfaction ratings, every free-text column (major,
#   self-descriptions, disability explanations), none carried in any form.
# Covariates: cov_age, cov_gender (SPSS labels). id = row index.

import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests
import tempfile

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = ("https://zenodo.org/api/records/23623141/files/"
            "Empathy%2010.22.sav/content")
SPEC = {  # table: (prefix, n items, allowed values)
    "gray_2026_bes": ("BES", 20, set(range(1, 6))),
    "gray_2026_iri": ("IRI", 28, set(range(0, 5))),
    "gray_2026_see": ("SEE", 31, set(range(1, 7))),
    "gray_2026_efq": ("EFQ", 15, set(range(1, 6))),
    "gray_2026_bpns": ("BPNS", 21, set(range(1, 8))),
    "gray_2026_pwb": ("PWB", 18, set(range(1, 8))),
}
GENDER = {1: "male", 2: "female", 3: "trans male", 4: "trans female",
          5: "gender variant/non-conforming", 6: "self-described"}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(r.content)
        tmp.flush()
        d, meta = pyreadstat.read_sav(tmp.name)
    assert d.shape == (398, 268), d.shape
    assert meta.variable_value_labels["gender"][2] == "Female"
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = d["age"]
    d["cov_gender"] = d["gender"].map(GENDER)
    covs = ["cov_age", "cov_gender"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (p, n, allowed) in SPEC.items():
        items = [f"{p}{i}" for i in range(1, n + 1)]
        long = d.melt(id_vars=["id"] + covs, value_vars=items,
                      var_name="item", value_name="resp").dropna(
                          subset=["resp"])
        frac = long["resp"] % 1 != 0
        if frac.any():
            print(f"[drop] {table}: {int(frac.sum())} imputed non-integer cells")
        long = long[~frac].copy()
        long["resp"] = long["resp"].astype(int)
        assert not set(long["resp"]) - allowed, (table, set(long["resp"]))
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: allowed for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
