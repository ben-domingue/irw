#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10624169
# DOI: 10.7717/peerj.15871
#   "The impact of core self-evaluation on school adaptation of high school
#   students after their return to school during the COVID-19 pandemic: the
#   parallel mediation of positive and negative coping styles" (Wang, Duan,
#   Han, Huang, Wang & Wang, 2023), PeerJ 11:e15871.
# Data: Supplemental File peerj-11-15871-s001.xlsx (500 x 68), fetched from the
#       Europe PMC supplementaryFiles zip. s002.docx is the "variable
#       assignment table" (anchor labels per scale). 500 students at one senior
#       high school in Changzhou, Jiangsu, paper-and-pencil, 2020.
# License: CC BY 4.0 (PeerJ article and supplements; Europe PMC "cc by").
#
# Item text: not shipped. The workbook has bare codes (CSE1.., SA1..,
#   Coping1..); no variable or value labels exist (xlsx). s002.docx gives the
#   anchor labels only (English): CSE and SA "1=completely inconsistent ..
#   5=completely consistent", coping "0=not taken .. 3=frequently taken". The
#   stems are in the Chinese instruments cited by the paper: CSES (Du, Zhang &
#   Zhao 2012), Simplified Coping Style Questionnaire (Xie 1998), School
#   Adaptation Questionnaire (Cui 2008). Not in the deposit.
#
# Tables:
#   wang_2023_cse            Core Self-Evaluation Scale, Chinese revision,
#                            CSE1-10, 1-5. Item sum == the file's CSE total on
#                            every row, so the items are as scored (the paper
#                            says some items are reverse-scored).
#   wang_2023_school_adapt   School Adaptation Questionnaire (Cui 2008),
#                            SA1-27, 1-5
#   wang_2023_scsq           Simplified Coping Style Questionnaire, Coping1-20,
#                            0-3; items 1-12 sum to "Positive", 13-20 to
#                            "Negative" on every row (asserted).
# Skipped: CSE, SA, the five SA subscale totals, Positive, Negative (composites).
# id: row index (the file has no id column). Covariates: gender (1 male,
#   2 female), age. No PII. 5 rows share their 57-item pattern with another
#   row; all are two-valued near-straight-line patterns, read as chance.

import io
import sys
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ZIP_URL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10624169/"
           "supplementaryFiles")
FNAME = "peerj-11-15871-s001.xlsx"
COVS = {"GENDER": "cov_gender", "AGE": "cov_age"}
SCALES = {
    "wang_2023_cse": ([f"CSE{i}" for i in range(1, 11)], range(1, 6)),
    "wang_2023_school_adapt": ([f"SA{i}" for i in range(1, 28)], range(1, 6)),
    "wang_2023_scsq": ([f"Coping{i}" for i in range(1, 21)], range(0, 4)),
}
SKIP = {c: "composite score" for c in
        ["CSE", "SA", "School a", "Peer r", "Tchstu r", "Academic a",
         "Conwentional a", "Positive", "Negative"]}


def fetch_zip() -> bytes:
    for attempt in range(6):
        try:
            r = requests.get(ZIP_URL, headers=UA, timeout=300)
            r.raise_for_status()
            return r.content
        except requests.RequestException:
            if attempt == 5:
                raise
            time.sleep(20 * (attempt + 1))


def convert() -> None:
    with zipfile.ZipFile(io.BytesIO(fetch_zip())) as z:
        d = pd.read_excel(io.BytesIO(z.read(FNAME)))
    assert d.shape == (500, 68), d.shape
    acc = set(COVS) | set(SKIP)
    for items, _ in SCALES.values():
        acc |= set(items)
    assert set(d.columns) == acc and len(d.columns) == len(acc)
    for c, why in SKIP.items():
        print(f"  skip {c}: {why}")
    cse = SCALES["wang_2023_cse"][0]
    cp = SCALES["wang_2023_scsq"][0]
    assert (d[cse].sum(axis=1) == d["CSE"]).all()
    assert (d[cp[:12]].sum(axis=1) == d["Positive"]).all()
    assert (d[cp[12:]].sum(axis=1) == d["Negative"]).all()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())
    assert len(set(SCALES)) == len(SCALES)
    total = 0
    for table, (items, allowed) in SCALES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        assert long["resp"].notna().all()
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].isin(list(allowed)).all()
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        pv = {i: set(allowed) for i in items}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        total += len(long)
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert total == 500 * 57


if __name__ == "__main__":
    convert()
