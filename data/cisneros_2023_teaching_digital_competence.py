#!/usr/bin/env python3
# Source: https://zenodo.org/records/10055380
# DOI: 10.5281/zenodo.10055380 (data, 2023; Cisneros Barahona, Márques Molías & Samaniego Erazo).
#   "Validation of an instrument for the evaluation of teaching digital competence".
# Data: "spss data.sav", 511 university lecturers (Ecuador, Spanish): D1.1-D1.6, D2.1-D2.5, D3.1-D3.5,
#       D4.1-D4.6 (22 items) each a self-placed proficiency level coded 0/25/50/75/100 (No iniciado /
#       Principiante / Medio / Experto / Transformador) -> 0-4 here. TD1-4, TCDD and D1-D4/DG are the
#       authors' dimension scores.
# License: CC BY 4.0 (Zenodo).
#
# Item text: shipped (.sav variable labels = Spanish stems with the printed item number, value labels =
#   the five level names; Spanish administration). Built by
#   automated_finding/itemtext_verification/make_itemtext_cisneros_2023.py.
#
# Table: cisneros_2023_digital_competence (511 x 22, 0-4); item = the .sav column name (D1.1).
# Covariates: cov_gender (1 male, 2 female), cov_years_experience (1-5 bands), cov_age (1-5 bands),
#   cov_faculty (1-4), cov_employment (1 titular, 2 ocasional), cov_dedication (1 full, 2 half, 3 part
#   time), cov_doctorate (1 yes, 2 no).
# id: row index.
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

RAW_DIR = RAW_ROOT / "zn_10055380"
FNAME = "spss data.sav"
ITEMS = [f"D1.{i}" for i in range(1, 7)] + [f"D2.{i}" for i in range(1, 6)] + [f"D3.{i}" for i in range(1, 6)] + [f"D4.{i}" for i in range(1, 7)]
COVS = {"Género": "cov_gender", "Años_de_experiencia_docente": "cov_years_experience", "Edad": "cov_age",
        "Facultad": "cov_faculty", "Relación_laboral": "cov_employment", "Tiempo_de_dedicación": "cov_dedication",
        "Grado_doctoral": "cov_doctorate"}
LEVEL = {0.0: 0, 25.0: 1, 50.0: 2, 75.0: 3, 100.0: 4}


def labels():
    _, meta = pyreadstat.read_sav(str(zenodo_fetch(10055380, FNAME, RAW_DIR)), metadataonly=True)
    return meta.column_names_to_labels, meta.variable_value_labels


def main() -> None:
    d, meta = pyreadstat.read_sav(str(zenodo_fetch(10055380, FNAME, RAW_DIR)))
    assert len(d) == 511
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    for c in ITEMS:
        assert set(d[c].dropna().unique()) <= set(LEVEL), c
        d[c] = d[c].map(LEVEL)
    t = long(d, ITEMS, covs, valid=range(0, 5))
    emit({"cisneros_2023_digital_competence": (t, pv_for(ITEMS, range(0, 5)))})


if __name__ == "__main__":
    main()
