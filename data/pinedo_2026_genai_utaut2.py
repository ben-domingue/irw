#!/usr/bin/env python3
# Source: https://zenodo.org/records/20400330
# DOI: 10.5281/zenodo.20400330 (dataset; the record names no published paper)
#   Pinedo, L. (2026). Survey on the Use of Generative Artificial Intelligence Tools Among
#   Marketing Undergraduates. Zenodo.
# Data: Database.xlsx, sheet "Data": 310 marketing undergraduates at two universities (Peru,
#       Costa Rica), 2025 academic year; 57 five-point agreement items in nine UTAUT2 blocks
#       (PE 7, EE 7, SI 7, HM 7, PV 5, FC 7, HT 5, BU 6, UT 6). Sheet "Legend" gives the
#       answer anchors and the covariate codes.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped -- the Legend sheet gives only the five anchors (Strongly disagree ..
#   Strongly agree) and the block codes; no stems exist in the deposit, and option labels
#   alone are not shipped.
#
# Tables: pinedo_2026_genai_utaut2 (310 x 57, 1-5; the nine constructs of one UTAUT2
#   questionnaire shipped as one table).
# Covariates: cov_age, cov_gender (Female/Male), cov_university (Universidad Latina de Costa
#   Rica / Universidad Privada Norbert Wiener, decoded from the Legend).
# id: the deposit's Q number (Q1 ... Q310).
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


RAW_DIR = RAW_ROOT / "zenodo_20400330"
BLOCKS = {"PE": 7, "EE": 7, "SI": 7, "HM": 7, "PV": 5, "FC": 7, "HT": 5, "BU": 6, "UT": 6}
ITEMS = [f"{b}{i}" for b, n in BLOCKS.items() for i in range(1, n + 1)]


def main() -> None:
    d = pd.read_excel(zenodo_fetch(20400330, "Database.xlsx", RAW_DIR), sheet_name="Data")
    assert len(d) == 310 and d["Q"].is_unique and set(ITEMS) <= set(d.columns)
    d["id"] = d["Q"].str[1:].astype(int)
    d["cov_age"] = d["AG"].astype(int)
    d["cov_gender"] = d["GE"].map({1: "Female", 2: "Male"})
    d["cov_university"] = d["UN"].map({1: "Universidad Latina de Costa Rica", 2: "Universidad Privada Norbert Wiener"})
    assert d[["cov_gender", "cov_university"]].notna().all().all()
    covs = ["cov_age", "cov_gender", "cov_university"]
    emit({"pinedo_2026_genai_utaut2": (long(d, ITEMS, covs, valid=range(1, 6)), pv_for(ITEMS, range(1, 6)))})


if __name__ == "__main__":
    main()
