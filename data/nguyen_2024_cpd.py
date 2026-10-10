#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/7IZW37
# DOI: 10.7910/DVN/7IZW37 (dataset; no paper DOI on the record, none found by search)
#   Nguyen, Tien-Trung; Hoang, Anh-Duc; Vu, Cam Tu; Nguyen, Chien Thang; Le, Thi Hong
#   Chi; Tran, My Ngoc (2024). "Replication Data for Vietnamese Secondary Teachers'
#   Motivation and Willingness to Join CPD Activities". Harvard Dataverse, V1.
# Data: "390 Sep 23.csv" (file 8141386, format=original) -- 390 Vietnamese secondary
#       teachers x 47 columns: a Google-Forms timestamp, four coded demographics, 34
#       six-point items in four lettered blocks (A1-A9, B1-B8, C1-C12, D1-D5), two
#       free-text Vietnamese questions on hours spent in professional groups, and six
#       empty trailing columns. No codebook, questionnaire or paper in the deposit.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. The CSV has no variable or value labels at all (plain CSV);
#   the item headers are short English abbreviations ("A1.Compliance",
#   "C7.OutEaseofJoin"), not stems, and the Vietnamese questionnaire is not deposited.
#   The only administered wording in the file is the two free-text hour questions.
#
# Constructs: there is no codebook, so the tables follow the deposit's own lettered
#   blocks, read from the header abbreviations:
#   nguyen_2024_cpd_motivation   A1-A9   reasons for joining CPD (compliance, pedagogical/
#                                        IT/psychological capacity, new curriculum,
#                                        own/peer needs, self/peer reflection)
#   nguyen_2024_cpd_benefits     B1-B8   expected benefits (fill knowledge/skill gaps,
#                                        use resources, solve problems, plan, emotions,
#                                        relationships)
#   nguyen_2024_cpd_conditions   C1-C12  enabling conditions: C1-C6 inside the school, C7-C12
#                                        the same six conditions ("Out...") outside it
#                                        (ease of joining, school/external funding,
#                                        flexible time, recognition by manager/peers)
#   nguyen_2024_cpd_willingness  D1-D5   support received/given (D1, D2) and willingness to
#                                        chair/operate/present in professional groups
#   All items 1-6, shipped as stored; the anchors are undocumented (no codebook). Item
#   codes are the source headers verbatim (B3's "UtilzeIncónumeRes" typo included).
# Skipped: Timestamp (form submission time, administrative); the two free-text hours
#   questions (open text: "1 tháng", "Khoảng 36h"); Unnamed: 41-46 (empty).
# Covariates: cov_school_type, cov_grade_level, cov_subject (each 1/2), cov_degree
#   (1/2/3), shipped as the source's codes -- their labels are not documented anywhere
#   in the deposit.
# No id column: id = row index + 1. 35 rows repeat another row's 34 item responses (31
#   straight-liners, two pairs that are not); every row has a distinct timestamp, so
#   nothing marks a resubmission and all rows are kept. Two cells missing (C10, C12).

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
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "nguyen_2024"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/8141386?format=original"

BLOCKS = {"nguyen_2024_cpd_motivation": "A", "nguyen_2024_cpd_benefits": "B",
          "nguyen_2024_cpd_conditions": "C", "nguyen_2024_cpd_willingness": "D"}
BLOCK_SIZE = {"A": 9, "B": 8, "C": 12, "D": 5}
COVS = {"School type": "cov_school_type", "Grade level": "cov_grade_level",
        "Subject": "cov_subject", "Degree": "cov_degree"}


def fetch() -> Path:
    p = RAW_DIR / "390_Sep_23.csv"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_csv(fetch(), encoding="utf-8-sig")
    assert d.shape == (390, 47), d.shape
    tables = {name: [c for c in d.columns if c.split(".")[0][:1] == L
                     and c.split(".")[0][1:].isdigit()]
              for name, L in BLOCKS.items()}
    for name, its in tables.items():
        assert len(its) == BLOCK_SIZE[BLOCKS[name]], (name, its)
    items = [c for its in tables.values() for c in its]
    hours = [c for c in d.columns if c[:3] in ("6. ", "7. ")]
    empty = [c for c in d.columns if c.startswith("Unnamed:")]
    assert len(hours) == 2 and len(empty) == 6 and d[empty].isna().all().all()
    # books: every column shipped or skipped with a reason
    accounted = {"Timestamp"} | set(COVS) | set(items) | set(hours) | set(empty)
    assert accounted == set(d.columns), set(d.columns) ^ accounted
    print("  [skip] Timestamp: form submission time (administrative)")
    for c in hours:
        print(f"  [skip] {c[:50]}...: free-text hours")
    for c in empty:
        print(f"  [skip] {c}: empty column")
    d = d.rename(columns=COVS).reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    covs = list(COVS.values())
    names = list(tables)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, its in tables.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert (t["resp"] % 1 == 0).all()
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(1, 6).all(), name
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        checks = run_qc(t)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload")
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
