#!/usr/bin/env python3
# Source: https://frontiersin.figshare.com/articles/dataset/Table_1_Relationship_Between_Person-Organization_Fit_and_Teacher_Burnout_in_Kindergarten_The_Mediating_Role_of_Job_Satisfaction_XLS/20265216
# DOI: 10.3389/fpsyt.2022.948934.s001 (supplementary data of 10.3389/fpsyt.2022.948934)
#   Zang, L., & Chen, Y. (2022). Relationship between person-organization fit and teacher
#   burnout in kindergarten: the mediating role of job satisfaction. Frontiers in Psychiatry,
#   13, 948934.
# Data: Table_1 (.xls), 637 Chinese kindergarten teachers: A1-C9 person-organization fit (9
#       items, 1-5/1-6 as deposited), the 22 MBI-Educators items under the deposit's D/Q/F codes
#       (0-6), G1-K30 job satisfaction (30 items, 1-6). Codes are the deposit's column names.
# License: CC BY 4.0 (figshare record; Frontiers article CC BY 4.0).
#
# Item text: not shipped -- positional codes only, no labels in the .xls; the MBI is a `block`
#   row in itemtext/instrument_rights_register.csv in any case.
#
# Tables: zang_2022_po_fit (9), zang_2022_mbi_es (22, 0-6), zang_2022_job_satisfaction (30, 1-6).
# Covariates: cov_gender (1/2), cov_age (1-4), cov_teaching_years (1-5), cov_education (1-5),
#   cov_preschool_major (1 yes, 2 no), cov_establishment (有无编制, 1/2), cov_grade (1-4),
#   cov_title (1-4), cov_kindergarten_type (园所性质, 1/2), cov_location (园所地点, 1/2).
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

RAW_DIR = RAW_ROOT / "figshare_20265216"
FNAME = ("Table_1_Relationship Between Person-Organization Fit and Teacher Burnout in Kindergarten: "
         "The Mediating Role of Job Satisfaction.XLS")
COVS = {"性别": "cov_gender", "年龄": "cov_age", "教龄": "cov_teaching_years", "最高学历": "cov_education",
        "专业是否为学前教育": "cov_preschool_major", "有无编制": "cov_establishment", "任教年级": "cov_grade",
        "职称": "cov_title", "园所性质": "cov_kindergarten_type", "园所地点": "cov_location"}
PO = ["A1", "A2", "A3", "B4", "B5", "B6", "C7", "C8", "C9"]
MBI = ["D1", "D2", "D3", "D6", "D8", "D13", "D14", "D16", "D20", "Q5", "Q10", "Q11", "Q15", "Q22",
       "F4", "F7", "F9", "F12", "F17", "F18", "F19", "F21"]
JS = [f"{p}{i}" for p, rng in (("G", range(1, 8)), ("H", range(8, 14)), ("I", range(14, 18)),
                                  ("J", range(18, 24)), ("K", range(24, 31))) for i in rng]


def main() -> None:
    d = pd.read_excel(figshare_fetch(20265216, FNAME, RAW_DIR))
    assert len(d) == 637
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    emit({"zang_2022_po_fit": (long(d, PO, covs, valid=range(1, 7)), pv_for(PO, range(1, 7))),
          "zang_2022_mbi_es": (long(d, MBI, covs, valid=range(0, 7)), pv_for(MBI, range(0, 7))),
          "zang_2022_job_satisfaction": (long(d, JS, covs, valid=range(1, 7)), pv_for(JS, range(1, 7)))})


if __name__ == "__main__":
    main()
