#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/RCJ1YC (Harvard Dataverse)
# DOI: 10.7910/DVN/RCJ1YC (dataset, 2023; Maruyama, Takao; Igei, Kengo). Replication data for "Community-wide Support
#   for Primary Students to Improve Foundational Literacy and Numeracy: Empirical Evidence from Madagascar" -- a
#   school-level randomised trial (140 schools, grades 3-5) with a 44-item mathematics test at baseline and endline.
# Data: Data_MadagascarIE_student_baseline.tab and Data_MadagascarIE_student_endline.tab (one row per student, 9,364
#   students in both), with Q1_correct_wrong..Q44_correct_wrong (1 = correct, 0 = wrong; codebooks_student_file.xlsx).
#   The Q*_response columns hold the raw answers (not shipped). Students who did not sit the numeracy assessment
#   (Attendance_Numeracy* != 1) have blank items and are dropped, so N = 8,455 at baseline and 7,033 at endline.
# Table: maruyama_2023_madagascar_math, items q1..q44, resp 0/1, wave 1 = baseline, wave 2 = endline. The same Q1..Q44
#   numbering is used at both waves and per-item difficulty profiles agree across waves (the authors' IRT script
#   likewise uses the same 44 columns); the deposit does not explicitly say the forms are identical.
#   treat = school treatment arm (1 treatment, 0 control); cluster_id = School_Code (the unit of random assignment).
# id: ID_IE_Student is a study-assigned code; replaced by a 1..N index in sorted-code order (same student, same id, in
#   both waves). Covariates are from baseline: sex, age, grade, urban/rural, repeated-grade flag.
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none (school and student codes only; no names, dates of birth or locations below the education district, which
#   is not shipped).
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_F_2026-10-16"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset (ingested tab)."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        time.sleep(4)
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"] if f["dataFile"]["filename"] == fname][0]
        r = requests.get(f"https://{host}/api/access/datafile/{fid}", headers=UA, timeout=600)
        r.raise_for_status()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
        time.sleep(4)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values). QC, validate, write."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert max(map(len, tables)) <= 40, name
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 8, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")


def main() -> None:
    doi = "10.7910/DVN/RCJ1YC"
    rd = RAW_ROOT / "rcj1yc"
    b = pd.read_csv(dv_fetch(doi, "Data_MadagascarIE_student_baseline.tab", rd), sep="\t", low_memory=False)
    e = pd.read_csv(dv_fetch(doi, "Data_MadagascarIE_student_endline.tab", rd), sep="\t", low_memory=False)
    assert len(b) == 9364 and len(e) == 9364 and b["ID_IE_Student"].is_unique and e["ID_IE_Student"].is_unique
    assert set(b["ID_IE_Student"]) == set(e["ID_IE_Student"])
    idmap = {s: i + 1 for i, s in enumerate(sorted(b["ID_IE_Student"]))}
    qcols = [f"Q{i}_correct_wrong" for i in range(1, 45)]
    items = {c: f"q{i}" for i, c in enumerate(qcols, 1)}
    cov = b.set_index("ID_IE_Student")[["treatment", "School_Code", "Sex", "Age", "Grade", "CATEGORIE_COMMUNE", "Repeated"]]
    assert (e.set_index("ID_IE_Student")["treatment"].reindex(cov.index) == cov["treatment"]).all()
    parts = []
    for wave, d, att in [(1, b, "Attendance_Numeracy"), (2, e, "Attendance_Numeracy_endline")]:
        d = d[d[att] == 1]
        t = d.melt(id_vars=["ID_IE_Student"], value_vars=qcols, var_name="item", value_name="resp")
        t = t[t["resp"].notna()].copy()
        t["wave"] = wave
        parts.append(t)
    t = pd.concat(parts, ignore_index=True)
    assert t["resp"].isin([0, 1]).all()
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"].map(items), categories=list(items.values()), ordered=True)
    c = cov.reindex(t["ID_IE_Student"]).reset_index(drop=True)
    t["id"] = t["ID_IE_Student"].map(idmap).astype(int)
    t["treat"] = c["treatment"].astype(int).values
    t["cluster_id"] = c["School_Code"].astype(int).values
    t["cov_sex"] = c["Sex"].map({"F": "female", "G": "male"}).values
    t["cov_age"] = c["Age"].values
    t["cov_grade"] = c["Grade"].astype(int).values
    t["cov_urban"] = (c["CATEGORIE_COMMUNE"] == "URB").astype(int).values
    t["cov_repeated_grade"] = (c["Repeated"] == "R").astype(int).values
    cols = ["id", "item", "resp", "wave", "treat", "cluster_id", "cov_sex", "cov_age", "cov_grade", "cov_urban", "cov_repeated_grade"]
    t = t.sort_values(["id", "wave", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    t = t[cols]
    emit({"maruyama_2023_madagascar_math": (t, {i: {0, 1} for i in items.values()})})


if __name__ == "__main__":
    main()
