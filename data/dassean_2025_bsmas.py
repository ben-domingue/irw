#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_b_Psychometric_Validation_of_the_Jordanian_Version_of_the_Bergen_Social_Media_Addiction_Scale_BSMAS_b_/28375283
# DOI: 10.6084/m9.figshare.28375283.v2 (dataset; no paper DOI on the record)
#   Dassean, Khaled (2025). "Jordanian Version of the Bergen Social Media Addiction
#   Scale (BSMAS)" [data set]. figshare, v2.
# Data: "BSMAS jordanian version.sav": 605 Jordanians (school students, university
#       students, community; ages 16-60) x participant number, sample type, gender,
#       age, an age-group dummy, daily social-media hours, BSMAS item1-6 (+ total),
#       DASS-21 DASS1-21 (+ three subscale sums). SPSS variable and value labels
#       present. "BSMAS-TEST R-TEST.sav": 94 retest respondents (BSMAS twice, DASS
#       once, own numbering 1-94) -- NOT shipped: N < 100 on its own, and it cannot
#       be linked reliably to the main file (66 of 94 rows match a main-file row on
#       all 27 items, 28 match none). "Supplemantry material.docx": figures and the
#       Arabic questionnaire (instructions, the six BSMAS items, options).
# License: CC BY 4.0 (figshare record).
#
# Item text: dassean_2025_bsmas shipped (administered Arabic stems and options from the
#   deposit's Supplemantry material.docx, items numbered 1-6 matching the .sav's
#   component labels Salience..Conflict; English options from the .sav value labels;
#   built by automated_finding/itemtext_verification/make_itemtext_dassean_2025.py).
#   English stem translations are IRW's own. dassean_2025_dass21 not shipped: DASS
#   variable labels are positional ("S-1", "A-2"), value labels carry the four options,
#   and the Arabic DASS-21 wording is not in the deposit.
#
# Tables:
#   dassean_2025_bsmas   item1-6, 1 = Very rarely ... 5 = Very often
#   dassean_2025_dass21  DASS1-21, 0 = Did not apply to me at all ... 3 = Applied to
#                        me very much (two missing DASS17 cells dropped)
# Not shipped: total, depression, anxiety, stress (sums); agecomparison (age split,
#   derivable from cov_age); Number (used as id).
# Covariates: cov_sample (1 school students, 2 university students, 3 community),
#   cov_gender (1 male, 2 female), cov_age, cov_sm_hours (1 <1 h ... 5 >6 h daily;
#   one unlabelled 6 set to missing).

import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "dassean_2025"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/52344812"
TABLES = {"dassean_2025_bsmas": ([f"item{i}" for i in range(1, 7)], range(1, 6)),
          "dassean_2025_dass21": ([f"DASS{i}" for i in range(1, 22)], range(0, 4))}
COVS = {"sampletype": "cov_sample", "Gender": "cov_gender", "Age": "cov_age",
        "Houres": "cov_sm_hours"}
SKIP = {"total": "BSMAS sum", "depression": "DASS sum", "anxiety": "DASS sum",
        "stress": "DASS sum", "agecomparison": "age split, derivable from cov_age"}


SUPP = "https://ndownloader.figshare.com/files/52344902"   # questionnaire (item text)


def fetch() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in [("BSMAS_jordanian_version.sav", URL), ("supp.docx", SUPP)]:
        p = RAW_DIR / name
        if not p.exists():
            r = requests.get(url, headers=UA, timeout=300)
            r.raise_for_status()
            p.write_bytes(r.content)
    return RAW_DIR / "BSMAS_jordanian_version.sav"


def main() -> None:
    d, meta = pyreadstat.read_sav(str(fetch()))
    assert d.shape == (605, 37) and d["Number"].is_unique
    items = [c for its, _ in TABLES.values() for c in its]
    assert set(d.columns) == {"Number"} | set(items) | set(COVS) | set(SKIP)
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    d = d.rename(columns={"Number": "id", **COVS})
    d["id"] = d["id"].astype(int)
    d.loc[d["cov_sm_hours"] == 6, "cov_sm_hours"] = pd.NA
    covs = list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, rng) in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(list(rng)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
