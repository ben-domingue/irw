#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/26506
# DOI: 10.7910/DVN/26506 (dataset). Paper: Schoen, Harald (2007). Personality Traits and
#   Foreign Policy Attitudes in German Public Opinion. Journal of Conflict Resolution 51,
#   408-430.
# Data: replication_schoen.dta: 2,544 respondents of a 2002 German survey; the NEO-FFI,
#       60 items on 1-5 (starke Ablehnung .. starke Zustimmung), FR41_1 .. FR41_60 with the
#       German stems in the variable labels; 2,503 answered at least one item. The foreign
#       policy items (FR29_*, four heterogeneous 0-6 scales) are not shipped.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped -- rights. The NEO-FFI (PAR / Hogrefe) is a `block` row in
#   itemtext/instrument_rights_register.csv; the German stems are in the .dta variable
#   labels (checked; value labels give the two end anchors).
#
# One table: schoen_2007_neoffi, item = neoffi_1 .. neoffi_60 (the NEO-FFI item number
#   from the variable name), resp 1-5.
# Covariates: cov_gender (1 weiblich, 2 maennlich), cov_age, cov_education (FRS16, 1-7),
#   cov_region_1989 (FRS18: lived in West 1 / East 2 Germany before 1989, as coded).
# id: row index of the .dta.

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

RAW_DIR = RAW_ROOT / "10_7910_dvn_26506"


def main() -> None:
    d, meta = pyreadstat.read_dta(str(dv_fetch("10.7910/DVN/26506", "replication_schoen.dta", RAW_DIR)))
    assert len(d) == 2544
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns={"FRS19": "cov_gender", "ALTER": "cov_age", "FRS16": "cov_education", "FRS18": "cov_region_1989"})
    covs = ["cov_gender", "cov_age", "cov_education", "cov_region_1989"]
    for c in covs:
        d[c] = pd.to_numeric(d[c], errors="coerce").astype("Int64")
    rename = {f"FR41_{k}": f"neoffi_{k}" for k in range(1, 61)}
    assert set(rename) <= set(d.columns)
    t = long(d, list(rename), covs, valid=range(1, 6), rename=rename)
    emit({"schoen_2007_neoffi": (t, pv_for(rename.values(), range(1, 6)))})


if __name__ == "__main__":
    main()
