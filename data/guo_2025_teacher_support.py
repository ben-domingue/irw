#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11779917
# DOI: 10.1038/s41598-025-88187-x
#   "The impact of teacher emotional support on learning engagement among
#   college students mediated by academic self-efficacy and academic
#   resilience" (Guo, Wang, Li & Wang, 2025), Scientific Reports 15:3670.
# Data: Supplementary Table S1, 41598_2025_88187_MOESM1_ESM.xlsx (the article's
#       only supplementary file), fetched from the Europe PMC
#       supplementaryFiles zip. One sheet: a title row, a legend row, then a
#       header row and 414 respondents x (Number, Gender, Year, Major, 47 items).
# License: CC BY 4.0 (the article and its supplementary material; Europe PMC
#          reports "cc by").
#
# Item text: available, not shipped here -- the header row carries the full
#   English wording of every item ("1.Our teachers want students in this class
#   to respect each other's ideas." ...); the legend gives the 1-5 anchors
#   (1 = Strongly Disagree, 5 = Strongly Agree). Administered in Chinese
#   (translated/back-translated, Wenjuanxing online survey, two universities in
#   western Shandong, China); the Chinese wording is not in the deposit.
#
# Tables (the legend fixes the item-to-scale mapping):
#   guo_2025_tes   Teacher Emotional Support, 15 items (legend items 1-15)
#   guo_2025_ase   Academic Self-Efficacy, 22 items (items 16-37); items 14, 16,
#                  17 and 20 are negatively worded and left as deposited
#   guo_2025_ar    Academic Resilience, 5 items (items 38-42)
#   guo_2025_le    Learning Engagement, 5 items (items 43-47)
# All items 1-5, integer, no missing cells. No exact-duplicate response rows;
# the most similar pair of respondents agrees on 42/47 items. No PII.

import io
import sys
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
ZIP_URL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11779917/"
           "supplementaryFiles")
FNAME = "41598_2025_88187_MOESM1_ESM.xlsx"

SCALES = [("tes", 15), ("ase", 22), ("ar", 5), ("le", 5)]
COVS = {"Gender": "cov_gender",   # 1 = male, 2 = female
        "Year": "cov_year",       # 1 = freshman ... 4 = senior
        "Major": "cov_major"}     # 1 humanities, 2 sci/eng, 3 social sci, 4 other


def load() -> pd.DataFrame:
    r = requests.get(ZIP_URL, headers=UA, timeout=120)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        raw = pd.read_excel(io.BytesIO(z.read(FNAME)), header=None)
    assert raw.iloc[2, 0] == "Number", raw.iloc[2, 0]
    d = raw.iloc[3:].reset_index(drop=True)
    d.columns = list(raw.iloc[2])
    return d


def convert() -> None:
    d = load()
    assert d.shape == (414, 51), d.shape
    cols = list(d.columns)
    item_src = cols[4:]
    assert len(item_src) == 47

    # ---- books ---------------------------------------------------------
    skipped = {"Number": "becomes id (row number 1..414)"}
    acc = set(skipped) | set(COVS) | set(item_src)
    assert set(cols) == acc and len(cols) == len(acc)
    for c, why in skipped.items():
        print(f"  skip {c}: {why}")

    d["id"] = pd.to_numeric(d["Number"])
    assert d["id"].is_unique
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())
    for c in cov_cols:
        d[c] = pd.to_numeric(d[c])

    # map positional source columns to scale-prefixed item names
    pos = 0
    names = []
    for name, n in SCALES:
        mapping = {}
        for k in range(1, n + 1):
            src = item_src[pos]
            assert str(src).startswith(f"{k}."), (name, k, src)
            mapping[src] = f"{name}_{k}"
            pos += 1
        sub = d[["id"] + cov_cols + list(mapping)].rename(columns=mapping)
        items = list(mapping.values())
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=items,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"])
        assert long["resp"].notna().all()
        assert (long["resp"] % 1 == 0).all()
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100

        table = f"guo_2025_{name}"
        assert table not in names
        names.append(table)
        pv = {i: {1, 2, 3, 4, 5} for i in items}
        bad = set(long["resp"]) - {1, 2, 3, 4, 5}
        assert not bad, (table, bad)
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            (table, [(f.check, f.message) for f in rep.errors])
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert pos == 47


if __name__ == "__main__":
    convert()
