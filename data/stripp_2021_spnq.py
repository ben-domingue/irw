#!/usr/bin/env python3
# Source: https://zenodo.org/records/5524334
# DOI: 10.1007/s10943-022-01533-5
#   Stripp, T. A., Büssing, A., Wehberg, S., Andersen, H. S., et al. (2023).
#   "Measuring Spiritual Needs in a Secular Society: Validation and
#   Clinimetric Properties of the Danish 20-Item Spiritual Needs
#   Questionnaire." Journal of Religion and Health, 61, 3542-3565. (Springer
#   bot-walls automated fetches; read 2026-10-02 from a PDF Ben supplied.)
#   N = 325, recruited through social media and a medical-school learning
#   platform (June 2021), split at random into halves A and B for EFA/CFA.
#   Deposit: Stripp, T. A. (2021). "Dataset used for validation of the Danish
#   20-item Spiritual Needs Questionnaire." Zenodo.
# Data: Zenodo 5524334, Dataset_full_anonymized_SpNQ+WHO5.xls (325 rows x 25
#       columns; Danish adult convenience sample, many university students).
#       The deposit's sampleA (165) and sampleB (160) files are the two random
#       halves of the full file: their row multisets add up to it exactly
#       (asserted), so only the full file ships.
# License: CC BY 4.0 (Zenodo record metadata).
#
# Item text: not shipped. The .xls has no label levels at all (plain
#   headers n2..n27, w5_1..w5_5; no value labels). Lead: the paper's
#   Appendix 1 prints the DA-SpNQ-20 in Danish with English in italics,
#   item by item under the same codes N2..N27, with the four anchors
#   (Nej/No, Lille/Small, Stort/Large, Meget stort/Very large = 0-3). That
#   is a paper_explicit mapping keyed by item number, so it needs a
#   verify_<table>.R. WHO-5 wording is the published Danish WHO-5.
#
# Tables (item codes are the source column names):
#   stripp_2021_spnq  20 items (n2 .. n27, the SpNQ's own item numbers), 0-3.
#                     Response set from the paper: "4-point scale from no
#                     need to a very strong need (0-no, 1-yes, 2-strong,
#                     3-very strong)"; Appendix 1 anchors 0 Nej .. 3 Meget
#                     stort. Every item was forced-response.
#   stripp_2021_who5   5 items, 0-5. Paper: "6-point scale from 0-never to
#                     5-all the time" (Topp et al. 2015).
#
# Cleaning: none needed -- no missing cells, all values whole and inside the
#   documented sets.
# Dropped: nothing (no composites in the file).
# id: row index (the file has no respondent id; age, gender and
#   denomination were stripped by the depositor).
# Covariates: none.

import os
import sys
import tempfile
from collections import Counter
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BASE = "https://zenodo.org/api/records/5524334/files/{}/content"
FULL = "Dataset_full_anonymized_SpNQ+WHO5.xls"
HALVES = ["Dataset_sampleA_anonymized_SpNQ+WHO5.xls",
          "Dataset_sampleB_anonymized_SpNQ+WHO5.xls"]

SPNQ = [f"n{i}" for i in (2, 5, 6, 7, 8, 10, 11, 12, 14, 15, 16, 17, 18, 19,
                          20, 21, 22, 23, 26, 27)]
WHO5 = [f"w5_{i}" for i in range(1, 6)]
TABLES = {
    "stripp_2021_spnq": (SPNQ, range(0, 4)),
    "stripp_2021_who5": (WHO5, range(0, 6)),
}


def load(name):
    r = requests.get(BASE.format(name), headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".xls", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        return pd.read_excel(path)
    finally:
        os.unlink(path)


def rows(df):
    return Counter(map(tuple, df.values.tolist()))


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = load(FULL)
    assert d.shape == (325, 25), d.shape
    a, b = (load(h) for h in HALVES)
    assert list(a.columns) == list(b.columns) == list(d.columns)
    assert rows(d) == rows(a) + rows(b)  # halves partition the full file

    # Balance the books.
    items = SPNQ + WHO5
    assert set(d.columns) == set(items), set(d.columns) ^ set(items)
    assert not d.isna().any().any()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)

    names = []
    for table, (its, allowed) in TABLES.items():
        long = d.melt(id_vars=["id"], value_vars=its, var_name="item",
                      value_name="resp")
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        allowed = set(allowed)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"]]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
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
