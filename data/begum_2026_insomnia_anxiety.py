#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/sg2whyws4h
# DOI: 10.17632/sg2whyws4h (dataset; the record names no published paper)
#   Begum, Khalib, Mahmud, Piyas et al. (2026). Onidra: A Clinically Annotated Survey Dataset
#   for Insomnia and Anxiety Assessment Based on ISI and HAM-A. Mendeley Data, V1.
# Data: Onidra_Raw_Dataset.xlsx: 10,008 respondents from all eight divisions of Bangladesh
#       (June 2022 - October 2024, 27 enumerators, Aachol Foundation / Daffodil International
#       University), the 7-item Insomnia Severity Index (0-4) and the 14-item Hamilton Anxiety
#       Rating Scale (0-4, self-rated here), sociodemographics and clinician severity labels.
#       The AD1-AD13 lifestyle questions (mixed categorical / multi-select) and the
#       preprocessed copy of the file (integer-coded covariates, totals) are not shipped.
#       One "." in HAM3 is treated as missing.
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: HAM-A shipped (the deposit's "Codebook and Complete Survey Questionnaire.pdf"
#   reproduces the 14 items with their parenthetical symptom lists and the 0-4 anchors;
#   English administration; built by
#   automated_finding/itemtext_verification/make_itemtext_begum_2026.py). ISI not shipped --
#   rights: the Insomnia Severity Index is a `block` row in itemtext/instrument_rights_register.csv
#   (Mapi licence); the wording is in the same PDF, Part-B.
#
# Tables: begum_2026_isi (ISI1..ISI7, 0-4), begum_2026_hama (HAM1..HAM14, 0-4).
# Covariates (as the deposit's text categories): cov_gender (Female/Male/Third), cov_age_group
#   (<18, 18-23, 24-28, >28), cov_living_status, cov_occupation, cov_education_year,
#   cov_marital_status, cov_smoking, cov_alcohol, cov_place_of_education, cov_university_type,
#   cov_sleep_time, cov_clinician_insomnia and cov_clinician_anxiety (the clinicians' final
#   severity labels).
# id: row index (the deposit's Participant ID P000001.. is a study-assigned serial).
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

RAW_DIR = RAW_ROOT / "mendeley_sg2whyws4h"
COVS = {"Gender": "cov_gender", "Age": "cov_age_group", "LivingStatus": "cov_living_status",
        "Occupation": "cov_occupation", "EducationalYear": "cov_education_year",
        "MaritalStatus": "cov_marital_status", "SmokingHabit": "cov_smoking", "Alcohol": "cov_alcohol",
        "Place_of_ Education": "cov_place_of_education", "UniversityType": "cov_university_type",
        "SleepTime": "cov_sleep_time", "Doctor Opinion Insomnia": "cov_clinician_insomnia",
        "Doctor Opinion Anxiety": "cov_clinician_anxiety"}
ISI = [f"ISI{i}" for i in range(1, 8)]
HAM = [f"HAM{i}" for i in range(1, 15)]


def main() -> None:
    d = pd.read_excel(mendeley_fetch("sg2whyws4h", "Onidra_Raw_Dataset.xlsx", RAW_DIR))
    assert len(d) == 10008 and d["Participant ID"].is_unique
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in ISI + HAM:
        d[c] = pd.to_numeric(d[c], errors="coerce")  # one "." in HAM3 -> missing
    emit({
        "begum_2026_isi": (long(d, ISI, covs, valid=range(0, 5)), pv_for(ISI, range(0, 5))),
        "begum_2026_hama": (long(d, HAM, covs, valid=range(0, 5)), pv_for(HAM, range(0, 5))),
    })


if __name__ == "__main__":
    main()
