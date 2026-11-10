#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/PETWZF
# DOI (data): 10.7910/DVN/PETWZF
# DOI (paper): 10.3352/jeehp.2018.15.14
# Data: Seo, D. G., & Choi, J. (2018). Post-hoc simulation study of computerized
#   adaptive testing for the Korean Medical Licensing Examination. Journal of
#   Educational Evaluation for Health Professions, 15, 14. Harvard Dataverse
#   file "Jeehp_15_14_raw data.txt": the scored item responses of the January
#   2017 Korean Medical Licensing Examination (KMLE) written test, 3,259
#   examinees x 360 items, tab-separated, no header, no id column.
# Q-matrix: Choi, Y., & Seo, D. G. (2020). Estimation of item parameters and
#   examinees' mastery probability in each domain of the KMLE using a DINA
#   model. JEEHP, 17, 35. https://doi.org/10.7910/DVN/X2DRTE, "Dataset 2. Q
#   matrix data.csv" (360 x 8). That deposit's "Dataset 1" is the same raw file
#   byte for byte (md5 719b2a50d341bb801fc832c2617f5af0), and the paper names
#   PETWZF as its source, so the table cites the original deposit.
# License: CC0 1.0 on both deposits, verified via the Dataverse API
#   (latestVersion.license). Both papers CC BY 4.0. The data come from the
#   Korea Health Personnel Licensing Examination Institute, which publishes
#   JEEHP; the 2020 paper's ethics statement says the open file holds no
#   identifying information about the examinees.
#
# Found by the repos sweep of 2026-11-10 (lane C, "medical licensing
#   examination"; the triage reached it through X2DRTE as worth_retrying).
#
# ONE output table:
#   seo_2018_kmle  item_001..item_360, scored 0/1 (1 = correct; mean p = .72,
#     matching the "high-stakes exam" difficulty the papers report). No missing
#     cells: every examinee has all 360 items.
#   qmatrix1..qmatrix8 = the deposit's 8 content domains C1..C8 (Table 1 of
#     the 2020 paper: 45, 45, 45, 25, 154, 20, 20, 6 items). Each item loads on
#     exactly one domain. The papers do not name the domains.
# `id` is the row index (the file has no id column). No covariates exist.
# Item codes are positional (item_001 = column 1 of the file = row 1 of the
#   Q-matrix = Item ID 1 in the 2020 paper's Table 3).
#
# Item text: NOT SHIPPED. The KMLE items are secure licensing-exam items; no
#   deposit or paper prints them.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RAW_URL = "https://dataverse.harvard.edu/api/access/datafile/3157422?format=original"
QMAT_URL = "https://dataverse.harvard.edu/api/access/datafile/4271747?format=original"


def fetch(url):
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    return r.content


def convert():
    raw = pd.read_csv(io.BytesIO(fetch(RAW_URL)), sep="\t", header=None)
    raw = raw.dropna(axis=1, how="all")
    assert raw.shape == (3259, 360), raw.shape
    q = pd.read_csv(io.BytesIO(fetch(QMAT_URL)), header=None)
    assert q.shape == (360, 8), q.shape
    assert (q.sum(axis=1) == 1).all()
    assert q.sum().tolist() == [45, 45, 45, 25, 154, 20, 20, 6]

    items = [f"item_{i:03d}" for i in range(1, 361)]
    raw = raw.copy()
    raw.columns = items
    raw.insert(0, "id", range(1, len(raw) + 1))
    long = raw.melt(id_vars="id", var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {0, 1}
    q.index = items
    qcols = [f"qmatrix{a}" for a in range(1, 9)]
    q.columns = qcols
    long = long.merge(q, left_on="item", right_index=True, how="left")
    assert long[qcols].notna().all().all()
    long = long.sort_values(["id", "item"])[["id", "item", "resp"] + qcols]
    assert not long.duplicated(["id", "item"]).any()

    checks = run_qc(long[["id", "item", "resp"]], permitted_values={c: [0, 1] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")

    name = "seo_2018_kmle"
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
