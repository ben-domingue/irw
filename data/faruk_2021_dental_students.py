#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/ycv96d9pf3
# DOI: 10.17632/ycv96d9pf3 (dataset, 2021; Faruk, Shova & Hosen). The record names no published paper.
# Data: "Dental students - Suicidal behaviors and literacy.sav", 468 Bangladeshi dental students:
#       PHQ_1-9 (0-3), GAD_1-7 (0-3), SI/SP/SA month/year/lifetime (9 yes/no suicidal-behaviour items),
#       LOSS_1-12 (true/false/don't know -- not shipped: a 3-option knowledge item with no key in the
#       deposit), SOSS_1-16 (1-5 stigma of suicide). "English Questionnaire.docx" is the instrument.
# License: CC BY 4.0 (Mendeley Data).
#
# Item text: shipped for phq9 and gad7 (.sav variable labels = stems, value labels = anchors) and for
#   soss (no variable labels; value labels give the anchors, stems from the deposited English
#   questionnaire, keyed by the printed SOSS-k number = column SOSS_k). suicidal_behavior: not shipped
#   (3 questions x 3 windows, stems are in the questionnaire but the yes/no items are not a scale).
#
# Tables: faruk_2021_phq9 (468 x 9, 0-3), faruk_2021_gad7 (468 x 7, 0-3), faruk_2021_soss (468 x 16,
#   1-5), faruk_2021_suicidal_behavior (468 x 9, 0 no / 1 yes).
# Covariates: cov_gender (1 female, 2 male), cov_institute_location (1 inside Dhaka, 2 outside),
#   cov_study_year (1-4), cov_residence (1 urban, 2 rural), cov_religion (1 Islam, 2 other),
#   cov_family_type (1 nuclear, 2 joint), cov_family_income (1 <15000, 2 15000-30000, 3 >30000 BDT),
#   cov_smoker (1 yes, 2 no), cov_substance_use (1 yes, 2 no).
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

import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "md_ycv96d9pf3"
FNAME = "Dental students - Suicidal behaviors and literacy.sav"
COVS = {"Gender": "cov_gender", "Institute": "cov_institute_location", "Study_yr": "cov_study_year",
        "Residnce": "cov_residence", "Religion": "cov_religion", "Familytype": "cov_family_type",
        "Income": "cov_family_income", "Smoker": "cov_smoker", "Drug": "cov_substance_use"}
PHQ = [f"PHQ_{i}" for i in range(1, 10)]
GAD = [f"GAD_{i}" for i in range(1, 8)]
SOSS = [f"SOSS_{i}" for i in range(1, 17)]
SB = [f"{a}_{b}" for a in ("SI", "SP", "SA") for b in ("Month", "Year", "Lifetime")]


def labels():
    _, meta = pyreadstat.read_sav(str(mendeley_fetch("ycv96d9pf3", FNAME, RAW_DIR)), metadataonly=True)
    return meta.column_names_to_labels, meta.variable_value_labels


def main() -> None:
    d, meta = pyreadstat.read_sav(str(mendeley_fetch("ycv96d9pf3", FNAME, RAW_DIR)))
    assert len(d) == 468
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    for c in SB:
        d[c] = d[c].map({1.0: 0, 2.0: 1})  # 1 No, 2 Yes -> 0/1
    emit({
        "faruk_2021_phq9": (long(d, PHQ, covs, valid=range(0, 4)), pv_for(PHQ, range(0, 4))),
        "faruk_2021_gad7": (long(d, GAD, covs, valid=range(0, 4)), pv_for(GAD, range(0, 4))),
        "faruk_2021_soss": (long(d, SOSS, covs, valid=range(1, 6)), pv_for(SOSS, range(1, 6))),
        "faruk_2021_suicidal_behavior": (long(d, SB, covs, valid=(0, 1)), pv_for(SB, (0, 1))),
    })


if __name__ == "__main__":
    main()
