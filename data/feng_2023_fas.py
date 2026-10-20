#!/usr/bin/env python3

# Source: https://zenodo.org/records/10070595
# DOI: 10.5061/dryad.66t1g1k4d
#   Feng, S., McDaniel, S., & Van de Winckel, A. (2023). Finding
#   functionality: Rasch analysis of the Functionality Appreciation Scale in
#   community-dwelling adults in the US [Dataset]. Dryad / Zenodo.
#   Paper: Front. Rehabil. Sci. 4:1222892, doi:10.3389/fresc.2023.1222892.
# Data: "FAS_data_10.30.2023_for_DRYAD.xlsx", sheet "FAS DATA" -- 567 US
#   adults (RedCap for community-dwelling adults, paper forms for adults with
#   spinal cord injury), collected 2019-07-20 to 2021-09-09 in Minnesota.
#   7 Functionality Appreciation Scale items, 0-4.
# License: CC0 1.0 (verified on the Zenodo record, 2026-10-20).
# Item text: IN HAND but NOT shipped here, pending a rights ruling. Both the
#   README and the workbook's "Legend" sheet print all 7 stems verbatim
#   ("I appreciate my body for what it is capable of doing.") and all 5
#   anchors (0 = strongly disagree .. 4 = strongly agree), so extraction is
#   solved. The blocker is rights, not text: these are the Functionality
#   Appreciation Scale's own items (Alleva, Tylka & Kroon Van Diest, 2017),
#   a third-party instrument the depositors reproduced -- the deposit's CC0
#   covers the depositors' material, not the instrument. Needs a row in
#   itemtext/instrument_rights_register.csv before it ships.
#
# ONE table: the 7 FAS items, asked of every respondent.
#
# id: the deposit's own ID column, which is study-assigned (the README notes
#   11XXX numbers mark the adults with spinal cord injury). 567 unique over
#   567 rows. Not PII.
# Covariates: the README's full documented set. GRP is the clinical grouping
#   (H = no mental health condition or pain, M = mental health conditions,
#   P = pain or pain + mental health); AGE is a band (0 = <65, 1 = 65+), not
#   a year; SEX is 0/1/2 male/female/other. EB/CB/ER/CR/EBA/CBA are the six
#   yes/no breathing, relaxation and body-awareness practice questions.
# "." in ER and CR is the file's missing marker, present for the 14
#   paper-form respondents; it is set to missing rather than read as a code.
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
    REPO_ROOT / "automated_finding" / "runs" / "zenodo" / "10070595"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 10070595, "FAS_data_10.30.2023_for_DRYAD.xlsx"
TABLE = "feng_2023_fas"
ITEMS = [f"F{i}" for i in range(1, 8)]
COVS = {"GRP": "cov_group", "AGE": "cov_age_band", "SEX": "cov_sex",
        "MHC": "cov_mental_health_condition", "PAIN": "cov_pain",
        "EB": "cov_ever_breathing", "CB": "cov_current_breathing",
        "ER": "cov_ever_relaxation", "CR": "cov_current_relaxation",
        "EBA": "cov_ever_body_awareness", "CBA": "cov_current_body_awareness"}
MISSING_MARKER = "."
SCALE = set(range(0, 5))


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
    df = pd.read_excel(fetch(), sheet_name="FAS DATA")
    expected = {"ID", *COVS, *ITEMS}
    assert set(df.columns) == expected, set(df.columns) ^ expected
    assert len(df) == 567, len(df)
    assert df["ID"].nunique() == len(df), "ID is not unique per respondent"

    df = df.rename(columns={"ID": "id", **COVS})
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        df[cov] = df[cov].replace(MISSING_MARKER, pd.NA)
    assert df["cov_ever_relaxation"].isna().sum() == 14, "expected 14 blanks"

    t = (df[["id", *cov_cols, *ITEMS]]
         .melt(id_vars=["id", *cov_cols], value_vars=ITEMS,
               var_name="item", value_name="resp")
         .dropna(subset=["resp"]))
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the README's documented 0-4 scale: {bad}"
    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() == 567 and t["item"].nunique() == 7

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
