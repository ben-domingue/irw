#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/FHWPHK
# DOI (data): 10.7910/DVN/FHWPHK
# DOI (paper): 10.3352/jeehp.2020.17.42
# Data: Park, S. Y., Kong, H.-H., Kim, M.-J., Yoon, Y. S., Lee, S.-H., Im, S.,
#   & Seo, J.-H. (2020). Clinical performance of medical students in Korea in
#   a whole-task emergency station in the objective structured clinical
#   examination with a standardized patient complaining of palpitations.
#   Journal of Educational Evaluation for Health Professions, 17, 42. Harvard
#   Dataverse "Dataset 1. Raw data of the students' responses and the result
#   data" (sheet "Raw data").
# License: CC0 1.0, verified via the Dataverse API.
#
# Found 2026-11-10 (hour-1110-b) from the JEEHP collection leads (lane C).
#
# ONE output table:
#   park_2020_osce_palpitations  checklist scores of 150 third-year medical
#     students (5 universities, Busan-Gyeongnam Clinical Skill Examination) on
#     a whole-task emergency OSCE station (palpitations): history taking
#     (items 1-13, binary), physical examination (14-18, 3-point), ECG study
#     (19-24, binary or 3-point), patient education (25-27, binary) and
#     clinical reasoning (28, the written diagnosis; stored as levels 1-3,
#     every student has one) -- matches the paper's Methods item counts.
#     The deposit stores each multi-point item as one-hot columns, e.g.
#     "14(2)" and "14(1)", "28(3)/(2)/(1)"; these are recombined to the
#     credit level (0 when no column is ticked). No row ticks two levels.
#     Items 19-22 and 24-27 are stored directly (19 holds 0-2).
#   Not shipped: the six PPI columns (patient-physician interaction, 0-4; not
#     described in the paper) and the single global-rating item; the two
#     summary rows (counts, proportions) above/below the data.
#   Checked: 150 students (No 1-150), as in the paper.
# `id` is the deposit's No. No covariates in the file.
#
# Item text: not shipped -- item numbers only.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("PARK_RAW", "Dataset 1. Raw data of the students' responses and the result data.xlsx")
NAME = "park_2020_osce_palpitations"


def convert():
    raw = pd.read_excel(RAW, sheet_name="Raw data", header=None)
    hdr = [str(h).replace(".0", "") for h in raw.iloc[3].tolist()]
    d = raw.iloc[4:154].reset_index(drop=True)
    assert d[0].tolist() == list(range(1, 151))
    scores = {}
    for j in range(1, 37):  # checklist columns; 37+ are PPI 1-6 and the global rating
        m = re.fullmatch(r"(\d+)(?:\((\d)\))?", hdr[j])
        assert m, hdr[j]
        num, lvl = int(m.group(1)), m.group(2)
        col = pd.to_numeric(d[j])
        if lvl is None:
            assert num not in scores
            scores[num] = col
        else:
            assert set(col.dropna()) <= {0, 1}
            prev = scores.get(num, pd.Series(0, index=d.index))
            assert not ((prev > 0) & (col == 1)).any()
            scores[num] = prev + col * int(lvl)
    assert sorted(scores) == list(range(1, 29))
    wide = pd.DataFrame({f"item{k:02d}": v for k, v in sorted(scores.items())})
    wide.insert(0, "id", d[0].astype(int))
    long = wide.melt(id_vars="id", var_name="item", value_name="resp").dropna(subset=["resp"])
    assert set(long["resp"]) <= {0, 1, 2, 3}
    long["resp"] = long["resp"].astype(int)
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{NAME}.csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    print(long.groupby("item")["resp"].agg(["min", "max"]).T.to_string())


if __name__ == "__main__":
    convert()
