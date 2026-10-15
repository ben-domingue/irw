#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/bdzjtff5bh
# DOI: 10.17632/bdzjtff5bh (dataset, 2022; the record names no published paper)
#   Prasetiyo, W. H. (2022). Dataset for Measuring Adversity Quotient, Digital Competence,
#   Attitude Computer Technology and Self-Efficacy. Mendeley Data, V1.
# Data: Dataset_... .xlsx, 901 Indonesian teachers from 28 provinces (Google Forms survey);
#       header row 2 carries the item codes: AQ (C1-3, Ow1-2, R1-3, E1-3), ACT (A1-8, Up1-5,
#       Un1-6), SCT (Wr1-10, Em1-8, Cr1-4), TPACK1-5; all 1-5 agreement. Trailing legend rows
#       (gender / age codes) are dropped. The deposited .docx is the English questionnaire,
#       Part A-D in the same order.
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: shipped from the deposited questionnaire (English; Part A-D stems in column order,
#   anchors 1 Strongly Disagree .. 5 Strongly Agree). The administration language is not
#   stated (Indonesian teachers, English questionnaire deposited) -- `language` left blank,
#   as for li_2026/yang_2026 in the 2026-10-11 batch. Built by
#   automated_finding/itemtext_verification/make_itemtext_prasetiyo_2022.py.
#
# Tables: prasetiyo_2022_aq (11), prasetiyo_2022_act (19), prasetiyo_2022_sct (22),
#   prasetiyo_2022_tpack (5); all 1-5.
# Covariates: cov_grade_level (1 kindergarten, 2 elementary, 3 junior high, 4 senior high),
#   cov_gender (1 male, 2 female), cov_age (1 20-30, 2 31-40, 3 41-50, 4 >50).
# id: No. Resp, the deposit's respondent number.
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

RAW_DIR = RAW_ROOT / "10_17632_bdzjtff5bh"
FNAME = ("Dataset_Adversity Quotient, Adversity Quotient, Digital Competence, Attitude Computer Technology "
         "and Self-Efficacy.xlsx")
BLOCKS = {"prasetiyo_2022_aq": ["C1", "C2", "C3", "Ow1", "Ow2", "R1", "R2", "R3", "E1", "E2", "E3"],
          "prasetiyo_2022_act": [f"A{i}" for i in range(1, 9)] + [f"Up{i}" for i in range(1, 6)]
                                + [f"Un{i}" for i in range(1, 7)],
          "prasetiyo_2022_sct": [f"Wr{i}" for i in range(1, 11)] + [f"Em{i}" for i in range(1, 9)]
                                + [f"Cr{i}" for i in range(1, 5)],
          "prasetiyo_2022_tpack": [f"TPACK{i}" for i in range(1, 6)]}
COVS = ["cov_grade_level", "cov_gender", "cov_age"]


def load() -> pd.DataFrame:
    x = pd.read_excel(mendeley_fetch("bdzjtff5bh", FNAME, RAW_DIR), header=None)
    cols = ["id", *COVS] + list(x.iloc[1, 4:])
    d = x.iloc[2:].copy()
    d.columns = cols
    d = d[d["id"].notna()].reset_index(drop=True)
    assert len(d) == 901 and d["id"].is_unique
    return d


def main() -> None:
    d = load()
    d["id"] = d["id"].astype(int)
    for c in COVS:
        d[c] = pd.to_numeric(d[c]).astype("Int64")
    emit({t: (long(d, items, COVS, valid=range(1, 6)), pv_for(items, range(1, 6))) for t, items in BLOCKS.items()})


if __name__ == "__main__":
    main()
