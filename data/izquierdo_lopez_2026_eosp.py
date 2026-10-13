#!/usr/bin/env python3
# Source: https://zenodo.org/records/22308208
# DOI: 10.5281/zenodo.22308208 (dataset; the record names no published paper)
#   Izquierdo López, M., Sainz, V., & Martínez-Otero, V. (2026). Item-Level Data From the
#   Spanish Validation of the Observational Scale of Giftedness for Teachers (EOSP). Zenodo.
# Data: Dataset_A_EOSP.sav (Dataset_A_EOSP_codebook.txt describes every column): 160 Spanish
#       primary-school pupils (5-12) each rated once by one of 125 teachers on the 36-item
#       Escala Observacional de Superdotación para Profesorado (four nine-item areas:
#       A Académica, B Personalidad, C Interpersonal, D Intereses y actitudes; 1-9). Each row is
#       one pupil x one teacher, so id is the pupil and rater the teacher. The four area sums
#       and the total are not shipped.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped -- the SPSS variable labels (identical to the codebook) hold the Spanish
#   stems ("NIVEL DE EXPRESIÓN: Capacidad para expresarse oralmente y por escrito"); no value
#   labels on the items (checked), so the 1-9 points carry blank option_text. English in
#   item_text_translated is an IRW translation.
#
# Tables: izquierdo_lopez_2026_eosp (160 pupils x 36 items, 1-9, rater = teacher).
# Covariates: pupil cov_student_sex, cov_student_age, cov_student_grade, cov_gifted_diagnosis;
#   teacher cov_teacher_sex, cov_teacher_age, cov_teacher_experience, cov_teacher_category;
#   school cov_school_type, cov_school_location (codes as deposited; the codebook labels only
#   Titularidad_centro's name). The sparse Provincia column (5 of 160) is not shipped.
# id: the deposit's Código_Alumno number; rater: the Código_Profesor label.
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def zenodo_fetch(record: int, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://zenodo.org/api/records/{record}", headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == fname][0]
        download(url, p)
    return p


def figshare_fetch(article: int, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://api.figshare.com/v2/articles/{article}", headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == fname][0]
        download(url, p)
    return p


def mendeley_fetch(dataset: str, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://data.mendeley.com/public-api/datasets/{dataset}", headers=UA, timeout=120).json()
        url = [f["content_details"]["download_url"] for f in j["files"] if f["filename"] == fname][0]
        download(url, p)
    return p


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset in its original format."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"].get("originalFileName", f["dataFile"]["filename"]) == fname][0]
        download(f"https://{host}/api/access/datafile/{fid}?format=original", p)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values or None). QC, validate, write."""
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        keys = ["id", "item"] + [c for c in ("wave", "rater") if c in t]
        assert not t.duplicated(keys).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv} if pv else None)
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min():g}-{t['resp'].max():g}")


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=(),
         rename: dict | None = None) -> pd.DataFrame:
    """Melt `items` to long, drop missing, check integer codes inside `valid`, order columns.
    `rename` maps a source column to the `item` code it ships under (default: the column name)."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    if rename:
        t["item"] = t["item"].map(lambda c: rename.get(c, c))
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", *extra, "item"]).reset_index(drop=True)


def pv_for(items, valid) -> dict:
    return {i: set(valid) for i in items}


import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "zenodo_22308208"
FNAME = "Dataset_A_EOSP.sav"
COVS = {"Sexo_Alumno": "cov_student_sex", "Edad_Alumno": "cov_student_age", "Curso_Alumno": "cov_student_grade",
        "Diagnóstico_AACC_Alumno": "cov_gifted_diagnosis", "Sexo": "cov_teacher_sex", "Edad": "cov_teacher_age",
        "Años_experiencia": "cov_teacher_experience", "Categoría_profesional": "cov_teacher_category",
        "Titularidad_centro": "cov_school_type", "Ubicación": "cov_school_location"}
ITEMS = [f"ACI_{a}{i}" for a in "ABCD" for i in range(1, 10)]


def read():
    return pyreadstat.read_sav(zenodo_fetch(22308208, FNAME, RAW_DIR))


def stems():
    """(code, Spanish variable label) per item, straight from the .sav."""
    _, m = read()
    assert not any(c in m.variable_value_labels for c in ITEMS)
    return [(c, m.column_names_to_labels[c]) for c in ITEMS]


def main() -> None:
    d, m = read()
    assert len(d) == 160 and d["Código_Alumno"].is_unique
    d["id"] = d["Código_Alumno"].str.replace("Alumno_", "").astype(int)
    d["rater"] = d["Código_Profesor"]
    sums = {"A": "AACC_Académica", "B": "AACC_Personalidad", "C": "AACC_Interpersonal", "D": "AACC_Intereses_Actitudes"}
    for a, col in sums.items():
        assert (d[[f"ACI_{a}{i}" for i in range(1, 10)]].sum(axis=1) == d[col]).all(), a
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    t = long(d, ITEMS, covs, valid=range(1, 10), extra=("rater",))
    t = t[["id", "item", "resp", *covs, "rater"]]
    emit({"izquierdo_lopez_2026_eosp": (t, pv_for(ITEMS, range(1, 10)))})


if __name__ == "__main__":
    main()
