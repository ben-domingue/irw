#!/usr/bin/env python3
# Source: https://zenodo.org/records/7487238 (QTI-EP) and
#   https://zenodo.org/records/7489024 (Teacher-Student Relationships, CR)
# DOI: 10.5281/zenodo.7487238; 10.5281/zenodo.7489024 (data). QTI-EP
#   validation: 10.1387/RevPsicodidact.9081.
#   Garcia Bacete, F. J., Marande Perrin, G., Munoz Tinoco, M. V., & GREI
#   Group (2023). GREI Longitudinal Project datasets. Zenodo.
# Data: one .sav per deposit (latin-1 strings), each with a "Met-D"
#   descriptive-metadata PDF giving every item's wording and value labels:
#   - QTI-EP_Data_CC-CS_T2-Post.sav: 2nd-grade pupils, Castellon + Seville
#     comparison cohorts, spring 2011; Questionnaire on Teacher Interaction -
#     Early Primary (Zijlstra et al. 2013), 20 items, 1-5 (never .. always).
#   - TEACHER-STUDENT-CR_Data_CC_T6-Pre.sav: 6th-grade pupils, Castellon,
#     autumn 2014; Teacher Student Relationships - Child Rating (Wu, Hughes &
#     Kwok 2010), 22 items, 1-5 (little or none .. the most).
# License: CC BY 4.0 (both Zenodo records).
# Codebook: the Met-D PDF in each deposit.
#
# GREI is a near-identical T1-T4 series; per the 2026-10 backlog rule this
#   takes one representative wave per instrument (the IRW already has the
#   GREI victimization and loneliness representatives).
# Item text: not shipped -- the English wording is in the Met-D PDFs; no
#   rights-register rows for QTI-EP or TSR-CR.
#
# Tables (raw item columns; the deposits' Rec_* reverse-scored copies and
#   factor/dimension scores are not shipped):
#   garciabacete_2023_qti_ep   QTI_EP_01..20 (wave suffix stripped), 1-5
#   garciabacete_2023_tsr_cr   TeacherStudent_CR1..22 (suffix stripped), 1-5
# Rows with no item answered (pupils listed in the class roster who did not
#   complete this measure) drop out.
# Covariates: cov_sex (Met-D: 0 = boy, 1 = girl), cov_site (Sample 11 =
#   Castellon, 13 = Seville), cov_classroom (the deposit's classroom code).
# id = the deposit's 6-digit child ID (a study code, not a personal one).

import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
ALLOWED = {1, 2, 3, 4, 5}
SPEC = {
    "garciabacete_2023_qti_ep": (
        "https://zenodo.org/api/records/7487238/files/"
        "QTI-EP_Data_CC-CS_T2-Post.sav/content",
        [f"QTI_EP_{i:02d}" for i in range(1, 21)], "_T2post"),
    "garciabacete_2023_tsr_cr": (
        "https://zenodo.org/api/records/7489024/files/"
        "TEACHER-STUDENT-CR_Data_CC_T6-Pre.sav/content",
        [f"TeacherStudent_CR{i}" for i in range(1, 23)], "_T6pre"),
}
SITE = {11: "Castellon", 13: "Seville"}
SEX = {0: "boy", 1: "girl"}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (url, items, suf) in SPEC.items():
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
            tmp.write(r.content)
            tmp.flush()
            d, _ = pyreadstat.read_sav(tmp.name, encoding="latin1")
        d = d.rename(columns={i + suf: i for i in items})
        assert d["ID"].is_unique
        d["id"] = d["ID"].astype(int)
        d["cov_sex"] = d["Sex"].map(SEX)
        d["cov_site"] = d["Sample"].map(SITE)
        assert d["cov_site"].notna().all()
        d["cov_classroom"] = d["Classroom" + suf].astype("Int64")
        covs = ["cov_sex", "cov_site", "cov_classroom"]
        long = d.melt(id_vars=["id"] + covs, value_vars=items,
                      var_name="item", value_name="resp").dropna(
                          subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert not set(long["resp"]) - ALLOWED, table
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: ALLOWED for c in items})
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
