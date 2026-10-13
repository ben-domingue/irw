#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/3SCNGV (Harvard Dataverse; the same file is on Mendeley
#   Data as 10.17632/yxp8rbjrn8.1, CC BY 4.0)
# DOI: 10.7910/DVN/3SCNGV (dataset; the record names no paper)
#   Asadollahi, Abdolrahim (2022). Falls efficacy scale-international (the short version)
#   among Iranian older people. Harvard Dataverse, V1.
# Data: "Soroush Mega Data_ 12 Aban 1400.sav": 9,117 Iranian adults aged 60+ (survey of
#       mid-2021, Aban 1400): the Short FES-I, 7 items on 1-4 (FES.1 .. FES.7), with
#       demographic codes; the UCLA/GDS/GAI/frailty columns are totals only.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. The FES items carry no variable or value labels (checked both
#   levels; the demographic variables are labelled); the Short FES-I wording is ProFaNE's.
#
# One table: asadollahi_2022_short_fesi, item = FES.1 .. FES.7, resp 1-4.
# Covariates: cov_age (years old in 2021), cov_education (1-5, labelled in the .sav),
#   cov_marital_status (1-5), cov_job (1-6), cov_living_with (1-4), cov_fall_history
#   (1 yes, 2 no), cov_needs_adl_support (1 yes, 2 no).
# id: the deposit's ID.

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

RAW_DIR = RAW_ROOT / "10_7910_dvn_3scngv"
FNAME = "Soroush Mega Data_ 12 Aban 1400.sav"
COVS = {"YO.in.2021": "cov_age", "Edu": "cov_education", "MaritalS": "cov_marital_status", "Job": "cov_job",
        "LivW": "cov_living_with", "History.of.Falls": "cov_fall_history", "NADLS": "cov_needs_adl_support"}


def main() -> None:
    d, meta = pyreadstat.read_sav(str(dv_fetch("10.7910/DVN/3SCNGV", FNAME, RAW_DIR)))
    assert len(d) == 9117 and d["ID"].is_unique
    d = d.rename(columns={"ID": "id", **COVS})
    d["id"] = d["id"].astype(int)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    items = [f"FES.{k}" for k in range(1, 8)]
    emit({"asadollahi_2022_short_fesi": (long(d, items, covs, valid=range(1, 5)), pv_for(items, range(1, 5)))})


if __name__ == "__main__":
    main()
