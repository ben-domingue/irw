#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Three_Dimensions_of_Teachers_Job_Burnout/33113030
# DOI: 10.6084/m9.figshare.33113030 (dataset, v2 2026; the record names no published paper)
#   Zhang, L. (2026). Three Dimensions of Teachers' Job Burnout. figshare.
# Data: PE teacher burnout data.sav, 560 Chinese primary/secondary physical-education teachers:
#       SJ1-5, TD1-4, CJ1-6 job burnout (15 items, 1-7; JobBurnout = sum), JS1-6, XW1-5, JZ1-4,
#       GS1-3 professional identity (18 items, 1-5; role values, behavioural tendency,
#       occupational values, belonging), HL1-3, FX1-3, ZZ1-3 work engagement (UWES-9, 1-7;
#       vigor, dedication, absorption). No labels on any column (both levels empty).
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped -- no labels in the file, codes are positional pinyin initials, and
#   the UWES is a `block` row in the rights register.
#
# Tables: zhang_2026_pe_burnout (15, 1-7), zhang_2026_pe_identity (18, 1-5),
#   zhang_2026_pe_uwes9 (9, 1-7).
# Covariates: cov_gender (1/2), cov_age (1-4 bands), cov_ethnicity (text as deposited, e.g.
#   Han, Miao), cov_education (2-4), cov_region (1-9), cov_teaching_years (1-6), cov_school
#   (1-3), cov_title (1-5) -- codes undocumented in the deposit.
# id: the deposit's ID column.
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

RAW_DIR = RAW_ROOT / "figshare_33113030"
FNAME = "PE teacher burnout data.sav"
COVS = {"Gender": "cov_gender", "Age": "cov_age", "Ethnicity": "cov_ethnicity", "Education": "cov_education",
        "Region": "cov_region", "Years": "cov_teaching_years", "School": "cov_school", "Professional": "cov_title"}
BURN = [f"SJ{i}" for i in range(1, 6)] + [f"TD{i}" for i in range(1, 5)] + [f"CJ{i}" for i in range(1, 7)]
IDENT = ([f"JS{i}" for i in range(1, 7)] + [f"XW{i}" for i in range(1, 6)] + [f"JZ{i}" for i in range(1, 5)]
         + [f"GS{i}" for i in range(1, 4)])
UWES = [f"HL{i}" for i in range(1, 4)] + [f"FX{i}" for i in range(1, 4)] + [f"ZZ{i}" for i in range(1, 4)]


def main() -> None:
    d, meta = pyreadstat.read_sav(str(figshare_fetch(33113030, FNAME, RAW_DIR)))
    assert len(d) == 560 and d["ID"].is_unique
    d = d.rename(columns={"ID": "id", **COVS})
    d["id"] = d["id"].astype(int)
    covs = list(COVS.values())
    for c in covs:
        if c != "cov_ethnicity":
            d[c] = d[c].astype("Int64")
    emit({"zhang_2026_pe_burnout": (long(d, BURN, covs, valid=range(1, 8)), pv_for(BURN, range(1, 8))),
          "zhang_2026_pe_identity": (long(d, IDENT, covs, valid=range(1, 6)), pv_for(IDENT, range(1, 6))),
          "zhang_2026_pe_uwes9": (long(d, UWES, covs, valid=range(1, 8)), pv_for(UWES, range(1, 8)))})


if __name__ == "__main__":
    main()
