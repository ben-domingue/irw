#!/usr/bin/env python3
# Source: https://zenodo.org/records/19811259
# DOI: 10.5281/zenodo.19811259 (dataset; no published paper yet)
#   "A psychometric comparison of four approaches to the Gaming Addiction
#   Scale (GAS)." Deposited 2026-04-27 by "Anonymous authors" for review. The
#   Readme says the data come from a UNICEF Spain / University of Santiago de
#   Compostela / Spanish General Council of Informatics Engineering project
#   (USC-CL027), collected 2024-02-27 from a nationwide representative sample
#   of Spanish secondary-school adolescents. With no named author, the table
#   prefix is the collecting institution (usc); rename once the paper is out.
# Data: Zenodo 19811259, "GAS_data_2026.sav" (34,076 rows x 81 columns). The
#   deposit's "R code GASA.txt" analyses the seven GASA items.
# License: CC BY 4.0 (Zenodo record licence). The Readme adds "Restrictions
#   placed on the data: None, citing authors of the publication related."
#
# Item text: not shipped. GASA and PHQ items carry only positional variable
#   labels ("GASA1", "PHQ1"); GASA value labels are present (0 Nunca ..
#   4 Muy a menudo), PHQ items have none. The wellbeing and relationship
#   items carry their Spanish stems as variable labels and no value labels.
#   The published GASA-7 (Lemmens et al. 2009, Spanish version) and PHQ-9
#   would be needed for the first two.
#
# Tables (item codes: the GASA/PHQ codes are the authors' own names, taken
#   from the .sav variable labels -- the R code reads the file with columns
#   GASA1-GASA7 -- instead of the deposit's positional V216-V222 / V58-V66;
#   the other two keep the V-number column names):
#   usc_2026_gasa         7 items, 0-4  Game Addiction Scale for Adolescents
#                          (GASA-7), value-labelled 0 Nunca .. 4 Muy a menudo
#   usc_2026_phq9         9 items, 0-3  PHQ-9 (PHQ_TOTAL = sum, asserted)
#   usc_2026_wellbeing    6 items, 0-10 V46-V51, Children's Worlds
#                          Psychological Subjective Well-Being Scale items
#                          ("Me gusta ser como soy" .. "Soy optimista sobre mi
#                          futuro"); BIENESTAR = their mean, asserted
#   usc_2026_relsat       5 items, 0-10 V52-V56, satisfaction with relations
#                          with classmates, teachers, friends, parents, rest of
#                          family; INTEGRACIÓN = their mean, asserted
#
# Dropped as items:
#   - V57 "MI VIDA EN ESTE MOMENTO" (overall life satisfaction, 0-10): a
#     single item, not part of the relationship block's composite
#     (INTEGRACIÓN is the mean of V52-V56 only); single-item scales are not
#     shipped. SATISFACCIÓN_VITAL is a copy of it.
#   - Gaming behaviour and PEGI questions (V182, V183-V188, V206-V209 and the
#     MÁS30*/DINERO*/HORAS*/PEGI18 recodes): single questions on different
#     formats, not a scale.
#   - Every derived column: G1-G7_RECOD, GASA4/6/7_rICD, GASA_TOTAL,
#     GASA_CRIBADO, GASAcore, GASAcoresum, GASAICDsum, GASAICD11,
#     GASAsinmissing, COREsinmissing, ICDsinmissing, GASAmis, PHQ_TOTAL,
#     DEPRESIÓN, DEPRESIÓN_CRIBADO, BIENESTAR, INTEGRACIÓN, SATISFACCIÓN_VITAL,
#     the four *10percent flags, and Random (a random-split helper).
#
# id: row index (the file has no id column). No PII: no names, contacts,
#   dates of birth, locations or free text.
# Covariates: cov_gender (0 male, 1 female, 2 other), cov_age (11-18),
#   cov_grade (S3 CURSO, ESO year 1-4), cov_cycle (S4 CICLO ESO, 1-2),
#   cov_repeated_grade (S5, 0 no, 1 yes), cov_gaming_freq (V181, 0 never ..
#   4 every or almost every day; only 4 respondents report never).

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
URL = "https://zenodo.org/api/records/19811259/files/GAS_data_2026.sav/content"


def vs(a, b):
    return [f"V{i}" for i in range(a, b + 1)]


GASA = dict(zip(vs(216, 222), [f"GASA{i}" for i in range(1, 8)]))
PHQ = dict(zip(vs(58, 66), [f"PHQ{i}" for i in range(1, 10)]))

TABLES = {
    "usc_2026_gasa": (list(GASA.values()), range(0, 5)),
    "usc_2026_phq9": (list(PHQ.values()), range(0, 4)),
    "usc_2026_wellbeing": (vs(46, 51), range(0, 11)),
    "usc_2026_relsat": (vs(52, 56), range(0, 11)),
}

COVS = {"S1": "cov_gender", "S2": "cov_age", "S3": "cov_grade",
        "S4": "cov_cycle", "S5": "cov_repeated_grade",
        "V181": "cov_gaming_freq"}

DROPPED = set(vs(182, 188)) | set(vs(206, 209)) | {"V57"} | {
    "MÁS30h_semanales_VIDEOJUEGOS", "HORAS_VIDEOJUEGOS_REALES",
    "DINERO_VIDEOJUEGOS", "MÁS30euros_VIDEOJUEGOS", "PEGI18",
    "DEPRESIÓN_CRIBADO", "INTEGRACIÓN", "SATISFACCIÓN_VITAL", "BIENESTAR",
    "PHQ_TOTAL", "DEPRESIÓN", "GASA_TOTAL", "GASA_CRIBADO", "GASAcore",
    "GASAcoresum", "GASA4_rICD", "GASA6_rICD", "GASA7_rICD", "GASAICDsum",
    "GASAICD11", "GASAsinmissing", "COREsinmissing", "ICDsinmissing",
    "GASAmis", "Random", "integración10percent", "satisfaction10percent",
    "bienestar10percent", "depresion10percent"} | {
    f"G{i}_RECOD" for i in range(1, 8)}


def load():
    r = requests.get(URL, headers=UA, timeout=300)
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
    assert d.shape == (34076, 81), d.shape
    labels = meta.column_names_to_labels
    # The renamed codes are the authors' own labels, not an assumption.
    for src, code in {**GASA, **PHQ}.items():
        assert labels[src] == code, (src, labels[src])

    # Composites agree with the items they summarise.
    assert (d["PHQ_TOTAL"] == d[vs(58, 66)].sum(axis=1)).all()
    assert np.allclose(d["BIENESTAR"], d[vs(46, 51)].mean(axis=1),
                       equal_nan=True)
    assert np.allclose(d["INTEGRACIÓN"], d[vs(52, 56)].mean(axis=1),
                       equal_nan=True)

    d = d.rename(columns={**GASA, **PHQ, **COVS})
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    cov_cols = list(COVS.values())

    # Balance the books.
    shipped = {c for items, _ in TABLES.values() for c in items}
    accounted = shipped | DROPPED | set(cov_cols) | {"id"}
    assert set(d.columns) == accounted, set(d.columns) ^ accounted

    names = []
    for table, (items, allowed) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all(), table
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - set(allowed)
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(items) > 1
        pv = {i: set(allowed) for i in items}
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
