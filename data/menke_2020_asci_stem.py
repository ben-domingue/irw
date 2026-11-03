#!/usr/bin/env python3
# Source: https://doi.org/10.6071/M3T09X (Dryad), mirrored at
#   https://zenodo.org/records/4394240
# DOI: 10.6071/M3T09X (data); preprint 10.26434/chemrxiv.13180115
# Paper: Chang J, Menke E (2020-2022). Measuring attitude towards chemistry,
#   biology, and math at a Hispanic-serving institution. ChemRxiv preprint.
# Data: six Qualtrics exports from UC Merced general-chemistry courses: a
#   semester-start ("Presurvey") and semester-end ("Postsurvey") file for
#   Spring 2019, Fall 2019 and Spring 2020.
# License: CC0 1.0 (verified on the Dryad/Zenodo record).
#
# Found by the automated_finding repos sweep of 2026-11-02 (mode 3), worked
# from leads/repos_leads_2026-11-02.csv the same day (BATCH_LOG.md).
#
# THREE output tables, one per subject, each the same 20 semantic-differential
# pairs ("Chemistry is... Easy:Hard", ...), the ASCI item set:
#   menke_2020_asci_chemistry  Q1_1..Q1_20
#   menke_2020_asci_biology    Q34_1..Q34_20
#   menke_2020_asci_math       Q32_1..Q32_20
# resp is the 1-7 position as exported by Qualtrics, 1 = the LEFT adjective of
#   the pair in the column's own header (e.g. Q1_1 1 = Easy .. 7 = Hard). The
#   pairs mix polarity, so items are NOT all keyed the same way. The direction
#   is confirmed on the data: "Worthless:Beneficial" averages 5.7 and
#   "Good:Bad" 2.7 in every semester.
# ONLY THE THREE SEMESTER-START FILES SHIP, stacked with cov_semester. The
#   exports carry no respondent identifier, so a semester-end response cannot
#   be linked to the same student's semester-start response; shipping both
#   would put the same students in twice under different ids. A student who
#   took the survey in two semesters is likewise two ids here.
# Rows dropped: anyone whose consent item (Q35) is present and not 1 (the
#   Fall 2019 export leaves Q35 blank for everyone), and rows with no answers.
# No covariates beyond semester: the exports carry none.
# `id` is a running index over the stacked semester-start files.
#
# Item text: not shipped. The pair wording is in every column header, but the
#   item set is Bauer's (2008) Attitude toward the Subject of Chemistry
#   Inventory (J. Chem. Educ. 85:1440), whose rights terms have not been read.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW_DIR = os.environ.get("MENKE_RAW_DIR", ".")
FILES = [("2019S_Presurvey.xlsx", "2019 spring"), ("2019F_Presurvey.xlsx", "2019 fall"),
         ("2020S_Presurvey.xlsx", "2020 spring")]
BLOCKS = {"chemistry": ("Q1_", "Chemistry is"), "biology": ("Q34_", "Biology is"), "math": ("Q32_", "Math is")}
ALL_ITEMS = [f"{p}{k}" for p, _ in BLOCKS.values() for k in range(1, 21)]
PAIRS = {}  # (prefix, k) -> "Left:Right", asserted identical across the three exports


def load():
    frames = []
    for fn, sem in FILES:
        raw = pd.read_excel(os.path.join(RAW_DIR, fn), header=0)
        hdr = raw.iloc[0]
        for p, stem in BLOCKS.values():
            for k in range(1, 21):
                h = str(hdr[f"{p}{k}"])
                assert stem in h, (fn, p, k)
                pair = h.rsplit(stem, 1)[1].lstrip(" -…").strip()
                PAIRS.setdefault((p, k), pair)
                assert PAIRS[(p, k)] == pair, (fn, p, k, pair, PAIRS[(p, k)])
        d = raw.iloc[1:].copy()
        cols = set(d.columns) - {"Unnamed: 0"}
        assert cols == set(ALL_ITEMS) | {"Q35"}, (fn, cols ^ (set(ALL_ITEMS) | {"Q35"}))
        txt = [c for c in d.columns if c != "Q35" and pd.api.types.is_string_dtype(d[c])]
        print(f"PII screen {fn}: {len(txt)} text columns of {len(d.columns)} examined (item columns only otherwise)")
        q35 = pd.to_numeric(d["Q35"], errors="coerce")
        d = d[q35.isna() | (q35 == 1)]
        v = d[ALL_ITEMS].apply(pd.to_numeric, errors="raise")
        v = v[v.notna().any(axis=1)]
        v["cov_semester"] = sem
        frames.append(v)
        print(f"  {fn}: {len(v)} respondents kept")
    out = pd.concat(frames, ignore_index=True)
    out["id"] = range(1, len(out) + 1)
    return out


def convert():
    df = load()
    tables = {}
    for subj, (p, _) in BLOCKS.items():
        items = [f"{p}{k}" for k in range(1, 21)]
        long = df[["id", "cov_semester"] + items].melt(id_vars=["id", "cov_semester"], var_name="item",
                                                        value_name="resp")
        long = long.dropna(subset=["resp"])
        assert set(long["resp"]) <= set(range(1, 8))
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp", "cov_semester"]]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(range(1, 8)) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {subj} {c.name}: {c.detail[:160]}")
        tables[f"menke_2020_asci_{subj}"] = long
    assert len(tables) == 3
    os.makedirs(OUT_DIR, exist_ok=True)
    for t, long in tables.items():
        long.to_csv(os.path.join(OUT_DIR, f"{t}.csv"), index=False)
        print(f"{t}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
