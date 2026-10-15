#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/v8k4k2km69
# DOI: 10.17632/v8k4k2km69 (dataset, 2026; Prasetiyo). The record names no published paper.
# Data: "Dataset of Digital Competence in Indonesia Higher Education.xlsx" sheet RAW, 519 Indonesian
#       university lecturers; two header rows (block / code). ACT1-12 Attitude toward Computer
#       Technology and SCT1-25 Self-Efficacy with Computer Technology (Milbrath & Kinzie 2000; the
#       deposited instrument prints a 1-4 agreement scale, the data carry 1-4),
#       and 21 DigCompEdu CheckIn items PE1-4 DR1-3 TL1-4 AS1-3 EL1-3 FLDC1-4, each with five ordered
#       proficiency statements (1-5). The sheet's right-hand legend lists the DigCompEdu option texts.
#       "Research Instrument ... .docx" is the instrument.
# License: CC BY 4.0 (Mendeley Data).
#
# Item text: shipped for all three (instrument docx: ACT/SCT stems by printed item number = code
#   number, positional; DigCompEdu stems and per-item option statements by block order). Built by
#   automated_finding/itemtext_verification/make_itemtext_prasetiyo_2026.py.
#
# Tables: prasetiyo_2026_act (519 x 12, 1-4), prasetiyo_2026_sct (519 x 25, 1-4),
#   prasetiyo_2026_digcompedu (519 x 21, 1-5).
# Covariates: cov_gender (1 male, 2 female), cov_institution_type (1 public, 2 private),
#   cov_discipline (1-5 legend in sheet), cov_institutional_support (1-5), cov_teaching_mode (1-3),
#   cov_collaboration_freq (1-5), cov_collaboration_effect (1-5).
# id: "No. Respondent".
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

RAW_DIR = RAW_ROOT / "md_v8k4k2km69"
FNAME = "Dataset of Digital Competence in Indonesia Higher Education.xlsx"
ACT = [f"ACT{i}" for i in range(1, 13)]
SCT = [f"SCT{i}" for i in range(1, 26)]
DCE = [f"PE{i}" for i in range(1, 5)] + [f"DR{i}" for i in range(1, 4)] + [f"TL{i}" for i in range(1, 5)] + \
      [f"AS{i}" for i in range(1, 4)] + [f"EL{i}" for i in range(1, 4)] + [f"FLDC{i}" for i in range(1, 5)]
COVS = {1: "cov_gender", 2: "cov_institution_type", 3: "cov_discipline", 4: "cov_institutional_support",
        5: "cov_teaching_mode", 6: "cov_collaboration_freq", 8: "cov_collaboration_effect"}


def load() -> pd.DataFrame:
    x = pd.read_excel(mendeley_fetch("v8k4k2km69", FNAME, RAW_DIR), sheet_name="RAW", header=None)
    codes = [x.iat[2, j] if isinstance(x.iat[2, j], str) and x.iat[2, j] in DCE else x.iat[1, j] for j in range(69)]
    d = x.iloc[3:, :69].copy()
    d.columns = ["id", *codes[1:]]
    d = d[d["id"].notna()].reset_index(drop=True)
    d = d.rename(columns={codes[j]: v for j, v in COVS.items()})
    assert all(c in d.columns for c in ACT + SCT + DCE), set(ACT + SCT + DCE) - set(d.columns)
    return d


def main() -> None:
    d = load()
    assert len(d) == 519 and d["id"].is_unique
    d["id"] = d["id"].astype(int)
    covs = list(COVS.values())
    for c in covs:
        d[c] = pd.to_numeric(d[c], errors="coerce").astype("Int64")
    for c in ACT + SCT + DCE:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    emit({"prasetiyo_2026_act": (long(d, ACT, covs, valid=range(1, 5)), pv_for(ACT, range(1, 5))),
          "prasetiyo_2026_sct": (long(d, SCT, covs, valid=range(1, 5)), pv_for(SCT, range(1, 5))),
          "prasetiyo_2026_digcompedu": (long(d, DCE, covs, valid=range(1, 6)), pv_for(DCE, range(1, 6)))})


if __name__ == "__main__":
    main()
