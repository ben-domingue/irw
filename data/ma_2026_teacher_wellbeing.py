#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/KXNKRI
# DOI: 10.7910/DVN/KXNKRI (data, 2026; Ma, Sai). "Social-Emotional Competence and Teacher Well-Being in
#   Western China: Identity as a Mediating Mechanism and Urban-Rural Invariance"; no paper DOI given.
# Data: Raw_data.csv, 569 senior-high-school teachers in western China: PSEC1-5 (perceived
#       social-emotional competence), TPI1-13 (teacher professional identity), TOWB1-12 (occupational
#       well-being), all 1-7; ATT1-3 attention checks (all passed) not shipped. Codebook.docx gives the
#       English item wording; Questionnaire.pdf is the Chinese instrument as administered.
# License: CC0 1.0 (Harvard Dataverse).
#
# Item text: shipped for all three (Chinese stems from Questionnaire.pdf, numbered 1-30 in block order
#   = PSEC1-5, TPI1-13, TOWB1-12; English from Codebook.docx in `_translated`; anchors from the
#   codebook's 1-7 legend). Built by automated_finding/itemtext_verification/make_itemtext_ma_2026.py.
#
# Tables: ma_2026_psec (569 x 5), ma_2026_tpi (569 x 13), ma_2026_towb (569 x 12); 1-7.
# Covariates: cov_gender (1 male, 2 female), cov_teach_years (1 <=5, 2 6-10, 3 11-15, 4 >=16),
#   cov_school_location (1 urban, 2 rural), cov_school_type (1 public, 2 private), cov_title (1-5),
#   cov_head_teacher (1 yes, 2 no).
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

RAW_DIR = RAW_ROOT / "dv_KXNKRI"
FNAME = "Raw_data.csv"
BLOCKS = {"psec": [f"PSEC{i}" for i in range(1, 6)], "tpi": [f"TPI{i}" for i in range(1, 14)],
          "towb": [f"TOWB{i}" for i in range(1, 13)]}
COVS = {"Gender": "cov_gender", "TeachYears": "cov_teach_years", "SchoolLoc": "cov_school_location",
        "SchoolType": "cov_school_type", "Title": "cov_title", "HeadTeacher": "cov_head_teacher"}


def main() -> None:
    d = pd.read_csv(dv_fetch("10.7910/DVN/KXNKRI", FNAME, RAW_DIR), encoding="utf-8-sig")
    assert len(d) == 569 and (d["ATT1"] == 5).all() and (d["ATT2"] == 4).all() and (d["ATT3"] == 3).all()
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    emit({f"ma_2026_{k}": (long(d, v, covs, valid=range(1, 8)), pv_for(v, range(1, 8))) for k, v in BLOCKS.items()})


if __name__ == "__main__":
    main()
