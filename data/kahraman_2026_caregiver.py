#!/usr/bin/env python3
# Source: https://zenodo.org/records/20381044
# DOI: 10.5281/zenodo.20381044 (dataset; the record names no paper)
#   Kahraman, Emir Gökhan (2026). Anonymized Raw Dataset of Caregiver Burden and Anxiety
#   Among Relatives of Cancer Patients Undergoing Active Chemotherapy (N = 494). Zenodo.
# Data: database_en.xlsx: 494 informal caregivers at Izmir City Hospital outpatient
#       chemotherapy units (Oct 2025 - May 2026; complete cases of 634 screened), with
#       the Zarit Burden Interview as administered (19 items, 1-5) and the Beck Anxiety
#       Inventory (21 items, stored 1-4), plus caregiver and patient background.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped -- rights. Column headers are codes only (ZBI-1, BAI-7); the ZBI
#   (Mapi Research Trust) and the BAI (Pearson, a `block` row in
#   itemtext/instrument_rights_register.csv) are licensed instruments.
#
# Tables:
#   kahraman_2026_zbi  ZBI-1..ZBI-19 as deposited (the file has 19 ZBI columns, not the
#                      22-item form; item = the header), resp 1-5.
#   kahraman_2026_bai  BAI-1..BAI-21, resp 1-4 as stored (the BAI's 0-3 shifted by one).
# Covariates (strings as deposited unless noted): cov_caregiver_age, cov_caregiver_gender,
#   cov_marital_status, cov_education, cov_income, cov_relationship (to the patient),
#   cov_living_with_patient, cov_caregiving_months, cov_patient_age, cov_patient_gender,
#   cov_cancer_type, cov_chemo_duration.
# id: the deposit's "Caregiver ID" (caregiver1 ..), kept as the integer suffix.

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

RAW_DIR = RAW_ROOT / "10_5281_zenodo_20381044"
COVS = {"Caregiver Age": "cov_caregiver_age", "Caregiver Gender": "cov_caregiver_gender",
        "Marital Status": "cov_marital_status", "Caregiver Education Level": "cov_education",
        "Monthly Income Status": "cov_income", "Relationship to Patient": "cov_relationship",
        "Living with Patient": "cov_living_with_patient",
        "Caregiving Duration (Months)": "cov_caregiving_months", "Patient Age": "cov_patient_age",
        "Patient Gender": "cov_patient_gender", "Cancer Type": "cov_cancer_type",
        "Chemotherapy Duration": "cov_chemo_duration"}


def main() -> None:
    d = pd.read_excel(zenodo_fetch(20381044, "database_en.xlsx", RAW_DIR))
    assert len(d) == 494 and d["Caregiver ID"].is_unique
    d["id"] = d["Caregiver ID"].str.replace("caregiver", "", regex=False).astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    zbi = [c for c in d.columns if c.startswith("ZBI-")]
    bai = [c for c in d.columns if c.startswith("BAI-")]
    assert len(zbi) == 19 and len(bai) == 21, (len(zbi), len(bai))
    emit({"kahraman_2026_zbi": (long(d, zbi, covs, valid=range(1, 6)), pv_for(zbi, range(1, 6))),
          "kahraman_2026_bai": (long(d, bai, covs, valid=range(1, 5)), pv_for(bai, range(1, 5)))})


if __name__ == "__main__":
    main()
