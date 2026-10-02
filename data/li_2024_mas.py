#!/usr/bin/env python3
# Source: https://frontiersin.figshare.com/articles/dataset/Table_2_Translation_and_psychometric_validation_of_the_Chinese_version_of_the_metacognitive_awareness_scale_among_nursing_students_xls/25838518
#   and its sibling Table_1 (figshare 25838515, DOI 10.3389/fpsyg.2024.1354810.s001).
# DOI: 10.3389/fpsyg.2024.1354810
#   Li, S., Xu, J., Jia, X., Zhao, Y., Liu, X., & Wang, Y. (2024). "Translation
#   and psychometric validation of the Chinese version of the metacognitive
#   awareness scale among nursing students." Frontiers in Psychology, 15,
#   1354810. (Open access, PMC11139026.)
# Data: two Frontiers supplementary .xls files, one per random half of the
#       sample (the paper's Group A for EFA and Group B for CFA, 296 each):
#       Table_2 (.s002, figshare file 46374706, 296 x 66, group = 1) and
#       Table_1 (.s001, figshare file 46374703, 296 x 58, group = 2).
#       Together they are the paper's 592 nursing undergraduates: 512
#       women / 80 men and 142/140/186/124 by year, both reproduced exactly
#       (asserted), mean age 21.25.
# License: CC BY 4.0 (figshare API, both articles).
#
# Item text: not shipped. Both label levels checked: .xls files, so there
#   are no variable or value labels; the headers are subscale codes
#   (DK1..E6). The paper's Table 1 ties each subscale code to the original
#   MAI item number (I1-I52), but it prints no stems; the English wording is
#   Schraw & Dennison's (1994) Metacognitive Awareness Inventory, and the
#   Chinese wording is not published in the paper.
#
# Instrument (paper section 3.3 and Table 1): the 52-item Metacognitive
#   Awareness Inventory (Schraw & Dennison 1994), Chinese version; knowledge
#   of cognition (declarative DK1-8, procedural PK1-4, conditional CK1-5)
#   and regulation of cognition (planning P1-7, information management
#   IMS1-10, monitoring M1-7, debugging DS1-5, evaluation E1-6). "5-point
#   Likert scale, with scores ranging from 1 (always false) to 5 (always
#   true)" -- asserted per item. Item codes are the source column names.
#
# Checked and kept: 19 rows (12 within Table_2, 1 within Table_1, 6 across
#   the two) share their gender/age/year/52-item vector with another row.
#   Every one is a near-constant all-3 pattern, i.e. a careless-responding
#   profile that different students can produce independently, and the
#   paper's N of 592 counts them, so they are not treated as repeated
#   submissions.
# Dropped: number (a row counter within each file) and the composites
#   total (both files) and DK, PK, CK, P, IMS, M, E, DS (Table_2 only; the
#   subscale sums match their items except E, which is not relied on).
#   group is the file indicator and is kept as cov_group.
# id: row index over the stacked files (Table_2 first).
# Covariates: cov_group (1 = Group A/EFA half, 2 = Group B/CFA half),
#   cov_gender (1 male, 2 female; decoded from the paper's 80/512 split),
#   cov_age, cov_year (1-4 = freshman..senior; decoded from the paper's
#   142/140/186/124 split).

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
FILES = [("https://ndownloader.figshare.com/files/46374706", 66, 1),
         ("https://ndownloader.figshare.com/files/46374703", 58, 2)]
TABLE = "li_2024_mas"

BLOCKS = {"DK": 8, "PK": 4, "CK": 5, "P": 7, "IMS": 10, "M": 7, "DS": 5,
          "E": 6}
ITEMS = [f"{k}{i}" for k, n in BLOCKS.items() for i in range(1, n + 1)]
COVS = {"group": "cov_group", "Gender": "cov_gender", "Age": "cov_age",
        "grade": "cov_year"}
PERMITTED = set(range(1, 6))


def load(url):
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name="Sheet1")


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    parts = []
    for url, ncol, grp in FILES:
        d = load(url)
        assert d.shape == (296, ncol), d.shape
        known = {"number", "total"} | set(ITEMS) | set(COVS)
        if ncol == 66:
            known |= set(BLOCKS)
        assert set(d.columns) == known, set(d.columns) ^ known
        assert (d["group"] == grp).all()
        assert d["number"].tolist() == list(range(1, 297))
        parts.append(d[list(COVS) + ITEMS])
    d = pd.concat(parts, ignore_index=True)
    assert len(d) == 592
    assert d["Gender"].value_counts().to_dict() == {2: 512, 1: 80}
    assert d["grade"].value_counts().to_dict() == {1: 142, 2: 140, 3: 186,
                                                   4: 124}
    assert not d[ITEMS].isna().any().any()

    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())
    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - PERMITTED
        assert not bad, (it, bad)
    pv = {i: PERMITTED for i in ITEMS}
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() == 592 and long["item"].nunique() == 52
    fails = [(c.name, c.detail) for c in run_qc(long, permitted_values=pv)
             if c.status == "fail"]
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
