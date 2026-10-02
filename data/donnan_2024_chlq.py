#!/usr/bin/env python3
# Source: https://doi.org/10.5683/SP3/WM4BDU
# DOI: 10.1186/s12889-025-23770-5
#   Jacques, Donnan, Bishop, Howells, Gao & Najafizada (2025). "Development of
#   a cannabis health literacy questionnaire: preliminary validation using the
#   Rasch model." BMC Public Health 25, 2539.
# Data: Borealis (Scholars Portal Dataverse) 10.5683/SP3/WM4BDU (Donnan,
#       Jaques, Bishop, Howells & Najafizada, 2024), "CHLQ_RaschDataset_Feb2024"
#       downloaded with ?format=original (.xlsx, 1,035 rows x 34 columns; one
#       sheet "CHLQ_AngusReid_CanadaWide_Mar28"). Canadian adults recruited
#       through the Angus Reid Forum and social media ads, 2022-09 to 2023-03,
#       in English. The deposit's README and CHLQ_Codebook_2023.docx document
#       every item and both response formats.
# License: CC0 1.0 (Dataverse dataset metadata).
#
# Item text: not shipped, but cheap. The .xlsx has no labels (no variable or
#   value labels are possible in this format; headers are codes only), but
#   CHLQ_Codebook_2023.docx in the same deposit gives the full stem for all
#   32 codes plus both scales ("0 = Not correct, 1 = Correct, 0 = I don't
#   know" for KC/UHR; 1 Strongly Disagree .. 5 Strongly Agree for KR/SAU).
#   The multiple-choice options for KC/UHR are not in the codebook.
#
# Tables:
#   donnan_2024_chlq   32 items  Cannabis Health Literacy Questionnaire, one
#                       instrument in four dimensions:
#                         KC1-KC10  knowledge of cannabis, 0/1 (scored correct;
#                                   "I don't know" scored 0)
#                         KR1-KR12  knowledge of risks, 1-5 agreement
#                         UHR1-UHR6 understanding of risks and harms, 0/1
#                         SAU1-SAU4 seek/access/use information, 1-5
#                       The paper fits all 32 jointly as one Rasch model, so
#                       they ship as one table. KC9 was dropped from the final
#                       questionnaire (codebook note) but was administered,
#                       so it is kept. Multiple-choice items are already
#                       scored correct/incorrect in the deposit; the chosen
#                       option is not available.
#
# Dropped as items:
#   - KR7_RE, KR8_RE: reverse-coded copies of KR7/KR8 (KR + KR_RE = 6 in every
#     row, asserted). The raw KR7/KR8 ship; the README names KR7 and KR8 as the
#     reverse-keyed items.
# Missing: a few cells per item hold the string "#MISSING!" (an Excel error
#   value; the README says missing data are left missing). They become NA and
#   are dropped from the long file.
#
# id: row index. There are no identifier, covariate or free-text columns.

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
URL = "https://borealisdata.ca/api/access/datafile/717552?format=original"

TABLE = "donnan_2024_chlq"
BINARY = [f"KC{i}" for i in range(1, 11)] + [f"UHR{i}" for i in range(1, 7)]
LIKERT = [f"KR{i}" for i in range(1, 13)] + [f"SAU{i}" for i in range(1, 5)]
ITEMS = [f"SAU{i}" for i in range(1, 5)] + [f"KC{i}" for i in range(1, 11)] \
    + [f"KR{i}" for i in range(1, 13)] + [f"UHR{i}" for i in range(1, 7)]
ALLOWED = {**{i: {0, 1} for i in BINARY}, **{i: {1, 2, 3, 4, 5} for i in LIKERT}}
DROPPED = ["KR7_RE", "KR8_RE"]


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name=0)


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = load()
    assert d.shape == (1035, 34), d.shape
    assert set(d.columns) == set(ITEMS) | set(DROPPED), \
        set(d.columns) ^ (set(ITEMS) | set(DROPPED))
    assert len(ITEMS) == 32 and set(ALLOWED) == set(ITEMS)

    # The only non-numeric cell value anywhere is the Excel error string.
    for c in d.columns:
        txt = {v for v in d[c] if isinstance(v, str)}
        assert txt <= {"#MISSING!"}, (c, txt)
    d = d.replace("#MISSING!", pd.NA).apply(pd.to_numeric)
    for k in (7, 8):
        both = d[[f"KR{k}", f"KR{k}_RE"]].dropna()
        assert ((both[f"KR{k}"] + both[f"KR{k}_RE"]) == 6).all(), k

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    long = d.melt(id_vars=["id"], value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - ALLOWED[it]
        assert not bad, (it, bad)
    long = long[["id", "item", "resp"]]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 32

    pv = {i: set(v) for i, v in ALLOWED.items()}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
