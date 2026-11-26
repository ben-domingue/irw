#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_i_Dataset_for_How_does_teacher-student_interaction_drive_English_learning_engagement_A_serial_mediation_analysis_of_academic_self-efficacy_and_English_learning_interest_in_Chinese_application-oriented_universities_i_/32112169
# DOI: 10.6084/m9.figshare.32112169.v1 (data; no paper DOI on the record)
#   Li D (2026). Dataset for: How does teacher-student interaction drive
#   English learning engagement? A serial mediation analysis of academic
#   self-efficacy and English learning interest in Chinese application-oriented
#   universities. figshare.
# Data: one workbook, sheets Dataset (201 x 55), Variable Key, Item_Descriptions
#   (the Chinese stem of every item).
# License: CC BY 4.0 (figshare record).
# Codebook: the workbook's Variable Key and Item_Descriptions sheets.
#
# Counts: 201 rows = the description's final-analysis N = 201. Each Dataset
#   total (TSIQ, ASE, LI, LE) equals the sum of its key items (asserted).
# Tables (1-5, raw items; the R_* reverse-coded copies and the totals are
#   dropped; the four negatively worded items Q16, Q26, Q34, Q46 ship
#   unreversed):
#   li_2026_teacher_student_interaction  11 items Q3,Q5-Q8,Q11-Q16
#   li_2026_academic_self_efficacy       10 items Q17-Q26
#   li_2026_english_learning_interest     8 items Q27-Q34
#   li_2026_english_learning_engagement  11 items Q35-Q41,Q43-Q46
# Item code Q43: the data column is headed "Q42", but the Variable Key's LE
#   formula and the Item_Descriptions sheet both call this item Q43 (there is
#   no Q42 in either), and the LE total reproduces only with this column. It
#   ships as Q43 so it joins the deposit's own description.
# id = Participant_ID (unique). Informed_Consent (all 1) dropped.
# Covariates: gender, grade, EFL level, student type (codes; labels in the
#   Variable Key).
# Item text: not shipped -- the Chinese stems are in Item_Descriptions; the
#   instruments are unidentified adaptations with no register row.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://ndownloader.figshare.com/files/70373055"
SPEC = {
    "li_2026_teacher_student_interaction":
        (["Q3", "Q5", "Q6", "Q7", "Q8", "Q11", "Q12", "Q13", "Q14", "Q15", "Q16"], "TSIQ"),
    "li_2026_academic_self_efficacy": ([f"Q{i}" for i in range(17, 27)], "ASE"),
    "li_2026_english_learning_interest": ([f"Q{i}" for i in range(27, 35)], "LI"),
    "li_2026_english_learning_engagement":
        ([f"Q{i}" for i in range(35, 42)] + ["Q43", "Q44", "Q45", "Q46"], "LE"),
}
REVERSED = {"Q16", "Q26", "Q34", "Q46"}
COVS = {"Gender": "cov_gender", "Grade": "cov_grade", "EFL": "cov_efl_level",
        "Student_Type": "cov_student_type"}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    x = pd.read_excel(io.BytesIO(r.content), sheet_name=None)
    d = x["Dataset"]
    assert d.shape == (201, 55), d.shape
    assert "Q43" not in d.columns and "Q42" in d.columns
    d = d.rename(columns={"Q42": "Q43"})
    desc = " ".join(str(v) for v in x["Item_Descriptions"].astype(str).values.ravel())
    desc += " " + " ".join(map(str, x["Item_Descriptions"].columns))
    for cols, _ in SPEC.values():
        for c in cols:
            assert f"{c}:" in desc, c
    for c in REVERSED:
        assert ((6 - d[c]) == d[f"R_{c[1:]}"]).all(), c
    for cols, total in SPEC.values():
        keyed = [f"R_{c[1:]}" if c in REVERSED else c for c in cols]
        assert (d[keyed].sum(axis=1) == d[total]).all(), total
    assert d["Participant_ID"].is_unique
    d = d.rename(columns={"Participant_ID": "id", **COVS})
    covs = list(COVS.values())
    allowed = set(range(1, 6))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (cols, _) in SPEC.items():
        long = d[["id"] + cols + covs].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp"
        ).dropna(subset=["resp"])
        assert not set(long["resp"]) - allowed, table
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: allowed for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
