#!/usr/bin/env python3
# Source: https://zenodo.org/records/20030985
# DOI: 10.29059/rpcc.20201215-114
#   Daniel-González, L., García Cadena, C. H., Valle de la O, A.,
#   Caycho-Rodríguez, T., & Martínez-Gómez, E. (2020). "Validation Study of
#   the 10-item Connor-Davidson Resilience Scale Among Mexican Medical and
#   Psychology Students." Revista de Psicología y Ciencias del Comportamiento
#   de la Unidad Académica de Ciencias Jurídicas y Sociales, 11(2), 4-18.
#   (The deposit's related identifier reads 10.29059/rpcc. 20201215-113,
#   which resolves to an unrelated article in the same issue; -114 is the
#   paper, matched on title and authors via Crossref.)
# Data: Zenodo 20030985, Dataset_CDRISC10.sav (330 rows x 31 columns; 174
#       medical + 156 psychology students, northeastern Mexico).
# License: CC BY 4.0 (Zenodo record metadata).
#
# Item text: not shipped. Both label levels checked: every item carries its
#   full Spanish stem as a variable label, and every item has value labels.
#   Not shipped on rights grounds, not availability: CD-RISC, SHS and PSS
#   each have a "block" verdict in the itemtext rights register (irw-validate
#   flags all three; the item codes are not wording, so no rename is
#   needed). The CD-RISC-10 Spanish stems are also in the paper's Appendix.
#
# Tables (item codes are the source column names):
#   danielgonzalez_2020_cdrisc10  CDRISC1-10  10-item CD-RISC, Mexican
#       Spanish. Paper: six-point scale, 0 = never .. 5 = always; value
#       labels 0 Nunca .. 5 Siempre agree.
#   danielgonzalez_2020_shs       SHS1-4  Subjective Happiness Scale. Paper:
#       seven-point; value labels 1..7 with end anchors. SHS4 is the
#       negatively worded item; its value labels read raw (1 = "Para nada")
#       yet it correlates positively with SHS1-3 (r = .15-.24), so it may be
#       stored after reverse-keying. Shipped as stored.
#   danielgonzalez_2020_pss       PSS1-14  Perceived Stress Scale (14 items).
#       Paper: six-point; value labels 0..5. The deposit description says
#       "0-4"; the paper, the value labels and the data all say 0-5, so 0-5
#       is asserted. PSS4/5/6/7/9/10/13 (the positively worded items) are
#       value-labelled 0 = Siempre .. 5 = Nunca, i.e. stored stress-keyed
#       (after reverse-coding); the rest 0 = Nunca .. 5 = Siempre.
#
# Cleaning: none needed. No missing cells, no fractional values, no
#   out-of-label codes, no sentinels.
# Dropped: nothing (the file has no totals).
# id: row index (the file has no respondent id).
# Covariates: cov_gender (1 man, 2 woman), cov_age, cov_program
#   (1 medicine, 2 psychology), all value-labelled in the file.

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
URL = ("https://zenodo.org/api/records/20030985/files/"
       "Dataset_CDRISC10.sav/content")

TABLES = {
    "danielgonzalez_2020_cdrisc10": ([f"CDRISC{i}" for i in range(1, 11)],
                                     range(0, 6)),
    "danielgonzalez_2020_shs": ([f"SHS{i}" for i in range(1, 5)],
                                range(1, 8)),
    "danielgonzalez_2020_pss": ([f"PSS{i}" for i in range(1, 15)],
                                range(0, 6)),
}
PSS_REVERSED = {4, 5, 6, 7, 9, 10, 13}
COVS = {"GEN": "cov_gender", "ED": "cov_age", "TPE": "cov_program"}


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
    assert d.shape == (330, 31), d.shape

    # Balance the books.
    items = {c for its, _ in TABLES.values() for c in its}
    known = items | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert d.notna().all().all()

    # Value labels: the documented sets, and the PSS keying.
    vl = meta.variable_value_labels
    for its, allowed in TABLES.values():
        for c in its:
            assert set(vl[c]) == set(map(float, allowed)), c
    for i in range(1, 15):
        first = vl[f"PSS{i}"][0.0]
        assert first == ("Siempre" if i in PSS_REVERSED else "Nunca"), i
    assert vl["CDRISC1"][0.0] == "Nunca" and vl["CDRISC1"][5.0] == "Siempre"
    assert vl["GEN"] == {1.0: "Hombre", 2.0: "Mujer"}
    assert vl["TPE"] == {1.0: "Estudiante Medicina",
                         2.0: "Estudiante Psicologia"}
    assert (d["TPE"] == 1).sum() == 174 and (d["TPE"] == 2).sum() == 156

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, allowed) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        allowed = set(allowed)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
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
