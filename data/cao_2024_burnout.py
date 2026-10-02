#!/usr/bin/env python3
# Source: https://zenodo.org/records/12788010
# DOI: none for this sample.
#   Deposit: Cao, B. (2024). THE EFFECT OF SOCIAL SUPPORT ON BURNOUT AMONG
#   CHINESE UNIVERSITY LECTURERS [Data set]. Zenodo.
#   https://doi.org/10.5281/zenodo.12788010
#   Instrument documentation (a DIFFERENT sample by the same author): Cao, B.,
#   Hassan, N. C., & Omar, M. K. (2025). The Impact of Work Stress and
#   Perceived Social Support on Burnout Dimensions Among Chinese University
#   Lecturers. International Journal of Social Science Research, 13(2).
#   https://doi.org/10.5296/ijssr.v13i2.22683 (CC BY 4.0, read in full).
#   That paper is not this file: it reports 326 lecturers from ONE university
#   (Shanxi Medical University, data July 10 - August 31 2024, 192 women),
#   whereas this deposit was published 2024-07-20, has 181 women, and spans
#   three university types (Q5). Same author, same three instruments, same N.
#   It is used only for what the instruments are and how they are scored.
# Data: dataset.sav (326 rows x 76 columns; Chinese university lecturers).
# License: CC BY 4.0 (Zenodo API).
#
# Item text: not shipped. Both label levels checked: no variable labels on any
#   item and no value labels on any item (value labels exist only on the
#   Q1-Q7 demographics, in Chinese). Stems are in the published MBI-ES,
#   MSPSS and Li (2005) College Teacher Work Stress Rating Scale.
#
# Tables (item codes are the source column names):
#   cao_2024_work_stress  worksecurity1-8, teachingquarantee1-5 (sic),
#       interpersonalrelationships1-4, workload1-3, jobdemanding1-4: the
#       24-item College Teacher Work Stress Rating Scale (Li 2005), 1 "no
#       stress at all" .. 4 "the most stressful event" per the paper.
#   cao_2024_mbi  emotionalexhaustion1-9, depersonalization1-5,
#       personalaccomplishment1-8: the 22-item Maslach Burnout Inventory
#       (Educators Survey). The paper describes a 7-point 1-7 frequency
#       scale, but every one of the 22 items in this file uses exactly 1-5,
#       so the administered format here is undocumented: NO permitted set is
#       asserted (values checked to be whole numbers only).
#   cao_2024_mspss  familysupport1-4, friendssupport1-4,
#       significantothersupport1-4: the 12-item MSPSS, 1-7 per the paper.
#   Each block's composite column equals the row mean of its items
#   (asserted), so items are stored as answered and no item is reversed.
#
# Dropped: the 11 subscale-mean composites.
# id: row index (no respondent id in the file).
# Covariates (codes as value-labelled in Chinese): cov_gender (1 female,
#   2 male), cov_age_band (1 25-30, 2 31-35, 3 36-40, 4 41-45),
#   cov_education (1 bachelor, 2 master, 3 doctorate, 4 doctoral student),
#   cov_marital (1 single, 2 married, 3 divorced), cov_university_type
#   (1 "double first-class", 2 first-tier, 3 second-tier), cov_income_band
#   (1 4000-5000 .. 4 7000-8000 RMB), cov_teaching_years_band (1 6 months-1
#   year .. 5 16-20 years).

import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/12788010/files/dataset.sav/content"

BLOCKS = {
    "worksecurity": 8, "teachingquarantee": 5,
    "interpersonalrelationships": 4, "workload": 3, "jobdemanding": 4,
    "emotionalexhaustion": 9, "depersonalization": 5,
    "personalaccomplishment": 8,
    "familysupport": 4, "friendssupport": 4, "significantothersupport": 4,
}


def items(*blocks):
    return [f"{b}{i}" for b in blocks for i in range(1, BLOCKS[b] + 1)]


TABLES = {
    "cao_2024_work_stress": items("worksecurity", "teachingquarantee",
                                  "interpersonalrelationships", "workload",
                                  "jobdemanding"),
    "cao_2024_mbi": items("emotionalexhaustion", "depersonalization",
                          "personalaccomplishment"),
    "cao_2024_mspss": items("familysupport", "friendssupport",
                            "significantothersupport"),
}
DOCUMENTED = {"cao_2024_work_stress": set(range(1, 5)),
              "cao_2024_mspss": set(range(1, 8))}
COVS = {"Q1": "cov_gender", "Q2": "cov_age_band", "Q3": "cov_education",
        "Q4": "cov_marital", "Q5": "cov_university_type",
        "Q6": "cov_income_band", "Q7": "cov_teaching_years_band"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (326, 76), d.shape

    item_cols = [c for its in TABLES.values() for c in its]
    known = set(item_cols) | set(BLOCKS) | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert len(item_cols) == len(set(item_cols)) == 58
    for b, k in BLOCKS.items():
        its = [f"{b}{i}" for i in range(1, k + 1)]
        assert np.allclose(d[its].mean(axis=1), d[b]), b
    assert not d.duplicated().any()
    assert not d.T.duplicated().any()
    assert not any(meta.column_names_to_labels.get(c) for c in item_cols)
    assert not any(c in meta.variable_value_labels for c in item_cols)
    # The MBI block never leaves 1-5 although the paper describes 1-7.
    assert set(np.unique(d[TABLES["cao_2024_mbi"]])) == {1, 2, 3, 4, 5}

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, its in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        pv = None
        if table in DOCUMENTED:
            allowed = DOCUMENTED[table]
            for it, g in long.groupby("item"):
                bad = set(g["resp"]) - allowed
                assert not bad, (table, it, bad)
            pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long, permitted_values=pv) if pv else run_qc(long)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        ctx = {"permitted_values": pv} if pv else None
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context=ctx)
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
