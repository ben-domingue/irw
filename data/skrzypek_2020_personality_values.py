#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/d4yd7trhnx
# DOI: 10.17632/d4yd7trhnx (dataset, 2020; the record names no published paper)
#   Skrzypek, M., Turska, D., Szostak-Węgierek, D., & Ostrowska, L. (2020). Dietetics students
#   declaring a preference for direct work with patients show a poor personality predisposition
#   to use the patient-centered counseling approach. Mendeley Data, V1.
# Data: DATA.sav, 390 Polish dietetics students: neo1-neo60, the NEO Five-Factor Inventory
#       (0-4), and val1-val56, the Schwartz Value Survey (-1 "opposed to my values" .. 7 "of
#       supreme importance"). The scale/facet columns (Power .. Agreeableness) are the authors'
#       scores. Items carry no labels (both levels empty). Nine NEO cells (6, 11, 15, 32-34, 45) and two
#       SVS cells (63, 70) hold out-of-range values and are dropped as entry errors.
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: not shipped -- positional codes with no labels, and both instruments are `block`
#   rows in itemtext/instrument_rights_register.csv (NEO-FFI / PAR; Schwartz SVS).
#
# Tables: skrzypek_2020_neo_ffi (60, 0-4), skrzypek_2020_svs (56, -1..7).
# Covariates: cov_age (years), cov_gender (1 F, 2 M), cov_specialty (1-16 per value labels),
#   cov_level (1 first-cycle, 2 second-cycle), cov_year (1-3).
# id: row index (no respondent identifier in the file).
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

RAW_DIR = RAW_ROOT / "10_17632_d4yd7trhnx"
FNAME = "DATA.sav"
COVS = {"age": "cov_age", "sex": "cov_gender", "speciality": "cov_specialty", "level": "cov_level",
        "year": "cov_year"}
NEO = [f"neo{i}" for i in range(1, 61)]
SVS = [f"val{i}" for i in range(1, 57)]


def main() -> None:
    d, meta = pyreadstat.read_sav(str(mendeley_fetch("d4yd7trhnx", FNAME, RAW_DIR)))
    assert len(d) == 390
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    for name, items, valid in (("neo", NEO, range(0, 5)), ("svs", SVS, range(-1, 8))):
        bad = d[items].stack().loc[lambda s: ~s.isin(valid)]
        print(f"    {name}: dropping {len(bad)} out-of-range cells (entry errors): {sorted(bad.unique())}")
        for c in items:
            d.loc[~d[c].isin(valid), c] = pd.NA
    emit({"skrzypek_2020_neo_ffi": (long(d, NEO, covs, valid=range(0, 5)), pv_for(NEO, range(0, 5))),
          "skrzypek_2020_svs": (long(d, SVS, covs, valid=range(-1, 8)), pv_for(SVS, range(-1, 8)))})


if __name__ == "__main__":
    main()
