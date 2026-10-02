#!/usr/bin/env python3
# Source: https://zenodo.org/records/11377073
# DOI: none found (Zenodo deposit only; no related publication in its
#   metadata, and a Crossref title search found no paper as of 2026-10-02).
#   De La Cruz-Valdiviano, C. B. (2024). "De Jong Gierveld Loneliness Scale:
#   validity, reliability and fairness in Peruvian adults." Zenodo.
#   https://doi.org/10.5281/zenodo.11377073
# Data: Zenodo 11377073, "Loneliness Scale Database in Peru.sav" (1,248 rows
#       x 19 columns; online survey of Peruvian adults aged 18-59). The
#       deposit also holds the scale authors' manual (De Jong Gierveld & Van
#       Tilburg 2019), their 2018 paper, an ethics approval, an authorisation
#       to use the instrument, and "Resultados DJGLS.docx" (the results
#       write-up: item table, CFA models, bifactor loadings).
# License: CC BY 4.0 (Zenodo record metadata).
#
# Item text: not shipped. Both label levels checked: S1-S11 carry no
#   variable labels and no value labels (only the covariates and totals have
#   variable labels). The Spanish stems, numbered 1-11 to match S1-S11, are
#   in the deposit's "Resultados DJGLS.docx" (bifactor-loadings table); the
#   English originals are in the deposit's 2019 manual. That would be a
#   paper_explicit mapping, so it needs a verify_<table>.R, not the cheap
#   gate.
#
# Tables (item codes are the source column names):
#   delacruzvaldiviano_2024_djgls  S1-S11  De Jong Gierveld Loneliness Scale
#       (11 items), Spanish. The file holds DICHOTOMISED, loneliness-keyed
#       item scores (0/1), not the raw answers: the manual scores the
#       answers this way (positive items 1, 4, 7, 8, 11 score 1 on
#       "no"/"more or less"; negative items 2, 3, 5, 6, 9, 10 on "yes"/"more
#       or less"), with a scale range of 0-11. `Soledad` equals the item sum
#       in every row (asserted). The administered answer format (three or
#       five categories) is not stated in the deposit. Permitted {0, 1} per
#       the manual's dichotomous scoring. Item means match the deposit's
#       Resultados table (e.g. S7 .73, S10 .49).
#       Factor structure (Resultados): social = 1, 4, 7, 8, 11; emotional =
#       2, 3, 5, 6, 9, 10.
#
# Cleaning: none needed. No missing cells, no fractional values.
# Dropped: Soledad (loneliness total), Ansiedad_ante_la_muerte and
#   Ideación_Suicida (death-anxiety and suicidal-ideation totals; their items
#   are not in the deposit), Etario (age group, derivable from age:
#   1 = 18-29, 2 = 30-59, asserted), ID (a 1..1248 sequence).
# id: row index (equal to the file's ID, asserted).
# Covariates: cov_age; cov_sex and cov_residence are coded 1/2 with NO value
#   labels in the file and no codebook, so their meaning is undocumented
#   (653/595 and 956/292 respectively).

import os
import sys
import tempfile
from pathlib import Path

import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/11377073/files/"
       "Loneliness%20Scale%20Database%20in%20Peru.sav/content")

TABLE = "delacruzvaldiviano_2024_djgls"
ITEMS = [f"S{i}" for i in range(1, 12)]
ALLOWED = {0, 1}
COMPOSITES = {"Soledad", "Ansiedad_ante_la_muerte", "Ideación_Suicida"}
DROPPED = {"Etario", "ID"}
COVS = {"Edad": "cov_age", "Sexo": "cov_sex", "Residencia": "cov_residence"}


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
    assert d.shape == (1248, 19), d.shape

    # Balance the books.
    known = set(ITEMS) | COMPOSITES | DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert d.notna().all().all()

    assert (d["Soledad"] == d[ITEMS].sum(axis=1)).all()
    assert (d["ID"] == range(1, len(d) + 1)).all()
    assert ((d["Etario"] == 1) == (d["Edad"] <= 29)).all()
    assert d["Edad"].between(18, 59).all()
    for c in ITEMS + ["Sexo", "Residencia"]:
        assert c not in meta.variable_value_labels, c

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - ALLOWED
        assert not bad, (it, bad)
    pv = {i: ALLOWED for i in ITEMS}
    long = long[["id", "item", "resp"] + cov_cols]
    for c in cov_cols:
        long[c] = long[c].astype("Int64")
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() == 1248
    assert long["item"].nunique() == len(ITEMS)
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
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
