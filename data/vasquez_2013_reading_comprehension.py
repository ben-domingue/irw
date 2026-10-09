#!/usr/bin/env python3
# Source: https://doi.org/10.5281/zenodo.22707
# DOI: 10.5281/zenodo.22707 (dataset: the SPSS file of a master's thesis, Programa de
#   Maestria para Docentes de la Region Callao, Escuela de Postgrado)
#   Vasquez-Camarena, Esperanza (2013). Comprension lectora, segun genero, en alumnos del
#   sexto grado de una institucion educativa del distrito del Callao [Data set]. Zenodo.
# Data: "2013_Vasquez_Comprension_lectora_segun_genero_en_alumnos_del_sexto_grado_de_una_
#       institucion_educativa_del_distrito_del_Callao.sav": 120 sixth-grade pupils (plus
#       one empty row) x Participante1, genero, turno, grado, 28 reading-comprehension
#       items scored 0 error / 1 acierto (value labels), four dimension totals and four
#       level codes. The item names encode the dimension and the item's position in the
#       test: cl = comprension literal (items 4, 9, 10, 11, 16, 18, 19, 23, 24),
#       co = reorganizacion (5, 6, 8, 17, 20, 21, 27), ci = inferencial (1, 3, 7, 13, 14,
#       22, 25, 26, 28), cc = critica (2, 12, 15).
# License: CC0 1.0 (Zenodo record).
#
# Item text: not shipped. Variable labels are empty; value labels give only
#   error/acierto; the reading passages and questions are not deposited.
#
# Table vasquez_2013_reading_comprehension: the 28 items, 0/1. Item codes are the
#   deposit's names except c021 and c027, renamed co21 and co27 (a zero typed for the
#   letter o: they sit in the reorganizacion block and the co total counts them). The
#   nine literal-comprehension items are 1 for every pupil (the deposit's cl total is 9
#   and its level "alto" for all 120); they are shipped as recorded.
# Skipped: puntajetotal, puntajetotalcl/co/ci/cc (totals), niveldecl/co, nivelci/cc
#   (level codes).
# Covariates: cov_gender (genero: 1 femenino, 2 masculino), cov_shift (turno: 1 manana,
#   2 tarde), cov_section (grado: 1-4 = sexto A-D).
# id: Participante1 (1-120).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5281_zenodo.22707"
FNAME = ("2013_Vasquez_Comprension_lectora_segun_genero_en_alumnos_del_sexto_grado_de_una_"
         "institucion_educativa_del_distrito_del_Callao.sav")
URL = "https://zenodo.org/api/records/22707/files/" + FNAME + "/content"
RENAME = {"c021": "co21", "c027": "co27"}
COVS = {"género": "cov_gender", "turno": "cov_shift", "grado": "cov_section"}
TOTALS = ["puntajetotal", "puntajetotalcl", "puntjtotalco", "puntajetotalci", "puntajetotalcc",
          "niveldecl", "niveldeco", "nivelci", "nivelcc"]


def main() -> None:
    d, meta = pyreadstat.read_sav(str(download(URL, RAW_DIR / FNAME)))
    d = d[d["Participante1"].notna()].copy()
    assert d.shape == (120, 41) and d["Participante1"].is_unique
    items = [c for c in d.columns if c not in COVS and c not in TOTALS and c != "Participante1"]
    assert len(items) == 28
    d = d.rename(columns=RENAME)
    items = [RENAME.get(c, c) for c in items]
    num = {c: int(c[2:]) for c in items}
    assert sorted(num.values()) == list(range(1, 29))
    for pre, tot in (("cl", "puntajetotalcl"), ("co", "puntjtotalco"), ("ci", "puntajetotalci"),
                     ("cc", "puntajetotalcc")):
        blk = [c for c in items if c.startswith(pre)]
        ok = (d[blk].sum(axis=1) == d[tot]) | d[blk].isna().any(axis=1)
        assert ok.all(), pre
    d["id"] = d["Participante1"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    items = sorted(items, key=num.get)
    emit({"vasquez_2013_reading_comprehension": (long(d, items, covs, valid=(0, 1)),
                                                 {i: {0, 1} for i in items})})


if __name__ == "__main__":
    main()
