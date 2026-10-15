#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/b6zh5mjd5p
# DOI: 10.17632/b6zh5mjd5p (dataset, 2021-09-20; Habibi, Akhmad). "Data on Physical Education Teachers'
#   Burnout during Pandemic: Structural Equation Modelling".
# Data: "2. Raw Data.xlsx", sheet "Raw data": 241 Indonesian PE teachers during COVID-19 distance learning:
#       TSC1-5 teacher self-concept, TE1-5 teacher efficacy, EE1-5 emotional exhaustion, DP1-3
#       depersonalisation, RPA1-7 reduced personal accomplishment (all 1 strongly disagree - 5 strongly
#       agree). "1. Instrument in English and Indonesian.docx" prints every stem in both languages.
#       Sheet "results" is PLS output. One respondent has no gender.
# License: CC BY 4.0 (Mendeley Data).
#
# Item text: shipped for tsc and te (Indonesian stems + the authors' English, from the instrument docx,
#   positional by printed number within block = column number). Not shipped for burnout: the EE/DP/RPA
#   stems are an MBI adaptation (rights-register block).
#
# Tables: habibi_2021_pe_tsc (5), habibi_2021_pe_te (5), habibi_2021_pe_burnout (15: EE1-5, DP1-3,
#   RPA1-7); 241 ids (row index). Covariates: cov_gender (1 men, 2 women), cov_teaching_level (Lv, 1-3 as
#   coded), cov_school_location (Sloc, 1-3 as coded), cov_school_type (Sc, 1/2 as coded); "ex" is constant.
#   Distinct from habibi_2020_* (Mendeley 6jmv43nffk, 876 teachers) and habibi_2026_* (figshare 31672783).
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
RAW_DIR = RAW_ROOT / "C_66_b6zh5mjd5p"
FNAME = "2. Raw Data.xlsx"
DOCX = "1. Instrument in English and Indonesian.docx"
BLOCKS = {"pe_tsc": [f"TSC{i}" for i in range(1, 6)],
          "pe_te": [f"TE{i}" for i in range(1, 6)],
          "pe_burnout": [f"EE{i}" for i in range(1, 6)] + ["DP1", "DP2", "DP3"] + [f"RPA{i}" for i in range(1, 8)]}
COVS = {"Gd": "cov_gender", "Lv": "cov_teaching_level", "Sloc": "cov_school_location", "Sc": "cov_school_type"}


def instrument_docx() -> Path:
    return mendeley_fetch("b6zh5mjd5p", DOCX, RAW_DIR)


def main() -> None:
    d = pd.read_excel(mendeley_fetch("b6zh5mjd5p", FNAME, RAW_DIR), sheet_name="Raw data")
    assert len(d) == 241
    d["id"] = d.index + 1
    for s, c in COVS.items():
        d[c] = d[s].astype("Int64")
    out = {}
    for k, cols in BLOCKS.items():
        out[f"habibi_2021_{k}"] = (long(d, cols, list(COVS.values()), valid=range(1, 6)), pv_for(cols, range(1, 6)))
    emit(out)


if __name__ == "__main__":
    main()
