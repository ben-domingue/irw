#!/usr/bin/env python3

# Source: https://zenodo.org/records/20811310
# DOI: 10.5281/zenodo.20811310
#   Baydhowi (2026). Data Set for Assessing Cross-Group Equivalence of the National
#   Identity Scale [Dataset]. Zenodo.
# Data: "Data DIF (3).xlsx" -- 504 Indonesian university students, 18 National
#       Identity Scale items, 1-5.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped. The workbook carries item NUMBERS only, no stems, and
#   .xlsx has no label level. Same position as the author's 2021 deposit: the scale
#   is the authors' own and the wording is in the paper, which the record gives no
#   DOI for. That is where the text is.
#
# NOT A DUPLICATE of the live baydhowi_2021_national_identity (zenodo.5642537, 300
#   respondents x 20 items, shipped earlier in this same #3077 run). Checked rather
#   than assumed: that table holds 261 distinct response vectors, this file 417, and
#   the exact-row overlap between them is ZERO. Different sample, and a later
#   18-item form of the same instrument.
#
# HEADER SHAPE. Row 0 names only the first three columns; row 1 is not data but the
#   AUTHOR'S ITEM NUMBERS for columns 2-19, in the deposit's own (non-sequential)
#   column order: 1, 2, 4, 12, 13, 3, 5, 7, 8, 9, 10, 15, 6, 11, 14, 16, 17, 18.
#   Item codes are built from THAT row, so the code is the source's own numbering
#   rather than the column position -- a one-position slip would otherwise be
#   invisible. Codes use the same ni_%02d spelling as the 2021 table; the
#   correspondence between the two forms is the author's numbering, not an
#   item-by-item verification by IRW.
# id: the file carries no respondent id, so the 0-based row index within the data
#   block is used. Each row is one respondent.
# Covariates: cov_gender (Jenis Kelamin), cov_university_type (Perguruan Tinggi).
# Rights: the National Identity Scale is the authors' own instrument and is not in
#   the rights register.
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
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "20811310"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 20811310, "Data DIF (3).xlsx"
NAME = "baydhowi_2026_national_identity"
SCALE = set(range(1, 6))


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                         headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    raw = pd.read_excel(fetch(), header=None)
    numbers = [int(float(v)) for v in raw.iloc[1, 2:].tolist()]
    assert sorted(numbers) == list(range(1, 19)), \
        f"row 1 is not a 1..18 item-number row: {numbers}"
    body = raw.iloc[2:, :].reset_index(drop=True)

    covs = pd.DataFrame({
        "cov_gender": body.iloc[:, 0].astype(str).str.strip(),
        "cov_university_type": body.iloc[:, 1].astype(str).str.strip(),
    })
    resp = body.iloc[:, 2:].copy()
    resp.columns = [f"ni_{n:02d}" for n in numbers]
    assert len(set(resp.columns)) == 18, "item codes are not distinct"

    d = pd.concat([covs, resp], axis=1)
    d.insert(0, "id", range(len(d)))
    t = (d.melt(id_vars=["id", "cov_gender", "cov_university_type"],
                value_vars=list(resp.columns), var_name="item", value_name="resp")
         .dropna(subset=["resp"]))
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the documented 1-5 scale: {bad}"
    t = t[["id", "item", "resp", "cov_gender", "cov_university_type"]]

    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2
    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:180]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
