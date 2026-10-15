#!/usr/bin/env python3
# Source: https://zenodo.org/records/21566065
# DOI: 10.5281/zenodo.21566065 (dataset, 2026-07-25; Montenegro Villarreal, Jessica Alexandra; Mantilla
#   Hidalgo, Monica). "Digital Competence Is Indirectly Associated with Technology Acceptance: A
#   UTAUT-IKANOS Structural Equation Model in Engineering Students".
# Data: "Data_set_ikanos_utaut.xlsx", sheet Datos_SEM: 309 first/second-semester engineering students
#       (Escuela Politecnica Nacional, Ecuador): PE1-3 performance expectancy, EE1-4 effort expectancy,
#       SI1-3 social influence, BI1-3 behavioural intention (adapted UTAUT, 1-5 Likert). IK_* are
#       IKANOS digital-competence test scores (composites, not item-level), not shipped. Sheet
#       Diccionario documents variables at block level only.
# License: CC BY 4.0 (Zenodo).
#
# Item text: not shipped -- code headers only; the dictionary names each block, not the items.
#
# Table: montenegro_villarreal_2026_utaut (13 items, 1-5, four UTAUT blocks in one table); 309 ids = the
#   file's ID. Covariates: cov_semester (1/2), cov_gender (1 masculino, 2 femenino), cov_age,
#   cov_device (1 smartphone, 2 tablet, 3 laptop/desktop), cov_internet (1 fixed home, 2 university
#   network, 3 mobile data).
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


def dans_fetch(doi: str, fname: str, raw_dir: Path) -> Path:
    """Download one original-format file of a DANS Data Station (Dataverse) dataset."""
    return dv_fetch(doi, fname, raw_dir, host="ssh.datastations.nl")
RAW_DIR = RAW_ROOT / "C_63_21566065"
FNAME = "Data_set_ikanos_utaut.xlsx"
ITEMS = ["PE1", "PE2", "PE3", "EE1", "EE2", "EE3", "EE4", "SI1", "SI2", "SI3", "BI1", "BI2", "BI3"]


def main() -> None:
    d = pd.read_excel(zenodo_fetch(21566065, FNAME, RAW_DIR), sheet_name="Datos_SEM")
    assert len(d) == 309 and d["ID"].is_unique
    d["id"] = d["ID"].astype(int)
    d["cov_semester"] = d["SEMESTRE"].astype("Int64")
    d["cov_gender"] = d["SEXO"].str.strip().map({"Masculino": 1, "Femenino": 2}).astype("Int64")
    d["cov_age"] = d["EDAD"].astype("Int64")
    d["cov_device"] = d["DISPOSITIVO"].str.strip().map(
        {"Teléfono Inteligente": 1, "Tablet": 2, "Laptot or Deskstop Computer": 3}).astype("Int64")
    d["cov_internet"] = d["INTERNET"].str.strip().map(
        {"Internet fijo en casa": 1, "Red de la Universidad": 2, "Datos móviles": 3}).astype("Int64")
    covs = ["cov_semester", "cov_gender", "cov_age", "cov_device", "cov_internet"]
    assert d[covs].notna().all().all()
    emit({"montenegro_villarreal_2026_utaut": (long(d, ITEMS, covs, valid=range(1, 6)), pv_for(ITEMS, range(1, 6)))})


if __name__ == "__main__":
    main()
