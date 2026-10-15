#!/usr/bin/env python3
# Source: https://zenodo.org/records/15359020
# DOI: 10.5281/zenodo.15359020 (dataset, 2025; Gutiérrez Molero, Heredia Ponce & Romero Oliva).
#   "Competencia digital 5º y 6º Educación Primaria"; no paper DOI on the record.
# Data: Tecnología.xlsx, 274 Spanish primary pupils (5th-6th grade, ages 10-13) from five schools:
#       63 self-report items "@1." .. "@63." on a 1-4 scale (knowledge 1-15, skills 16-35, attitudes
#       36-45, emotions 46-63 by the header wording); D1-D4 are the authors' dimension scores. Column
#       headers are SPSS-mangled Spanish stems (spaces removed, "no" -> "2", "si" -> "1").
# License: CC BY 4.0 (Zenodo).
#
# Item text: not shipped -- the only wording is the mangled header text; the instrument is not in the
#   deposit.
#
# Table: gutierrez_2025_pupil_digital_competence (274 x 63, 1-4); item = item_01..item_63 from the
#   "@k." header number (reversible).
# Covariates: cov_school (1-5), cov_sex (1-3 as deposited), cov_age (10-13), cov_grade (1 = 5th, 2 =
#   6th), cov_has_device (1/2), cov_has_internet (1/2).
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

import re  # noqa: E402

RAW_DIR = RAW_ROOT / "zn_15359020"
FNAME = "Tecnología.xlsx"


def main() -> None:
    d = pd.read_excel(zenodo_fetch(15359020, FNAME, RAW_DIR))
    assert len(d) == 274
    d["id"] = d.index + 1
    items = [c for c in d.columns if re.match(r"@\d+\.", str(c))]
    assert len(items) == 63
    ren = {c: f"item_{int(re.match(r'@(\d+)\.', c).group(1)):02d}" for c in items}
    cols = list(d.columns)
    d = d.rename(columns={"Centro": "cov_school", "Sexo": "cov_sex", "Edad": "cov_age", "Curso": "cov_grade",
                          cols[4]: "cov_has_device", cols[5]: "cov_has_internet"})
    covs = ["cov_school", "cov_sex", "cov_age", "cov_grade", "cov_has_device", "cov_has_internet"]
    for c in covs:
        d[c] = d[c].astype("Int64")
    t = long(d, items, covs, valid=range(1, 5), rename=ren)
    emit({"gutierrez_2025_pupil_digital_competence": (t, pv_for(ren.values(), range(1, 5)))})


if __name__ == "__main__":
    main()
