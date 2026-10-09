#!/usr/bin/env python3
# Source: https://doi.org/10.5281/zenodo.20634
# DOI: 10.5281/zenodo.20634 (dataset: the SPSS file of a master's thesis, Programa de
#   Maestria para Docentes de la Region Callao, Escuela de Postgrado)
#   Arista-Huaco, Manuel Jesus (2010). Motivacion de logro en educacion fisica y capacidades
#   motrices en alumnos de una institucion educativa publica del distrito de Bellavista
#   [Data set]. Zenodo.
# Data: "2010_Arista_Motivacion_de_logro_en_educacion_fisica_y_capacidades_motrices_en_
#       alumnos_de_una_institucion_educativa_publica_del_distrito_de_Bellavis.sav": 140
#       secondary-school pupils (all girls, ages 15-18) x Edad, Sexo, item1-item37 and
#       five empty trailing variables. The record: "La matriz de datos contiene las
#       siguientes variables: Edad, Sexo y 37 items."
# License: CC0 1.0 (Zenodo record).
#
# Item text: not shipped. Variable labels repeat the variable names ("item1"); the value
#   labels give the five anchors (1 totalmente en desacuerdo, 2 en desacuerdo, 3 indeciso,
#   4 de acuerdo, 5 totalmente de acuerdo) but no item wording is in the file, and the
#   thesis is not deposited.
#
# Table arista_2010_achievement_motivation: item1-item37, 1-5 as stored; one table (the
#   record and file give no subscale structure). Several items correlate about zero with
#   the rest (item1, item9, item11, item14, item26: item-rest r -.02 to .07), consistent
#   with negatively worded items left unreversed; shipped as stored.
# Skipped: VAR00001-VAR00005 (empty SPSS filler; one stray 3 in VAR00005), Sexo
#   (constant: all 2 femenino).
# Covariate: cov_age (Edad).
# id: row index (no id column).

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
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any()
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


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=()) -> pd.DataFrame:
    """Melt, drop missing, check integer codes inside `valid`, order columns."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", "item"]).reset_index(drop=True)


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


def dryad_file(path: Path) -> Path:
    """Dryad file downloads need a browser session (an Anubis challenge, then a 403 to
    plain HTTP clients), so the file is placed by hand: open the dataset page in a
    browser, download the file, and put it at `path`."""
    if not path.exists():
        raise SystemExit(f"missing {path}: download it from the Dryad dataset page "
                         "(plain HTTP downloads are refused) and rerun")
    return path
import pyreadstat

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5281_zenodo.20634"
FNAME = ("2010_Arista_Motivacion_de_logro_en_educacion_fisica_y_capacidades_motrices_en_alumnos_"
         "de_una_institucion_educativa_publica_del_distrito_de_Bellavis.sav")
URL = "https://zenodo.org/api/records/20634/files/" + FNAME + "/content"
ITEMS = [f"item{i}" for i in range(1, 38)]


def main() -> None:
    d, meta = pyreadstat.read_sav(str(download(URL, RAW_DIR / FNAME)))
    assert d.shape == (140, 44)
    filler = [f"VAR0000{i}" for i in range(1, 6)]
    assert set(ITEMS) | set(filler) | {"Edad", "Sexo"} == set(d.columns)
    assert d[filler].notna().sum().sum() == 1 and (d["Sexo"] == "2").all()
    assert meta.variable_value_labels["item1"][5.0] == "TOTALMENTE DE ACUERDO"
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d["cov_age"] = d["Edad"].astype("Int64")
    emit({"arista_2010_achievement_motivation": (long(d, ITEMS, ["cov_age"], valid=range(1, 6)),
                                                 {i: set(range(1, 6)) for i in ITEMS})})


if __name__ == "__main__":
    main()
