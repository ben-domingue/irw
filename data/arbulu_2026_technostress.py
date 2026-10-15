#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Digital_Competence_as_a_Personal_Resource_Against_Technostress_Among_Peruvian_University_Faculty_A_Latent-Variable_Study_with_Age-Group_Differences/33716161
# DOI: 10.6084/m9.figshare.33716161 (dataset, 2026; Arbulú Castillo, Arbulú & Saavedra Torres). The
#   record names no paper DOI.
# Data: S2_Dataset_clean.xlsx sheet data, 384 Peruvian university faculty: P1-P20 (14 administered
#       items of a 20-item Digital Competence Questionnaire, 1-7) and I1-I22 technostress (0-6); the
#       `careless` flag marks respondents the authors screened (dropped here). Dimension means and
#       sum scores are not shipped. S1_Supplementary_Tables.pdf documents the models, not the wording.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped -- the sheet's dictionary tab describes variables only; stems are not in the
#   deposit.
#
# Tables: arbulu_2026_digital_competence (14 items, 1-7), arbulu_2026_technostress (22 items, 0-6);
#   careless == 0 respondents.
# Covariates: cov_sex (Female/Male), cov_age.
# id: the file's id column.
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

RAW_DIR = RAW_ROOT / "fs_33716161"
FNAME = "S2_Dataset_clean.xlsx"


def main() -> None:
    d = pd.read_excel(figshare_fetch(33716161, FNAME, RAW_DIR), sheet_name="data")
    assert len(d) == 384 and d["id"].is_unique
    n_care = int(d["careless"].sum())
    d = d[d["careless"] == 0].reset_index(drop=True)
    print(f"dropped {n_care} careless-flagged respondents")
    d["cov_sex"] = d["Sex"]
    d["cov_age"] = d["Age"].astype("Int64")
    covs = ["cov_sex", "cov_age"]
    P = [c for c in d.columns if re.fullmatch(r"P\d+", c)]
    I = [c for c in d.columns if re.fullmatch(r"I\d+", c)]
    assert len(P) == 14 and len(I) == 22
    emit({"arbulu_2026_digital_competence": (long(d, P, covs, valid=range(1, 8)), pv_for(P, range(1, 8))),
          "arbulu_2026_technostress": (long(d, I, covs, valid=range(0, 7)), pv_for(I, range(0, 7)))})


if __name__ == "__main__":
    main()
