#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Work_intensification_and_burnout_in_secondary_teachers/6114659
# DOI: 10.6084/m9.figshare.6114659 (dataset, 2018; Loi, Lawrence & Gudex). The record names no paper DOI.
# Data: "Lawrence, Loi, & Gudex.sav", 215 Australian (NSW) secondary teachers, Qualtrics export with
#       full question text as variable labels: Q40_1-24 "degree to which the following elements of your
#       workload have increased" over the 24 Norwegian Teacher Self-Efficacy Scale task statements
#       (1-6, labels at 1 Not at all / 2 Slightly / 4 Moderately / 6 ..., unlabeled between), Q41_1-24
#       NTSES self-efficacy (1-7, labels at odd points), Q32_1-16 perceived organisational support
#       ("the organisation" = the school; 1-7), Q33_1-5 exchange ideology (1-7), Q34_1-22 MBI-ES
#       frequency (1 Never .. 7 Every day as deposited), Q39_1-4 workload satisfaction (not shipped,
#       4 items).
# License: CC BY 4.0 (figshare record).
#
# Item text: shipped for workload_increase, teacher_self_efficacy, pos and exchange_ideology (variable
#   label = block prompt + "-" + stem; value labels = anchors, "." = unlabeled point -> blank). mbi_es:
#   not shipped (MBI blocked in the rights register). Built by
#   automated_finding/itemtext_verification/make_itemtext_loi_2018.py.
#
# Tables: loi_2018_workload_increase (215 x 24, 1-6), loi_2018_teacher_self_efficacy (215 x 24, 1-7),
#   loi_2018_pos (215 x 16, 1-7), loi_2018_exchange_ideology (215 x 5, 1-7), loi_2018_mbi_es
#   (215 x 22, 1-7).
# Covariates: cov_gender (1 female, 2 male, 4 prefer not to say), cov_birth_year (2001 - Q9 code),
#   cov_years_teaching (Q11_1), cov_kla (Q16, 1-8), cov_currently_teaching (Q10 1 yes 2 no),
#   cov_employment (Q14 1-3), cov_management (Q49 1 yes 2 no), cov_employer (Q15 1-4).
# id: ID column.
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

import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "fs_6114659"
FNAME = "Lawrence, Loi, & Gudex.sav"
BLOCKS = {"workload_increase": ([f"Q40_{i}" for i in range(1, 25)], range(1, 7)),
          "teacher_self_efficacy": ([f"Q41_{i}" for i in range(1, 25)], range(1, 8)),
          "pos": ([f"Q32_{i}" for i in range(1, 17)], range(1, 8)),
          "exchange_ideology": ([f"Q33_{i}" for i in range(1, 6)], range(1, 8)),
          "mbi_es": ([f"Q34_{i}" for i in range(1, 23)], range(1, 8))}
COVS = {"Q7": "cov_gender", "Q11_1": "cov_years_teaching", "Q16": "cov_kla", "Q10": "cov_currently_teaching",
        "Q14": "cov_employment", "Q49": "cov_management", "Q15": "cov_employer"}


def labels():
    _, meta = pyreadstat.read_sav(str(figshare_fetch(6114659, FNAME, RAW_DIR)), metadataonly=True)
    return meta.column_names_to_labels, meta.variable_value_labels


def main() -> None:
    d, meta = pyreadstat.read_sav(str(figshare_fetch(6114659, FNAME, RAW_DIR)))
    assert len(d) == 215 and d["ID"].is_unique
    d["id"] = d["ID"].astype(int)
    d = d.rename(columns=COVS)
    d["cov_birth_year"] = (2001 - d["Q9"]).astype("Int64")
    covs = list(COVS.values()) + ["cov_birth_year"]
    for c in COVS.values():
        d[c] = d[c].astype("Int64")
    emit({f"loi_2018_{k}": (long(d, cols, covs, valid=valid), pv_for(cols, valid)) for k, (cols, valid) in BLOCKS.items()})


if __name__ == "__main__":
    main()
