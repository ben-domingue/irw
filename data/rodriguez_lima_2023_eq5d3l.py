#!/usr/bin/env python3
# Source: https://doi.org/10.5281/zenodo.8242026
# DOI: 10.5281/zenodo.8242026 (dataset; the record names no paper)
#   Rodriguez Lima, David Rene (2023). Validation of the EQ-5D-3L in Patients with Severe
#   COVID-19 One Year After Hospital Discharge [Data set]. Zenodo.
# Data: "Validity EQ-5D-3L.xlsx": sheet "Variable table", 225 patients who underwent
#       invasive mechanical ventilation for COVID-19, assessed one year after discharge
#       (prospective cohort) x 56 columns (demographics, comorbidities, admission
#       laboratory values, EQ1-EQ5, their total, PCFS); sheet "variable dictionary"
#       defines every column ("EQ1 Mobility assessed on a scale of 1 to 3" ...).
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped -- rights. The dictionary names each dimension only, and EQ-5D
#   is a `block` row in itemtext/instrument_rights_register.csv (EuroQol).
#
# Table rodriguez_lima_2023_eq5d3l: EQ1-EQ5 (mobility, self-care, usual activities,
#   pain/discomfort, anxiety/depression), 1-3 as stored (1 no problems .. 3 extreme
#   problems, the EQ-5D-3L levels); item = the deposit's column name.
# Skipped: TOTAL_EQ-5D-3L (the sum, asserted), PCFS (a single 0-4 functional-status
#   grade), the laboratory values and comorbidity flags, weight, height.
# Covariates: cov_age, cov_sex (Male / Female), cov_education (as worded in the file),
#   cov_ards (No ARDS / Mild / Moderate / Severe), cov_charlson (Charlson index).
# id: row index (no id column).

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
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any()
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


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=()) -> pd.DataFrame:
    """Melt, drop missing, check integer codes inside `valid`, order columns."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", "item"]).reset_index(drop=True)


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


def dryad_file(path: Path) -> Path:
    """Dryad file downloads need a browser session (an Anubis challenge, then a 403 to
    plain HTTP clients), so the file is placed by hand: open the dataset page in a
    browser, download the file, and put it at `path`."""
    if not path.exists():
        raise SystemExit(f"missing {path}: download it from the Dryad dataset page "
                         "(plain HTTP downloads are refused) and rerun")
    return path

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5281_zenodo.8242026"
URL = "https://zenodo.org/api/records/8242026/files/Validity%20EQ-5D-3L.xlsx/content"
ITEMS = ["EQ1", "EQ2", "EQ3", "EQ4", "EQ5"]
COVS = {"age": "cov_age", "sex": "cov_sex", "education": "cov_education", "ARDS": "cov_ards",
        "charlson": "cov_charlson"}


def main() -> None:
    d = pd.read_excel(download(URL, RAW_DIR / "Validity EQ-5D-3L.xlsx"), "Variable table")
    assert d.shape == (225, 56)
    assert (d[ITEMS].sum(axis=1) == d["TOTAL_EQ-5D-3L"]).all()
    rest = [c for c in d.columns if c not in ITEMS and c not in COVS]
    lab = set(d.columns[list(d.columns).index("leukocyte_blood_count"):
                        list(d.columns).index("alk_phos") + 1])
    flags = {"hypertension", "Diabetes_mellitus", "AIDS_VIH", "Chronic_pulmonary_disease",
             "Renal_disease", "Any_malignancy", "Rheumatic_disease",
             "Congestive_heart_failure", "tracheostomy"}
    assert set(rest) == lab | flags | {"weight", "height", "TOTAL_EQ-5D-3L", "PCFS"}, rest
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    d["cov_charlson"] = d["cov_charlson"].astype("Int64")
    emit({"rodriguez_lima_2023_eq5d3l": (long(d, ITEMS, covs, valid=range(1, 4)),
                                         {i: {1, 2, 3} for i in ITEMS})})


if __name__ == "__main__":
    main()
