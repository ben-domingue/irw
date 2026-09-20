#!/usr/bin/env python3
"""Relationship Assessment Scale and companion measures, Polish samples.

Source: https://www.nature.com/articles/s41598-022-26653-6
DOI: 10.1038/s41598-022-26653-6
Data: https://osf.io/7hv32/ (three SPSS files: reference sample and
      validation samples 1 and 2)
License: CC BY 4.0 (Crossref; the Europe PMC core record agrees. The triage
         row read `unknown`, which was the connector defect fixed in this
         same batch -- an empty core response read as an absent licence.)

Nine tables from one deposit. The RAS is the only instrument administered to
all three samples; everything else belongs to one validation sample.

MERGED RAS, AND A CODING DIFFERENCE THAT HAD TO BE HARMONISED FIRST.
Administration is confirmed identical: the deposit's own materials document
is titled "Materials used in Reference Sample and Validation Samples 1 and 2"
and prints one Polish RAS, seven items, A-E. So the three samples merge into
one table with `cov_study`, per the same-instrument rule.

But the samples do not agree on how items 4 and 7 -- the two negatively
worded ones -- are STORED. Validation sample 1 deposits them raw (RAS4 mean
1.88) alongside explicit reverse-scored copies (RAS4_R mean 4.12,
correlation -1.0). The reference sample and validation sample 2 deposit only
one copy, and its mean (4.24, 4.15) matches the reverse-scored direction, not
the raw one -- a 2.4-point gap on the same instrument where every other item
agrees within 0.2. Merging as-deposited would put two opposite scale
directions under one item code, which is exactly the `resp_ambiguous` defect
(#1827). This script therefore takes RAS4_R/RAS7_R for validation sample 1,
so all three samples carry the same direction for every item. Nothing is
invented: the reversed columns are the depositors' own.

`id` is prefixed with the sample (`ref_1`, `val1_1`, `val2_1`) because the
three samples are independently recruited and their row numbers would
otherwise collide silently.

Item text: NOT shipped, though the wording is in hand -- the materials
document gives all seven Polish RAS stems with their A-E anchors. The reason
is the reversal above: for items 4 and 7 the shipped `resp` runs opposite to
the printed anchors, so the option text would have to be mapped in reverse
for those two items and straight for the other five. That mapping is
knowable but it is `paper_explicit`, not `data_labels`, and a wrong guess
here is the kind of defect no gate catches (the item and resp sets would
still match perfectly). It needs a Step 5b verification script. Flagged in
TODO.md as a cheap, well-specified follow-up. The SPSS files carry no
variable labels and no value labels for any item column in any of the three
files -- both levels checked, both empty -- so there was no data_labels route.
"""
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
from irw_validate.compat import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
VIEW = "53083d2e2869472490beece1b35b7294"
OSF = "https://osf.io/download/{key}/?view_only=" + VIEW
UA = {"User-Agent": "irw-batch/1.0 (research)"}

SAMPLES = {"ref": "ekj84", "val1": "8y2s6", "val2": "frg9k"}

# The RAS as each sample spells it. Items 4 and 7 take the reverse-scored
# column in val1 so every sample runs the same direction -- see the docstring.
RAS_COLS = {
    "ref":  [f"RAS{i}T1" for i in range(1, 8)],
    "val1": ["RAS1", "RAS2", "RAS3", "RAS4_R", "RAS5", "RAS6", "RAS7_R"],
    "val2": [f"RAS{i}t1" for i in range(1, 8)],
}

# Single-sample instruments: table -> (sample, columns, permitted range)
SCALES = {
    "adamczyk_2022_workbat": ("val1", [f"WorkBAT{i}" for i in range(1, 21)], (1, 5)),
    "adamczyk_2022_qri":     ("val1", [f"QRI{i}" for i in range(1, 24)], (1, 4)),
    "adamczyk_2022_fbss":    ("val1", [f"FBSS{i}" for i in range(1, 7)], (1, 5)),
    "adamczyk_2022_resta":   ("val1", [f"ReSta{i}" for i in range(1, 6)], (0, 3)),
    "adamczyk_2022_upps":    ("val1", [f"UPPS{i}" for i in range(1, 5)], (1, 4)),
    "adamczyk_2022_cesd":    ("val2", [f"CESD{i}t1" for i in range(1, 21)], (0, 3)),
    "adamczyk_2022_mhc_sf":  ("val2", [f"MHC_SF_{i}t1" for i in range(1, 15)], (0, 5)),
    "adamczyk_2022_selsa":   ("val2", [f"SELSA{i}t1" for i in (3, 6, 10, 14, 15)], (1, 7)),
}
# CESD16 is spelled "CSED16t1" in the deposit -- a typo in the column name,
# not a different item. Patched at load rather than shipped misspelled.
COL_FIXES = {"val2": {"CSED16t1": "CESD16t1"}}

COVS = {
    "ref":  {"AgeT1": "cov_age", "GenderT1": "cov_gender"},
    "val1": {"Age": "cov_age", "Gender": "cov_gender"},
    "val2": {"aget1": "cov_age", "sext1": "cov_gender"},
}


def load() -> dict:
    out = {}
    for name, key in SAMPLES.items():
        r = requests.get(OSF.format(key=key), headers=UA, timeout=180)
        r.raise_for_status()
        path = Path(f"/tmp/irw_{name}.sav")
        path.write_bytes(r.content)
        df, meta = pyreadstat.read_sav(str(path))
        df = df.rename(columns=COL_FIXES.get(name, {}))
        df = df.reset_index(drop=True)
        df.insert(0, "id", [f"{name}_{i + 1}" for i in df.index])
        out[name] = (df, meta)
        path.unlink()
    return out


def tidy(wide, item_cols, cov_map, rename=None, extra=None):
    cov = {k: v for k, v in cov_map.items() if k in wide.columns}
    block = wide[["id"] + item_cols + list(cov)].rename(columns=cov)
    if rename:
        block = block.rename(columns=rename)
        item_cols = [rename.get(c, c) for c in item_cols]
    cov_cols = list(cov.values())
    long = block.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                      var_name="item", value_name="resp")
    if extra:
        for k, v in extra.items():
            long[k] = v
        cov_cols = list(extra) + cov_cols
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    return long[["id", "item", "resp"] + cov_cols], cov_cols


def finish(long, table, cov_cols, lo, hi, min_items):
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert long["resp"].between(lo, hi).all(), f"{table}: resp outside {lo}-{hi}"
    assert not long.duplicated(["id", "item"]).any(), f"{table}: duplicate id/item"
    assert long["id"].nunique() >= 100, f"{table}: below the 100-id floor"
    assert long["item"].nunique() == min_items, f"{table}: item count changed"
    assert long["item"].nunique() > 1, f"{table}: single-item table"
    bad = [c for c in run_qc(long) if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{table}.csv", index=False)
    print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


def convert() -> None:
    data = load()

    # ---- the merged RAS -------------------------------------------------
    frames, cov_cols = [], None
    for sample, cols in RAS_COLS.items():
        df, _ = data[sample]
        missing = [c for c in cols if c not in df.columns]
        assert not missing, f"{sample}: missing RAS columns {missing}"
        canon = {src: f"RAS{i}" for i, src in enumerate(cols, start=1)}
        long, cov_cols = tidy(df, cols, COVS[sample], rename=canon,
                              extra={"cov_study": sample})
        frames.append(long)
    ras = pd.concat(frames, ignore_index=True)
    assert ras["id"].nunique() == sum(len(data[s][0]) for s in SAMPLES), "ids collided"
    finish(ras, "adamczyk_2022_ras", cov_cols, 1, 5, 7)

    # ---- one table per single-sample instrument -------------------------
    for table, (sample, cols, (lo, hi)) in SCALES.items():
        df, _ = data[sample]
        missing = [c for c in cols if c not in df.columns]
        assert not missing, f"{table}: missing columns {missing}"
        canon = {src: src.replace("t1", "").replace("_R", "") for src in cols}
        long, covs = tidy(df, cols, COVS[sample], rename=canon)
        finish(long, table, covs, lo, hi, len(cols))


if __name__ == "__main__":
    convert()
