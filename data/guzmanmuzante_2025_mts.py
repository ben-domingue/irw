#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/ZGEDDT
# DOI: 10.1186/s40359-026-05372-x
#   Guzmán-Muzante, Serrano, Riquelme Ortíz, Fonseca, Kinney, Abregú Chesta,
#   Romero Carrasco, Severino-González & Cáceres (2026). "Psychometric
#   validation of the Mental Toughness Scale (MTS) in Chilean university
#   athletes." BMC Psychology. (CC BY 4.0 per Crossref.)
# Data: Harvard Dataverse 10.7910/DVN/ZGEDDT (Guzmán-Muzante, 2025),
#       "Base MTS Chilenos_200_nn.sav" (200 rows x 38 columns), fetched with
#       ?format=original. Chilean university athletes, Spanish
#       administration.
# License: CC0 1.0 (Dataverse dataset metadata).
#
# Documentation caveat: the paper's full text could not be read (Springer
#   serves a JavaScript bot challenge; not yet in PMC). Its abstract confirms
#   the instruments: a Spanish back-translated MTS and a general self-efficacy
#   (GSE) measure, here EAG_1-10 (Escala de Autoeficacia General). The
#   permitted response sets below are therefore NOT taken from this paper:
#     - EAG: the Spanish GSE is a 10-item, 4-point scale (1 incorrecto ..
#       4 cierto; Baessler & Schwarzer 1996, Sanjuan et al. 2000), and its
#       documented 1-4 set is passed to run_qc.
#     - MTS: the original MTS (Madrigal et al. 2013) is 11 items on a 7-point
#       scale, but this file holds 1-5 only, so the Chilean version evidently
#       used a different format. No document available to us states it, so no
#       permitted set is passed for MTS; values are only checked to be whole
#       numbers in 1-5. Confirm 1-5 against the paper's Methods when it can
#       be read.
#   The .sav carries an SPSS document note describing a 2017 multiple
#   imputation run on an earlier file ("Base de Datos Validacion FMU.sav",
#   5 imputations, linear regression). No Imputation_ column is present, all
#   MTS/EAG cells are whole numbers with none missing, and the item sums equal
#   MTS_Total/EAG_Total in every row (asserted), so the shipped cells are not
#   regression-imputed values; the note appears to be inherited metadata.
#
# Item text: not shipped. Both label levels checked: MTS_1-11 and EAG_1-10
#   have no variable labels and no value labels. The Spanish MTS wording would
#   be in the paper (unreadable here); the Spanish GSE is a published
#   canonical instrument.
#
# Tables (item codes are the source column names):
#   guzmanmuzante_2025_mts   11 items, 1-5  Mental Toughness Scale (Spanish).
#                             All 11 administered items ship; the paper's
#                             final solution keeps 10.
#   guzmanmuzante_2025_gse   10 items, 1-4  General Self-Efficacy (Spanish
#                             EAG)
#
# Dropped as items:
#   - MTS_Total, EAG_Total (sum scores; asserted equal to the item sums).
#   - CAT_Sub17/Sub20/Sub23/Adulto (competition-category dummies), Afiliación
#     (value labels 0/1 but data 1/2), SELEC_No, Hentre, Añoinicio: unlabelled
#     or label/data mismatched, meaning not documented. Not carried.
#
# id: row index (the file has no id column). No names, emails, birth dates,
#   IP or GPS. University and city are institution/place names, not personal
#   identifiers.
# Covariates: cov_age (Edad), cov_sex (1 Mujeres, 2 Hombres), cov_education
#   (1-6 per value labels: 1 primary incomplete, 2 secondary incomplete,
#   3 tertiary incomplete, 4 primary complete, 5 secondary complete,
#   6 tertiary complete), cov_sport (1-16 per value labels, e.g. 1 athletics,
#   2 basketball, 4 football, 12 rugby), cov_years_practice (Añospractica),
#   cov_university, cov_city (strings as entered; blanks -> NA).

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/11602319?format=original"

MTS = [f"MTS_{i}" for i in range(1, 12)]
EAG = [f"EAG_{i}" for i in range(1, 11)]
# (items, documented permitted set or None, range sanity bound)
TABLES = {
    "guzmanmuzante_2025_mts": (MTS, None, range(1, 6)),
    "guzmanmuzante_2025_gse": (EAG, range(1, 5), range(1, 5)),
}

COVS = {"Edad": "cov_age", "SEXO": "cov_sex", "Educación": "cov_education",
        "Deporte": "cov_sport", "Añospractica": "cov_years_practice",
        "Universidad": "cov_university", "Ciudad": "cov_city"}
DROPPED = ["MTS_Total", "EAG_Total", "CAT_Sub17", "CAT_Sub20", "CAT_Sub23",
           "CAT_Adulto", "Afiliación", "SELEC_No", "Hentre", "Añoinicio"]
NUM_COVS = ["cov_age", "cov_sex", "cov_education", "cov_sport",
            "cov_years_practice"]


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, _ = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = load()
    assert d.shape == (200, 38), d.shape

    # Balance the books: every column is an item, a covariate, or named.
    rest = set(d.columns) - set(MTS) - set(EAG) - set(COVS) - set(DROPPED)
    assert rest == set(), rest
    assert d[MTS + EAG].notna().all().all()
    assert (d[MTS].sum(axis=1) == d["MTS_Total"]).all()
    assert (d[EAG].sum(axis=1) == d["EAG_Total"]).all()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    for c in ("cov_university", "cov_city"):
        d[c] = d[c].astype(str).str.strip().replace("", pd.NA)
    cov_cols = list(COVS.values())

    names = []
    for table, (items, documented, bound) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - set(bound)
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp"] + cov_cols]
        for c in NUM_COVS:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(items) > 1
        pv = {i: set(documented) for i in items} if documented else None
        checks = run_qc(long, permitted_values=pv)
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
