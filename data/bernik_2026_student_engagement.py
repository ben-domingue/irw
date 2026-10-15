#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/33307392
# DOI: 10.6084/m9.figshare.33307392.v1 (dataset, 2026-08-21; Bernik, Nejc; Znidarsic, Jasmina; Sprajc,
#   Polona; Bernik, Mojca). "Excel file containing data from 269 undergraduate and postgraduate students
#   enrolled at Slovenian public universities ...".
# Data: "data_excel_repository.xlsx", 269 students: Q4a-Q4i (9 items, 1-6) information and data literacy
#       (IDL), Q5a-Q5l (12, 1-5) academic self-efficacy (ASE), Q6a-Q6c (3, 1-5) classroom engagement
#       (CE), Q7a-Q7i (9, 1-5) study engagement (SE) -- the four measures the deposit description lists,
#       in that order. No labels, no instrument file.
# License: CC BY 4.0 (figshare).
#
# Item text: not shipped -- code headers only (Q4a ...), both label levels absent, no instrument in the
#   deposit; the 9-item study engagement block is most likely the UWES-S-9 (rights-register block).
#
# Tables: bernik_2026_idl (9, 1-6), bernik_2026_ase (12, 1-5), bernik_2026_classroom_engagement (3, 1-5),
#   bernik_2026_study_engagement (9, 1-5); 269 ids (row index). Covariates: cov_gender (Q1_Sex, 1/2 as
#   coded), cov_age (years), cov_study_level (Q3_Study, 1/3 as coded).
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


def dans_fetch(doi: str, fname: str, raw_dir: Path) -> Path:
    """Download one original-format file of a DANS Data Station (Dataverse) dataset."""
    return dv_fetch(doi, fname, raw_dir, host="ssh.datastations.nl")
RAW_DIR = RAW_ROOT / "C_60_33307392"
FNAME = "data_excel_repository.xlsx"
BLOCKS = {"idl": ([f"Q4{c}" for c in "abcdefghi"], range(1, 7)),
          "ase": ([f"Q5{c}" for c in "abcdefghijkl"], range(1, 6)),
          "classroom_engagement": ([f"Q6{c}" for c in "abc"], range(1, 6)),
          "study_engagement": ([f"Q7{c}" for c in "abcdefghi"], range(1, 6))}


def main() -> None:
    d = pd.read_excel(figshare_fetch(33307392, FNAME, RAW_DIR))
    assert len(d) == 269
    d["id"] = d.index + 1
    d["cov_gender"] = d["Q1_Sex"].astype("Int64")
    d["cov_age"] = d["Q2_Age"].astype("Int64")
    d["cov_study_level"] = d["Q3_Study"].astype("Int64")
    covs = ["cov_gender", "cov_age", "cov_study_level"]
    out = {}
    for k, (cols, valid) in BLOCKS.items():
        out[f"bernik_2026_{k}"] = (long(d, cols, covs, valid=valid), pv_for(cols, valid))
    emit(out)


if __name__ == "__main__":
    main()
