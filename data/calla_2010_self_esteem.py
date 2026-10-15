#!/usr/bin/env python3
# Source: https://zenodo.org/records/20654
# DOI: 10.5281/zenodo.20654 (dataset, 2010; Calla-Colana, Zublema Liliana). "Autoestima y rendimiento
#   academico en el area personal social en alumnos de quinto ciclo de primaria de una institucion
#   educativa del Callao" (thesis data, Peru).
# Data: the single .sav, 100 fifth/sixth-grade pupils. I1-I16, a 16-item self-esteem questionnaire on
#       1-5 (variable labels "Item 1" .. "Item 20" with 5, 9, 13 and 18 absent, i.e. 16 of an original
#       20 items were retained; the labels are positional, no stems). Subscale totals (identidad,
#       conocimiento, autovaloracion, sentimiento de pertenencia, dominio, sentimiento de utilidad), the
#       total, the level categories and the academic-performance grade are not shipped.
#       SUJETO has one duplicated value (99 distinct for 100 rows), so id is the row index.
# License: CC0 1.0 (Zenodo record).
#
# Item text: not shipped -- variable labels are positional ("Item 7"); value labels exist only for
#   GRADO/SEXO/level variables, not for the items; the questionnaire is not in the deposit.
#
# Table: calla_2010_self_esteem (16 items, 1-5; N = 100, exactly at the floor).
# Covariates: cov_grade (1 5to primaria, 2 6to primaria), cov_sex (1 masculino, 2 femenino),
#   cov_academic_grade (REN_ACAD, 11-17 on the Peruvian 0-20 scale).
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


def osf_fetch(node: str, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://api.osf.io/v2/nodes/{node}/files/osfstorage/", headers=UA, timeout=120).json()
        url = [f["links"]["download"] for f in j["data"] if f["attributes"]["name"] == fname][0]
        download(url, p)
    return p
import re

RAW_DIR = RAW_ROOT / "zen_20654"
FNAME = ("2010_Calla_Autoestima_y_rendimiento_academico_en_el_area_personal_social_en_alumnos_de_quinto_"
         "ciclo_de_primaria_de_una_institucion_educativa_del_Ca.sav")


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(str(zenodo_fetch(20654, FNAME, RAW_DIR)))
    assert len(d) == 100
    d["id"] = range(1, len(d) + 1)
    d["cov_grade"] = d["GRADO"].astype(int); d["cov_sex"] = d["SEXO"].astype(int)
    d["cov_academic_grade"] = d["REN_ACAD"].astype(int)
    items = [c for c in d.columns if re.fullmatch(r"I\d+", c)]
    assert len(items) == 16
    emit({"calla_2010_self_esteem": (long(d, items, ["cov_grade", "cov_sex", "cov_academic_grade"], valid=range(1, 6)),
                                     pv_for(items, range(1, 6)))})


if __name__ == "__main__":
    main()
