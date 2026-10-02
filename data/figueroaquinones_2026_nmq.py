#!/usr/bin/env python3
# Source: https://zenodo.org/records/20431627
# DOI: 10.1186/s12891-026-10426-7
#   Figueroa-Quiñones, Fernandini-Valenzuela, Cordova-Gutierrez, Vargas-Prado,
#   Aquije-Cardenas et al. (2026). "Psychometric properties of the Peruvian
#   version of the Nordic Musculoskeletal Questionnaire (NMQ)." BMC
#   Musculoskeletal Disorders. (Deposit: Figueroa-Quiñones, Joel, Zenodo
#   20431627, "Dataset psychometric NMQ peruvian version".)
# Data: Zenodo 20431627, "dataset.xlsx" (1,215 rows x 24 columns; Peruvian
#   adults, mean age 22.7, 73.0% women -- matches the paper's abstract).
# License: CC BY 4.0 (Zenodo record licence; the article is CC BY 4.0 too).
#
# Item text: not shipped. The workbook has only column codes (N1-N9, A1, ...)
#   -- no labels at either level (xlsx has no variable or value labels), and
#   the deposit has no codebook. The wording is in the published instruments:
#   the NMQ's nine body regions (Kuorinka et al. 1987; Peruvian Spanish
#   translation in the paper), PHQ-2/GAD-2 and the Jenkins Sleep Scale.
#
# Tables (item codes are the source column names):
#   figueroaquinones_2026_nmq    9 items, 0/1  NMQ symptom presence in nine
#                                 body regions (NMQ = sum of N1-N9, asserted)
#   figueroaquinones_2026_phq4   4 items, 0-3  PHQ-4: A1-A2 = PHQ-2
#                                 (depressive symptoms; the file's PHQ-2 column
#                                 = A1 + A2, asserted) and B1-B2 = GAD-2
#                                 (anxiety; "GAT-2" = B1 + B2, asserted). The
#                                 paper uses them as the anxiety and
#                                 depression validity criteria. Shipped as one
#                                 PHQ-4 table rather than two 2-item tables:
#                                 same 0-3 frequency format and time frame.
#   figueroaquinones_2026_jss4   4 items, 1-6  Jenkins Sleep Scale-4, the
#                                 paper's sleep-problems criterion (JSS-4 =
#                                 sum, asserted). The JSS has six frequency
#                                 options, published as 0-5; this file codes
#                                 them 1-6 (sum range 4-24), shipped as coded.
#
# Dropped as items: PHQ-2, GAT-2, JSS-4, NMQ (authors' sum scores).
# id: row index. The file's ID column (1-1218, unique, 3 gaps) is a study
#   serial number and is not carried. No PII: no names, contacts, dates of
#   birth, locations or free text.
# Covariates: cov_age, cov_sex (1 male, 2 female; 887 of 1,215 are 2, the
#   paper's 73.0% women).

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/20431627/files/dataset.xlsx/content"

TABLES = {
    "figueroaquinones_2026_nmq": ([f"N{i}" for i in range(1, 10)],
                                  range(0, 2)),
    "figueroaquinones_2026_phq4": (["A1", "A2", "B1", "B2"], range(0, 4)),
    "figueroaquinones_2026_jss4": ([f"J{i}" for i in range(1, 5)],
                                   range(1, 7)),
}
SUMS = {"NMQ": [f"N{i}" for i in range(1, 10)], "PHQ-2": ["A1", "A2"],
        "GAT-2": ["B1", "B2"], "JSS-4": [f"J{i}" for i in range(1, 5)]}
COVS = {"AGE": "cov_age", "SEX": "cov_sex"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = load()
    assert d.shape == (1215, 24), d.shape
    assert d["ID"].is_unique
    for total, items in SUMS.items():
        assert (d[total] == d[items].sum(axis=1)).all(), total
    assert (d["SEX"] == 2).sum() == 887

    d = d.rename(columns=COVS).reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    cov_cols = list(COVS.values())

    # Balance the books.
    shipped = {c for items, _ in TABLES.values() for c in items}
    accounted = shipped | set(SUMS) | set(cov_cols) | {"id", "ID"}
    assert set(d.columns) == accounted, set(d.columns) ^ accounted

    names = []
    for table, (items, allowed) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - set(allowed)
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(items) > 1
        pv = {i: set(allowed) for i in items}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
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
