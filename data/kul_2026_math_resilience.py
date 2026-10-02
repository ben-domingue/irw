#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.30384058.v3
# DOI: none yet. The deposit's README_Codebook names the manuscript "Math
#   Anxiety and Everyday Resilience in High-Stakes Contexts: Parallel
#   Mediation via Mathematics Self-Concept and Self-Efficacy" (Humanities and
#   Social Sciences Communications) and says the data were "shared for peer
#   review"; Crossref found no published version as of 2026-10-02.
#   Dataset: Kul, U., Celik Demirci, S., & Korkmaz, S. (2026). Math Anxiety
#   and Everyday Resilience in High-Stakes Contexts. figshare.
# Data: figshare file 67729404, Data.sav (443 rows x 20 columns; Turkish
#       middle-school students), with README_Codebook (1).pdf (file 67746372).
# License: CC BY 4.0 (figshare API).
#
# Tables (item codes are the source column names). Per the codebook, "All
# Likert-type items use a 5-point response format (1 = Strongly
# Disagree/Low, 5 = Strongly Agree/High)", so {1..5} is asserted for every
# item. Each block's total (SCTop, SETop, ABTop) is the plain sum of its four
# items (asserted; ABTop includes the AB4 fill described below).
#   kul_2026_math_self_concept   MCS1, MSC2, MSC3, MSC4  mathematics
#       self-concept, adapted from Marsh (1990); 4 of the original 6 items
#       (codebook note). The first code is spelled MCS1 in the source.
#   kul_2026_math_self_efficacy  MSE1-MSE4  adapted from the PISA 2003
#       mathematics self-efficacy items.
#   kul_2026_academic_buoyancy   AB1-AB4  Academic Buoyancy Scale (Martin &
#       Marsh 2008), Turkish adaptation.
#   AB4 holds five identical non-integer cells (3.38104089) on a 1-5 item: a
#   mean fill (it is not the mean of AB4's integer cells, 3.438, so it was
#   computed on some other subset). Those cells are set to NA.
# Not shipped: Mathematics anxiety (mAMAS, 9 items) is in the file only as
#   its two subscale totals (KAYGI1, KAYGI2) and their sum (KayTop), so it
#   cannot ship. basariii (a 25-100 mathematics exam score) is not carried:
#   it is a separate outcome, not a covariate of the item responses.
#   VAR00001 is empty.
# Duplicates: one pair of rows is identical in all 20 columns; both answer 5
#   to every item with the minimum anxiety totals and an exam score of 100.
#   A ceiling pattern can recur by chance, the codebook's N is 443, and both
#   rows are kept.
# id: row index (the codebook: "cases are unordered and unlabeled").
# Covariates: none in the file.
#
# Item text: not shipped. Both label levels checked: no variable labels and
#   no value labels on any column. The codebook says the wording is in the
#   manuscript's Measures subsection, which is not yet published.

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
URL = "https://ndownloader.figshare.com/files/67729404"

TABLES = {
    "kul_2026_math_self_concept": (["MCS1", "MSC2", "MSC3", "MSC4"], "SCTop"),
    "kul_2026_math_self_efficacy": ([f"MSE{i}" for i in range(1, 5)],
                                    "SETop"),
    "kul_2026_academic_buoyancy": ([f"AB{i}" for i in range(1, 5)], "ABTop"),
}
DROPPED = {"SCTop", "SETop", "ABTop", "KayTop", "KAYGİ1", "KAYGİ2",
           "basariii", "VAR00001"}
PERMITTED = set(range(1, 6))


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
    assert d.shape == (443, 20), d.shape
    items = {c for its, _ in TABLES.values() for c in its}
    assert set(d.columns) == items | DROPPED, set(d.columns) ^ (items
                                                                | DROPPED)
    assert d["VAR00001"].isna().all()
    assert d.duplicated().sum() == 1
    dup = d[d.duplicated(keep=False)]
    assert (dup[list(items)] == 5).all(axis=None)
    assert not any(meta.column_names_to_labels.get(c) for c in items)
    assert not any(c in meta.variable_value_labels for c in items)

    for its, tot in TABLES.values():
        assert np.allclose(d[its].sum(axis=1), d[tot]), tot
    frac = d["AB4"] % 1 != 0
    assert frac.sum() == 5 and np.allclose(d.loc[frac, "AB4"], 3.38104089)
    d.loc[frac, "AB4"] = np.nan

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)

    names = []
    for table, (its, _) in TABLES.items():
        long = d.melt(id_vars=["id"], value_vars=its, var_name="item",
                      value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - PERMITTED
            assert not bad, (table, it, bad)
        pv = {i: PERMITTED for i in its}
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
