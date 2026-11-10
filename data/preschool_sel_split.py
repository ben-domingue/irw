#!/usr/bin/env python3
# Source: LDbase, "Preschool Social and Emotional Development" (Bailey et al. 2023),
#   https://ldbase.org/datasets/38d4a723-c167-4908-a250-2cf29a4ff49b
# DOI (data): 10.33009/ldbase.1680213217.8ed0
# Data: child-level CT file R305A180293_child-level_CT_v35.sav (1,445 children).
# License: ODC-By (original); derived CC BY 4.0, as in biblio.csv.
#
# Builds the SEVEN preschool_sel_* tables. Until 2026-11-10 no script on record
# built them: data/preschool_sel.R (2024, CT v33) writes one combined table with
# recoded responses, and the live split tables were made some other way.
# This script reproduces the six untouched live tables EXACTLY (id, item, resp
# on every row, checked 2026-11-10 against the served tables) and so records
# how they were built:
#   * id   = row number in the .sav (the file's own childid is not used).
#   * item = the source column name, lowercased.
#   * resp = the source value as stored, missing dropped. The scored columns
#     carry the source's own codes, e.g. 0 Incorrect / 1 Similar or self
#     correct (Same Valence for EMT) / 2 Correct for DN, HTKS and EMT.
#   * a column is kept only if it has more than one distinct non-missing value
#     (the rule in preschool_sel.R; it is what drops the unused WJ items).
#   * box: the 156 cells coded 0.5 are dropped (as preschool_sel.R did).
#
# preschool_sel_akt, FIXED 2026-11-10: the live table also carried all 48 EMT
#   items -- every one of its 21,016 EMT rows identical to preschool_sel_emt --
#   so EMT was served twice and "akt" held two instruments. Here akt is its 17
#   AKT scored items only (14,506 rows), matching the source column by column.
#   Note the source's value labels on the akt*s columns read 1 Incorrect /
#   2 Same Valence / 3 Correct while the stored values are 0/1/2; the values
#   follow the EMT/DN convention, so the labels are offset by one.
#
# Run: PRESCHOOL_SEL_RAW=/path/to/R305A180293_child-level_CT_v35.sav \
#        python3 data/preschool_sel_split.py
#   (downloads the file from LDbase when the variable is unset).

import os
import re
import sys
import tempfile
import urllib.request

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://ldbase.org/system/files/datasets/2023-05/R305A180293_child-level_CT_v35.sav"
RAW = os.environ.get("PRESCHOOL_SEL_RAW")

# table -> (regex a source column must fullmatch, expected items, rows)
TABLES = {
    "preschool_sel_akt":  (r"akt\d+_\d+s_t1", 17, 14506),
    "preschool_sel_box":  (r"box[12]_\d+_t1", 20, 14234),
    "preschool_sel_dn":   (r"dn_\d+_t1", 14, 12194),
    "preschool_sel_emt":  (r"emt[ab]\d+_\d+s_t1", 48, 21016),
    "preschool_sel_htks": (r"htks1_\d+_t1", 10, 8320),
    "preschool_sel_pl":   (r"(pl|plsp)_(as|ss)\d+_t1", 39, 19036),
    "preschool_sel_wj":   (r"wj_(ap|lw)\d+_t1", 78, 28320),
}


def read_source():
    path = RAW
    if not path:
        path = os.path.join(tempfile.gettempdir(), "R305A180293_child-level_CT_v35.sav")
        if not os.path.exists(path):
            urllib.request.urlretrieve(URL, path)
    d, _ = pyreadstat.read_sav(path)
    d.columns = [c.lower() for c in d.columns]
    assert len(d) == 1445, len(d)
    d["id"] = range(1, len(d) + 1)
    return d


def build(d, name, pattern):
    cols = sorted(c for c in d.columns if re.fullmatch(pattern, c))
    v = d[cols]
    if name == "preschool_sel_box":
        assert (v == 0.5).sum().sum() == 156
        v = v.mask(v == 0.5)
    keep = [c for c in cols if v[c].dropna().nunique() > 1]
    long = (pd.concat([d[["id"]], v[keep]], axis=1)
            .melt(id_vars="id", var_name="item", value_name="resp")
            .dropna(subset=["resp"]))
    assert (long["resp"] == long["resp"].round()).all()
    long["resp"] = long["resp"].astype(int)
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    return long


def convert():
    d = read_source()
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, (pattern, n_items, n_rows) in TABLES.items():
        long = build(d, name, pattern)
        assert long["item"].nunique() == n_items, (name, long["item"].nunique())
        assert len(long) == n_rows, (name, len(long))
        checks = run_qc(long)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")
    akt_items = set(build(d, "preschool_sel_akt", TABLES["preschool_sel_akt"][0])["item"])
    emt_items = set(build(d, "preschool_sel_emt", TABLES["preschool_sel_emt"][0])["item"])
    assert not akt_items & emt_items


if __name__ == "__main__":
    convert()
