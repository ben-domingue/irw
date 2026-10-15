#!/usr/bin/env python3
# Source: https://zenodo.org/records/18566680
# DOI: 10.5281/zenodo.18566680 (dataset, 2026; paper "submitted to Frontiers in Public Health")
#   Duplaga, M. (2026). Assessing nurses' digital competence for public health systems:
#   validation of a brief instrument and factors associated with competence [dataset]. Zenodo.
# Data: Dataset.xlsx, sheet "Dataset": 800 Polish nurses; DL_1-DL_12 the Digital Competence
#       Questionnaire for Nurses (1 decidedly disagree .. 5 decidedly agree) and EH1-EH10 the
#       eHealth Literacy Scale (same anchors). SOFT_1-15 (yes/no use of hospital software) and
#       the three score columns are not shipped. Sheet "Variables" is the codebook (codes and
#       categories, no item wording).
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped -- the codebook lists "Item 1 .. Item 12" without wording and the
#   data has no labels; the administered Polish wording is not in the deposit.
#
# Tables: duplaga_2026_dcqfn (12, 1-5), duplaga_2026_eheals (10, 1-5).
# Covariates: cov_age (years), cov_gender (0 female, 1 male), cov_residence (0 rural .. 4
#   >500k), cov_education (0 secondary .. 3 PhD), cov_internet_use (0-3), cov_social_media_use
#   (0-3), cov_specialist (0/1), cov_hospital (0/1), cov_private_facility (0/1).
# id: the deposit's id column.
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

RAW_DIR = RAW_ROOT / "zenodo_18566680"
FNAME = "Dataset.xlsx"
COVS = {"AGE": "cov_age", "SEX": "cov_gender", "RESID": "cov_residence", "EDUC": "cov_education",
        "INTERNET": "cov_internet_use", "SOCMED": "cov_social_media_use", "SPEC": "cov_specialist",
        "HOSPITAL": "cov_hospital", "PRIV": "cov_private_facility"}
DL = [f"DL_{i}" for i in range(1, 13)]
EH = [f"EH{i}" for i in range(1, 11)]


def main() -> None:
    d = pd.read_excel(zenodo_fetch(18566680, FNAME, RAW_DIR), sheet_name="Dataset")
    assert len(d) == 800 and d["id"].is_unique
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    emit({"duplaga_2026_dcqfn": (long(d, DL, covs, valid=range(1, 6)), pv_for(DL, range(1, 6))),
          "duplaga_2026_eheals": (long(d, EH, covs, valid=range(1, 6)), pv_for(EH, range(1, 6)))})


if __name__ == "__main__":
    main()
