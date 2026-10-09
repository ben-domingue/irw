#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/WWN1TS
# DOI: 10.7910/DVN/WWN1TS (dataset; the record names the paper only as "submitted to
#   Language Learning")
#   Holzknecht, Franz (2022). "Repeating the listening text: effects on student
#   performance, metacognitive processing, and anxiety". Harvard Dataverse.
# Data: data_facets.xlsx (file, format=original), sheet "data_all": the scored
#       listening test in FACETS layout -- one row per student x task x listening, with
#       `listentimes` coded as the workbook's own "items_labelling" sheet defines it
#       (1 = task heard once only, 2 = answers after the second listening, 3 = answers
#       after the first listening of a twice-heard task). 306 students x 4 tasks: two
#       multiple-choice tasks of 6 items (MCQ1, MCQ2) and two note-form tasks of 9
#       items (NF1, NF2). 153 students heard both MCQ tasks twice and the NF tasks once,
#       the other 153 the reverse. Items scored 0/1.
#       data_spss.sav holds the same test unscored plus questionnaires.
# License: CC0 1.0 (Dataverse record).
#
# Cross-checks run below: for every twice-heard task the "second listening" rows equal
#   data_spss.sav's *_twice_fin columns cell for cell (NF1: 1,377 of 1,377; that file's
#   value labels say 0 = correct, but the cells show 1 = correct), and the MCQ1 once-only
#   rows equal the .sav letter answers scored against the key in each column name
#   (MCQ_1_q1_key_A_once ...). The note-form once-only rows were rescored for FACETS
#   (they agree with the .sav codes on about 90% of answered cells); the FACETS sheet is
#   the analysts' final scoring and is what ships.
#
# Item text: not shipped. Plain workbook with no labels; the tasks (audio and items)
#   are not in the deposit -- only open_responses_questionnaire.docx, the post-test
#   questionnaire.
#
# Table holzknecht_2022_listening: id = the FACETS student number; item = task_q
#   (mcq1_1 .. mcq1_6, mcq2_1 .. mcq2_6, nf1_1 .. nf1_9, nf2_1 .. nf2_9); resp 0/1.
#   treat = 1 when the student heard that task twice (resp = the answer after the
#   second listening, the score the study analyses), 0 when heard once. Assignment
#   varies by task within student, so treat is a response-level column.
# Skipped: the first-listening answers of twice-heard tasks (an intermediate answer
#   to the same item by the same student); the trailing per-task sum column; the
#   workbook's "data_unique-items" sheet (a recoding of the same answers for a
#   different FACETS model); data_spss.sav's post-task questionnaires (strategy and
#   anxiety items asked per task format and condition, keyed to a candidate number that
#   matches only 289 of the 306 FACETS ids) and its demographics (all empty).

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_wwn1ts"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DV = "https://dataverse.harvard.edu/api"
FILES = ("data_facets.xlsx", "data_spss.sav")
NAME = "holzknecht_2022_listening"
TASKS = {1: ("mcq1", 6), 2: ("mcq2", 6), 3: ("nf1", 9), 4: ("nf2", 9)}


def fetch() -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out = {}
    j = None
    for f in FILES:
        p = RAW_DIR / f
        if not p.exists():
            if j is None:
                j = requests.get(f"{DV}/datasets/:persistentId/",
                                 params={"persistentId": "doi:10.7910/DVN/WWN1TS"},
                                 headers=UA, timeout=120).json()
            fid = [x["dataFile"]["id"] for x in j["data"]["latestVersion"]["files"]
                   if x["dataFile"].get("originalFileName", x["dataFile"]["filename"]) == f][0]
            r = requests.get(f"{DV}/access/datafile/{fid}?format=original", headers=UA,
                             timeout=300)
            r.raise_for_status()
            p.write_bytes(r.content)
        out[f] = p
    return out


def main() -> None:
    paths = fetch()
    a = pd.read_excel(paths["data_facets.xlsx"], "data_all")
    a.columns = ["student", "tasktype", "task", "listentimes", "items"] + \
        [f"v{i}" for i in range(1, 11)]
    assert len(a) == 1836 and a["student"].nunique() == 306
    s, _ = pyreadstat.read_sav(str(paths["data_spss.sav"]))

    # cross-check 1: second-listening rows == the .sav's twice_fin columns (NF1)
    z = a[(a.task == 3) & (a.listentimes == 2)].merge(s, left_on="student", right_on="candno")
    v = z[[f"v{i}" for i in range(1, 10)]].to_numpy()
    fin = z[[f"NF_1_q{i}_twice_fin" for i in range(1, 10)]].to_numpy()
    assert len(z) > 140 and np.array_equal(v, fin)
    # cross-check 2: MCQ1 once-only rows == letter answers scored against the key
    z = a[(a.task == 1) & (a.listentimes == 1)].merge(s, left_on="student", right_on="candno")
    cols = [c for c in s.columns if c.startswith("MCQ_1_q") and c.endswith("_once")]
    keys = [c.split("_key_")[1][0] for c in cols]
    sc = np.array([[int(r[c] == k) for c, k in zip(cols, keys)] for _, r in z.iterrows()])
    assert len(z) > 140 and np.array_equal(sc, z[[f"v{i}" for i in range(1, 7)]].to_numpy())

    rows = []
    for (stu, task), g in a.groupby(["student", "task"]):
        lts = set(g["listentimes"])
        assert lts in ({1}, {2, 3}), (stu, task, lts)
        twice = lts == {2, 3}
        r = g[g["listentimes"] == (2 if twice else 1)].iloc[0]
        pre, n = TASKS[task]
        # the column after the last item is the task sum
        assert r[f"v{n + 1}"] == r[[f"v{i}" for i in range(1, n + 1)]].sum(), (stu, task)
        for i in range(1, n + 1):
            rows.append((int(stu), f"{pre}_{i}", r[f"v{i}"], int(twice)))
    t = pd.DataFrame(rows, columns=["id", "item", "resp", "treat"]).dropna(subset=["resp"])
    assert t["resp"].isin([0, 1]).all()
    t["resp"] = t["resp"].astype(int)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    assert len(t) == 306 * 30 and not t.duplicated(["id", "item"]).any()
    # design: half the students heard both MCQ tasks twice, half both NF tasks
    assert t.groupby("id")["treat"].sum().value_counts().to_dict() == {12: 153, 18: 153}
    print("  [skip] first-listening answers of twice-heard tasks: intermediate answer")

    pv = {i: {0, 1} for i in t["item"].unique()}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    for f in report.warnings:
        print(f"    [validate warn] {f.check}: {f.message[:160]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
          f"resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
