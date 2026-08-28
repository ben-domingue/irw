"""Stress Questionnaire for Children and Adolescents (SQC).

Source: Hahn & Winkler (2025), Zenodo 10.5281/zenodo.17159652, CC BY 4.0 --
"Stress in Children and Adolescents: Development and Validation of a new
Questionnaire". 230 respondents, 17 SQC items on a 0-3 scale.

The deposit ships two files with the same respondents: an R-oriented file
holding exactly the 17 SQC items, and an SPSS file holding those plus the
study's other instruments. The SPSS file is read so the sample characteristics
are available as covariates, and the item set is asserted to match the R file's
17 columns.

Only the SQC ships. The SPSS file also carries MAI_KJ (27 columns), SSKJ (18)
and four KINDL subscale blocks, which are the study's comparison measures; the
deposit publishes no codebook naming their items or response formats, so they
are left rather than shipped under guessed construct names. They are a
recoverable lead if someone identifies them from the paper.

The SQC item numbering is not contiguous (`SQC_1..8, 10, 12, 13, 17, 19, 20,
...`): the validation dropped items from a longer pilot pool and the deposit
keeps the original numbers. Preserved as-is, since renumbering would break the
join to the source's own item labels.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

RECORD = 17159652
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "hahn_2025_sqc"

COVARIATES = {
    "Sample_group": "cov_sample_group",
    "COVID_group": "cov_covid_group",
    "Age_group": "cov_age_group",
    "Age": "cov_age",
    "Gender": "cov_gender",
    "School_Type": "cov_school_type",
    "caregiver_presence": "cov_caregiver_presence",
}


def fetch_raw(out_dir=None):
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    paths = {}
    for f in rec["files"]:
        if not f["key"].lower().endswith(".sav"):
            continue
        local = os.path.join(out_dir or "/tmp", f["key"])
        if not os.path.exists(local):
            r = requests.get(f["links"]["self"], timeout=600)
            r.raise_for_status()
            with open(local, "wb") as fh:
                fh.write(r.content)
        paths[f["key"]] = local
    return paths


def read_sav(p):
    try:
        return pyreadstat.read_sav(p, apply_value_formats=False)[0]
    except Exception:
        return pyreadstat.read_sav(p, apply_value_formats=False,
                                   encoding="latin1")[0]


def main(paths=None):
    paths = paths or fetch_raw()
    spss = read_sav(next(v for k, v in paths.items() if "SPSS" in k))
    r_file = read_sav(next(v for k, v in paths.items() if "_R_" in k))

    items = [c for c in spss.columns if re.match(r"^SQC_\d+$", str(c))]
    r_items = [c for c in r_file.columns if re.match(r"^SQC_\d+$", str(c))]
    assert set(items) == set(r_items), \
        "the SPSS and R files disagree on the SQC item set"
    assert len(items) == 17, f"expected 17 SQC items, found {len(items)}"

    spss = spss.rename(columns=COVARIATES)
    covs = [v for v in COVARIATES.values() if v in spss.columns]
    spss = spss.reset_index(drop=True)
    if "Subject_Number" in spss.columns:
        spss["id"] = spss["Subject_Number"].astype(int)
        assert spss["id"].is_unique, "Subject_Number is not one row per child"
    else:
        spss["id"] = spss.index + 1

    long = (spss.melt(id_vars=["id"] + covs, value_vars=items,
                      var_name="item", value_name="resp")
                .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 17
    assert long["resp"].between(0, 3).all(), "SQC is a 0-3 scale"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
