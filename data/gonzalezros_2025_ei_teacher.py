#!/usr/bin/env python3
# Source: https://zenodo.org/records/18091343
# DOI: 10.3390/jintelligence14050075
#   Gonzalez-Ros, L., Pozo-Rico, T., Castejon, J. L., & Gilar-Corbi, R.
#   (2026). "Emotional Intelligence and Teacher Self-Efficacy in Initial
#   Teacher Education: A Psychoeducational Intervention with Spanish
#   Pre-Service Teachers." Journal of Intelligence, 14(5), 75.
#   (PMC13207575; CC BY 4.0. Found by Crossref title search; the deposit has
#   no related identifiers.)
#   Dataset: Gonzalez-Ros, L., Pozo-Rico, T., Castejon, J. L., &
#   Gilar-Corbi, R. (2025). Zenodo. https://doi.org/10.5281/zenodo.18091343
# Data: Datos.sav (202 rows x 280 columns: 201 pre-service teachers plus one
#       empty trailing row; University of Alicante, spring 2024).
# License: CC BY 4.0 (Zenodo API).
#
# Design: a quasi-experimental pre/post study with a non-equivalent control
# group. GRUPO 2 (experimental, 100 at pretest) received an eight-week
# psychoeducational programme; GRUPO 1 (control, 101) did not -> treat 1/0.
# wave 1 = pretest (T1, all 201), wave 2 = posttest (T2, 163: the paper's
# 90 experimental + 73 control completers; the counts are asserted).
#
# Tables (item codes are the source column names, wave suffix removed):
#   gonzalezros_2025_ostes   item1OSTES .. item24OSTES  Teachers' Sense of
#       Efficacy Scale (Tschannen-Moran & Woolfolk Hoy 2001), Spanish. The
#       paper does not print the response format; the published TSES is a
#       9-point scale (1 "Nothing" .. 9 "A great deal"), and {1..9} is
#       asserted from that instrument documentation. The deposit's three
#       subscale means (ESTRATEGIASINSTRUCCION, GESTIONAULA,
#       PARTICIPACIONESTUDIANTES) are dropped.
#   gonzalezros_2025_tmms24  item1 .. item24  Trait Meta-Mood Scale-24
#       (Fernandez-Berrocal et al. 2004), 1-5 per the paper ("1 (Strongly
#       disagree) to 5 (Strongly agree)"). The Atencion/Claridad/Reparacion
#       totals equal the sums of items 1-8, 9-16, 17-24 (asserted).
#   gonzalezros_2025_eqi     item1 .. item51  the 51-item Spanish EQ-i
#       short form (Bar-On). NO permitted set is asserted: the paper says the
#       version used had 30 items "on a 4-point Likert scale ranging from 1
#       (Not true of me) to 4 (Very true of me)", but the deposit holds 51
#       items whose Spanish variable labels are the EQ-i stems, and every
#       item uses all of 1-5 (17-26% of all answers are 5 at each wave). The
#       paper's description does not fit the file, so the documented set
#       cannot be asserted and the observed one is not substituted for it.
#       The *_inv columns (22 per wave) are reverse-coded copies,
#       inv = 6 - item in every row (asserted), and are dropped; the EQ-i
#       composites (E_*, EQi_*, impresion_alta_*) are dropped.
#
# Dropped: the composites above; EQiST1 / EQiST2POST (empty, and identical
#   to each other); caso_completo and filter_$ (an SPSS filter flag and its
#   copy).
# id: row index. ID ("E1".."E201") is a study code and is not shipped.
# Covariates: cov_sex (1 hombre, 2 mujer; value labels), cov_age (years).
#
# Item text: not shipped. Both label levels checked: every item carries its
#   full Spanish stem as a variable label (OSTES, TMMS-24 and EQ-i, at both
#   waves; some T2 labels carry a stray trailing item number); no item has
#   value labels, so the option wording would come from the paper (TMMS-24
#   endpoints only) or the published instruments. Rights: the EQ-i is a
#   Multi-Health Systems instrument (the register blocks the MHS family);
#   TMMS-24 and TSES have no register row yet. The Spanish stems are cheap
#   once rights are ruled on; no English is in the source.

import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/18091343/files/Datos.sav/content"

# table -> (wave-1 columns, wave-2 columns, item codes, permitted set)
BLOCKS = {
    "gonzalezros_2025_ostes": (
        [f"item{i}OSTES_T1" for i in range(1, 25)],
        [f"item{i}OSTES_T2" for i in range(1, 25)],
        [f"item{i}OSTES" for i in range(1, 25)], set(range(1, 10))),
    "gonzalezros_2025_tmms24": (
        [f"item{i}T1" for i in range(1, 25)],
        [f"item{i}T2" for i in range(1, 25)],
        [f"item{i}" for i in range(1, 25)], set(range(1, 6))),
    "gonzalezros_2025_eqi": (
        [f"item{i}" for i in range(1, 52)],
        [f"item{i}_2" for i in range(1, 52)],
        [f"item{i}" for i in range(1, 52)], None),
}
INV_T1 = [3, 4, 8, 9, 10, 15, 16, 21, 22, 26, 27, 28, 33, 34, 37, 39, 40,
          44, 45, 48, 49, 50]
INV = ([f"item{i}_inv" for i in INV_T1]
       + [f"item{i}_2_inv" for i in INV_T1])
COMPOSITES = {
    "ESTRATEGIASINSTRUCCIÓN_T1", "GESTIÓNAULA_T1",
    "PARTICIPACIÓNESTUDIANTES_T1", "ESTRATEGIASINSTRUCCIÓN_T2",
    "GESTIÓNAULA_T2", "PARTICIPACIÓNESTUDIANTES_T2",
    "AtenciónemocionalT1", "ClaridademocionalT1", "ReparaciónemocionalT1",
    "AtenciónemocionalT2", "ClaridademocionalT2", "ReparaciónemocionalT2",
    "E_intrapersonalT1", "E_interpersonalT1", "E_manejoestresT1",
    "E_adaptT1", "E_humorT1", "E_possitiveimpressionT1", "EQi_T1",
    "E_INTRAPERT2", "E_INTERPERT2", "E_MANEJOESTREST2", "E_ADAPTT2",
    "E_HUMORT2", "E_POSSITIVEVIMPRESSIONT2", "EQi_T2", "impresion_alta_T1",
    "impresion_alta_T2", "E_positiveimpressionT1",
    "E_POSSITIVEIMPRESSIONT2"}
OTHER_DROPPED = {"EQiST1", "EQiST2POST", "caso_completo", "filter_$", "ID"}
COVS = {"GÉNERO": "cov_sex", "EDAD": "cov_age"}


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
    assert d.shape == (202, 280), d.shape

    item_cols = {c for b in BLOCKS.values() for c in b[0] + b[1]}
    known = (item_cols | set(INV) | COMPOSITES | OTHER_DROPPED | set(COVS)
             | {"GRUPO"})
    assert set(d.columns) == known, set(d.columns) ^ known

    # The one trailing row is empty.
    empty = d["ID"].isna() | (d["ID"] == "")
    assert empty.sum() == 1 and d.loc[empty].drop(
        columns=["ID", "caso_completo", "filter_$"]).isna().all(axis=None)
    d = d.loc[~empty].reset_index(drop=True)
    assert d["ID"].is_unique and len(d) == 201
    assert d[["EQiST1", "EQiST2POST"]].isna().all(axis=None)
    assert d["caso_completo"].equals(d["filter_$"])
    assert not d.drop(columns="ID").duplicated().any()

    for c in INV:
        src = c[:-4]
        assert ((d[c] == 6 - d[src]) | (d[c].isna() & d[src].isna())).all(), c
    for t in ("T1", "T2"):
        for name, lo in (("Atención", 1), ("Claridad", 9),
                         ("Reparación", 17)):
            cols = [f"item{i}{t}" for i in range(lo, lo + 8)]
            has = d[cols].notna().all(axis=1)
            assert np.allclose(d.loc[has, cols].sum(axis=1),
                               d.loc[has, f"{name}emocional{t}"]), (t, name)

    assert d["GRUPO"].value_counts().to_dict() == {1.0: 101, 2.0: 100}
    w2 = d[BLOCKS["gonzalezros_2025_tmms24"][1]].notna().any(axis=1)
    assert d.loc[w2, "GRUPO"].value_counts().to_dict() == {2.0: 90, 1.0: 73}

    d.insert(0, "id", d.index + 1)
    d["treat"] = (d["GRUPO"] == 2).astype(int)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (c1, c2, codes, allowed) in BLOCKS.items():
        parts = []
        for wave, cols in ((1, c1), (2, c2)):
            part = d[["id", "treat"] + cov_cols + cols].rename(
                columns=dict(zip(cols, codes)))
            part = part.melt(id_vars=["id", "treat"] + cov_cols,
                             value_vars=codes, var_name="item",
                             value_name="resp")
            part["wave"] = wave
            parts.append(part)
        long = pd.concat(parts).dropna(subset=["resp"])
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        pv = None
        if allowed is not None:
            for it, g in long.groupby("item"):
                bad = set(g["resp"]) - allowed
                assert not bad, (table, it, bad)
            pv = {i: allowed for i in codes}
        long = long[["id", "item", "resp", "wave", "treat"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "wave", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(codes) > 1
        assert long.groupby("wave")["id"].nunique().to_dict() == {1: 201,
                                                                    2: 163}
        checks = run_qc(long, permitted_values=pv) if pv else run_qc(long)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        ctx = {"permitted_values": pv} if pv else None
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context=ctx)
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
