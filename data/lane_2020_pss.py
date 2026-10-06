#!/usr/bin/env python3
# Source: https://zenodo.org/records/4264764 (Dryad 10.5061/dryad.2jm63xskj)
# DOI: 10.1136/bmjopen-2020-040245
#   Lane, McGrath, Cleary, Guerandel & Malone (2020). "Worried, weary and worn out:
#   mixed-method study of stress and well-being in final-year medical students",
#   BMJ Open 10(12): e040245.
# Data: Student_Stress_Database_November_2020.xlsx, Sheet1: 161 final-year medical
#       students at University College Dublin (2017) x 21 columns: Participant,
#       Batch, Age, Gender, GEM (graduate-entry), q1-q10 (Perceived Stress Scale),
#       TOTAL PSS, a 0-10 subjective stress rating and four free-text answers.
#       Stress_Questionnaire_for_Medical_Students_November_2020.docx is the
#       questionnaire.
# License: CC0 1.0 (Dryad/Zenodo record).
#
# Shipped: lane_2020_pss -- PSS-10 items q1-q10, 0-4. -999 = missing (3 cells,
#   dropped). TOTAL PSS equals the sum of the stored q1-q10 for 160 of 161 rows,
#   so the stored values are as scored; the positively worded items (4, 5, 7, 8)
#   are therefore most likely already reverse-scored -- not altered here.
# Not shipped: the free-text answers (scanned: no names or e-mail addresses, but
#   not item responses), the single 0-10 subjective stress rating, TOTAL PSS.
# Covariates: batch (1/2), age, gender (deposit codes 1/2/N), GEM (1/2; -999 ->
#   missing; age -999 -> missing).
#
# Item text: not shipped. Levels checked: xlsx headers q1-q10 only (no labels);
#   the questionnaire .docx in the deposit carries the PSS wording (PSS-10,
#   Cohen et al.), a published instrument.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "z4264764"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/4264764/files/Student_Stress_Database_November_2020.xlsx/content"
NAME = "lane_2020_pss"


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name="Sheet1")
    assert d.shape == (161, 21), d.shape
    items = [f"q{i}" for i in range(1, 11)]
    assert d["Participant"].is_unique
    x = d[items].replace(-999, float("nan"))
    assert (x.sum(axis=1) == d["TOTAL PSS"]).sum() >= 160
    d = d.rename(columns={"Participant": "id", "Batch": "cov_batch", "Age": "cov_age",
                          "Gender": "cov_gender", "GEM": "cov_graduate_entry"})
    for c in ("cov_graduate_entry", "cov_age"):
        d[c] = d[c].replace(-999, pd.NA)
    d["cov_gender"] = d["cov_gender"].astype(str)
    covs = ["cov_batch", "cov_age", "cov_gender", "cov_graduate_entry"]
    t = d.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
    t = t[t["resp"] != -999]
    assert t["resp"].isin(range(0, 5)).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert len(t) == 161 * 10 - 3
    pv = {i: {0, 1, 2, 3, 4} for i in items}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
