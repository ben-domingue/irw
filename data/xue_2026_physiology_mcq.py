#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/33963304
# DOI: 10.6084/m9.figshare.33963304.v1 (dataset; the record names no paper DOI)
#   Xue, Y. (2026). Dataset for "Active Learning, Student Perceptions, and Objective
#   Achievement in an Integrated Human Functional Physiology Course" [Data set]. figshare.
# Data: "Raw research data.xlsx", one sheet: 390 students of an integrated physiology /
#       immunology / biochemistry course x 41 columns: section marks, 13 one-mark
#       multiple-choice exam items scored 0/1 and named by topic (MCQ_Nucleic_acids_mark ..
#       MCQ_Genome_mark), ten survey questions stored as option letters (A-D, and "Nill"),
#       and eight in-class test marks (0-10, fractional). No codebook.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. The MCQ columns are topic names, not the questions; the deposit
#   has no codebook or exam paper.
#
# Tables (item = the column name with the "MCQ_" prefix and "_mark" suffix removed):
#   xue_2026_mcq   13 exam items, 0/1.
# Skipped: Survey_Q1-Q10 (option letters with no key or wording, and "Nill"), the in-class
#   test marks (continuous per-test scores) and the section / total marks.
# Covariates: cov_gender (M/F), cov_major (the deposit's codes), cov_group (presentation
#   group number).
# id: Student_Index.

import os
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.6084_m9.figshare.33963304.v1"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FNAME = "Raw research data.xlsx"
T = "xue_2026_mcq"
COVS = ["cov_gender", "cov_major", "cov_group"]


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        j = requests.get("https://api.figshare.com/v2/articles/33963304", headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == FNAME][0]
        download(url, p)
    return p


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv} if pv else None)
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min():g}-{t['resp'].max():g}")


def main() -> None:
    d = pd.read_excel(fetch())
    assert len(d) == 390 and d["Student_Index"].is_unique
    mcq = {c: re.sub(r"^MCQ_|_mark$", "", c) for c in d.columns if c.startswith("MCQ_")}
    assert len(mcq) == 13, mcq
    d = d.rename(columns={"Student_Index": "id", "Gender": "cov_gender", "Major": "cov_major",
                          "Group_No": "cov_group", **mcq})
    t = d.melt(id_vars=["id"] + COVS, value_vars=list(mcq.values()), var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].isin([0, 1]).all()
    t = t[["id", "item", "resp"] + COVS].sort_values(["id", "item"]).reset_index(drop=True)
    emit({T: (t, {i: {0, 1} for i in mcq.values()})})


if __name__ == "__main__":
    main()
