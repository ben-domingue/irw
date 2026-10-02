#!/usr/bin/env python3
# Source: https://zenodo.org/records/22048398
# DOI: none found (Zenodo deposit only; no related identifier in its
#   metadata, and Crossref / Europe PMC title searches found no paper as of
#   2026-10-02).
#   Turpo Chaparro, J. E., & Carranza Esteban, R. (2026). "Study data:
#   Procrastination at work: Evidence of validity, reliability, and factorial
#   invariance of a brief measure in Peruvian university professors." Zenodo.
#   The EAPED and workload formats are documented in the same group's
#   Lingan-Huaman, ..., Carranza-Esteban (2023), "Teacher self-efficacy:
#   development, validity, and factorial invariance of a brief measure in
#   Peruvian university professors", Frontiers in Education,
#   10.3389/feduc.2023.1211487 (a different sample, N=529; read 2026-10-02).
# Data: Zenodo 22048398, "Data - Proyecto 33_IM (1).sav" (586 rows x 44
#       columns; Peruvian university professors, Spanish administration).
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# Item text: shipped (turpochaparro_2026_{procrastination,workload,
#   teacher_self_efficacy}__items.csv). Both label levels checked: every item
#   carries its full Spanish stem as its variable label (the leading "01. "
#   numbering is stripped); value labels on every item name only the two
#   endpoints (pd: 1 Nunca / 5 Siempre; cl: 0 Nunca / 4 Muy frecuentemente:
#   todos los dias; ad: 1 Nunca / 4 Siempre), so the midpoints' option_text is
#   left blank. No English in the deposit, so the _translated fields are
#   empty.
#
# Tables (item codes are the source column names):
#   turpochaparro_2026_procrastination        pd01-pd14, 1-5  Teacher Work
#       Procrastination Scale (PAWS-DU; the deposit description's name). 14
#       items administered; the deposit's score PD_ProcLabDocec_TV2 equals
#       (sum of pd02, pd05, pd06, pd07, pd08, pd09, pd11, pd13 - 8) * 30/32
#       (asserted), i.e. the brief measure keeps those 8. All 14 ship.
#       Range 1-5 from the value labels (1 Nunca .. 5 Siempre).
#   turpochaparro_2026_workload               cl01-cl06, 0-4  Workload scale
#       (Calderon De la Cruz et al. 2018, UNIPSICO; six items, five options
#       per Lingan-Huaman 2023). CL_CargaLaboral_TV2 = 1.25 * sum (asserted).
#   turpochaparro_2026_teacher_self_efficacy  ad01-ad10, 1-4  EAPED (Escala
#       de Autoeficacia Percibida Especifica para la Docencia; 10 items,
#       1 Never .. 4 Always per Lingan-Huaman 2023). AD_AutoeAcadDoc_TV2 =
#       sum - 10 (asserted).
#
# Dropped:
#   - PD_ProcLabDocec_TV2, CL_CargaLaboral_TV2, AD_AutoeAcadDoc_TV2 (scores).
#   - ZZZZZZZZZZZ: an empty separator column.
#   - DeEstudio: constant 1.
#   - Num: a respondent number (1-586, permuted); replaced by the row index.
#   - Edad, EdadGrupo, Grado, Campo, Experiencia, Condicion, Universidad:
#     coded 1-k with no value labels and no paper to decode them.
# id: row index.
# Covariates: cov_sex (1 Masculino, 2 Femenino; value-labelled).

import os
import re
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
TEXT_DIR = REPO_ROOT / "automated_finding" / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/22048398/files/"
       "Data%20-%20Proyecto%2033_IM%20(1).sav/content")

PD = [f"pd{i:02d}" for i in range(1, 15)]
CL = [f"cl{i:02d}" for i in range(1, 7)]
AD = [f"ad{i:02d}" for i in range(1, 11)]
TABLES = {
    "turpochaparro_2026_procrastination": (
        PD, range(1, 6),
        "Teacher Work Procrastination Scale (PAWS-DU), Peruvian Spanish"),
    "turpochaparro_2026_workload": (
        CL, range(0, 5), "Workload scale (Carga laboral), Peruvian Spanish"),
    "turpochaparro_2026_teacher_self_efficacy": (
        AD, range(1, 5),
        "Escala de Autoeficacia Percibida Especifica para la Docencia "
        "(EAPED)"),
}
ENDPOINTS = {
    "pd": {1.0: "Nunca", 5.0: "Siempre"},
    "cl": {0.0: "Nunca", 4.0: "Muy frecuentemente:todos los días"},
    "ad": {1.0: "Nunca", 4.0: "Siempre"},
}
BRIEF = ["pd02", "pd05", "pd06", "pd07", "pd08", "pd09", "pd11", "pd13"]
COMPOSITES = {"PD_ProcLabDocec_TV2", "CL_CargaLaboral_TV2",
              "AD_AutoeAcadDoc_TV2"}
OTHER_DROPPED = {"ZZZZZZZZZZZ", "DeEstudio", "Num", "Edad", "EdadGrupo",
                 "Grado", "Campo", "Experiencia", "Condición", "Universidad"}
COVS = {"Sexo": "cov_sex"}


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


def stem(label):
    s = re.sub(r"^\d{2}\.\s*", "", label).strip()
    assert s and s != label, label
    return s


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (586, 44), d.shape

    # Balance the books.
    items = {c for its, _, _ in TABLES.values() for c in its}
    known = items | COMPOSITES | OTHER_DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known

    # Scores reproduce from the items, which pins the item blocks.
    assert ((d[BRIEF].sum(axis=1) - 8) * 30 / 32
            - d["PD_ProcLabDocec_TV2"]).abs().max() < 1e-9
    assert ((d[CL].sum(axis=1) * 1.25)
            - d["CL_CargaLaboral_TV2"]).abs().max() < 1e-9
    assert ((d[AD].sum(axis=1) - 10)
            - d["AD_AutoeAcadDoc_TV2"]).abs().max() < 1e-9
    assert d["ZZZZZZZZZZZ"].isna().all() and (d["DeEstudio"] == 1).all()
    assert d["Num"].is_unique
    assert meta.variable_value_labels["Sexo"] == {1.0: "Masculino",
                                                  2.0: "Femenino"}
    for c in items:
        assert meta.variable_value_labels[c] == ENDPOINTS[c[:2]], c

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, allowed, instrument) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
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
        assert long["item"].nunique() == len(its) > 1
        pv = {i: set(allowed) for i in its}
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

        # Item text: Spanish variable labels; endpoint value labels only.
        text = []
        for it in its:
            ends = meta.variable_value_labels[it]
            for k in allowed:
                text.append({
                    "table": table, "section_id": f"{table}_1", "item": it,
                    "instrument": instrument, "language": "Spanish",
                    "instructions": "", "section_prompt": "",
                    "item_text": stem(meta.column_names_to_labels[it]),
                    "item_text_translated": "", "correct_response": "",
                    "option_text": ends.get(float(k), ""),
                    "option_text_translated": "", "resp": k})
        tx = pd.DataFrame(text)
        assert set(tx["item"]) == set(long["item"])
        assert set(tx["resp"]) == set(allowed)
        tx.to_csv(TEXT_DIR / f"{table}__items.csv", index=False)
        print(f"{table}__items.csv: rows={len(tx)}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
