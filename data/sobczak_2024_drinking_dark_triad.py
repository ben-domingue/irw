#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/735s7fvt99
# DOI: 10.17632/735s7fvt99 (dataset; the record names no published paper)
#   Sobczak, M., & Rogowska, A. M. (2024). How sex indirectly affects problematic alcohol
#   drinking through the Dark Triad of personality. Mendeley Data, V1.
# Data: Data Base.xlsx, sheet "Data base": 565 Polish university students (18-46, 79% women;
#       Google Forms survey) with the 10-item brief Michigan Alcoholism Screening Test (bMAST)
#       and the 12-item Dirty Dozen Dark Triad (DDDT, 1-5). The bMAST items are deposited
#       already weighted (0 or 2 for items 1, 2, 4-7, 10; 0 or 5 for items 3, 8, 9); they
#       ship as 0/1 endorsement, with the weighting documented here. The composite columns
#       (bMAST, bMAST_cut5, bMAST_ARP, DDDTM, DDDTN, DDDTP) are not shipped.
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: not shipped -- the deposit's "Description" sheet labels each column only
#   positionally ("The brief Michigan Alcoholism Screening Test (bMAST) item 1", "The Dirty
#   Dozen Dark Triad (DDDT) scale item 1"); there are no stems and no option labels in the
#   file, and the Polish administered wording is not in the deposit.
#
# Tables: sobczak_2024_bmast (565 x 10, 0/1), sobczak_2024_dddt (565 x 12, 1-5).
# Covariates: cov_sex (Female/Male), cov_age (years), cov_study_year (1-6), cov_study_type
#   (Full-time / "Partl-time" as deposited).
# id: the deposit's ID.
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

RAW_DIR = RAW_ROOT / "mendeley_735s7fvt99"
COVS = {"Sex": "cov_sex", "Age": "cov_age", "Study year": "cov_study_year", "Study type": "cov_study_type"}
BMAST = [f"bMAST_{i:02d}" for i in range(1, 11)]
DDDT = [f"DDDT_{i:02d}" for i in range(1, 13)]
BMAST_WEIGHT = {1: 2, 2: 2, 3: 5, 4: 2, 5: 2, 6: 2, 7: 2, 8: 5, 9: 5, 10: 2}


def main() -> None:
    d = pd.read_excel(mendeley_fetch("735s7fvt99", "Data Base.xlsx", RAW_DIR), sheet_name="Data base")
    assert len(d) == 565 and d["ID"].is_unique
    d["id"] = d["ID"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for i, c in enumerate(BMAST, 1):  # weighted 0/2 or 0/5 as deposited -> 0/1 endorsement
        assert set(d[c].unique()) <= {0, BMAST_WEIGHT[i]}, (c, d[c].unique())
        d[c] = (d[c] > 0).astype(int)
    emit({
        "sobczak_2024_bmast": (long(d, BMAST, covs, valid=(0, 1)), pv_for(BMAST, (0, 1))),
        "sobczak_2024_dddt": (long(d, DDDT, covs, valid=range(1, 6)), pv_for(DDDT, range(1, 6))),
    })


if __name__ == "__main__":
    main()
