#!/usr/bin/env python3
# Source: https://zenodo.org/records/8404991
# DOI: 10.5281/zenodo.8404991 (dataset for the article of the same title; no article DOI on the record)
#   Zhao, Xiangge (2023). Triggering Chinese lecturers' intrinsic work motivation by
#   value-based leadership and growth mindset: Generation difference by using multigroup
#   analysis [Dataset]. Zenodo.
# Data: Dataset-518.csv: 518 Chinese university lecturers; four scales on 1-7: IWM intrinsic
#       work motivation (3), VBL value-based leadership (19), OSE organisational support
#       (8, the deposit's code), GM growth mindset (3); coded demographics.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. Headers are codes only and no questionnaire or codebook is
#   deposited; the article was not located.
#
# Tables (item = the deposit's column code): zhao_2023_iwm (3), zhao_2023_vbl (19),
#   zhao_2023_ose (8), zhao_2023_growth_mindset (3); all 1-7.
# Covariates (integer codes as deposited, undocumented): cov_identity, cov_gender, cov_age,
#   cov_marriage, cov_education, cov_teaching, cov_academic_rank, cov_discipline,
#   cov_university, cov_income.
# id: row index of the csv.

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

RAW_DIR = RAW_ROOT / "10_5281_zenodo_8404991"
COVS = {"Identity": "cov_identity", "Gender": "cov_gender", "Age": "cov_age", "Marriage": "cov_marriage",
        "Education": "cov_education", "Teaching": "cov_teaching", "Academicrank": "cov_academic_rank",
        "Discipline": "cov_discipline", "University": "cov_university", "Income": "cov_income"}
BLOCKS = {"zhao_2023_iwm": "IWM", "zhao_2023_vbl": "VBL", "zhao_2023_ose": "OSE", "zhao_2023_growth_mindset": "GM"}


def main() -> None:
    d = pd.read_csv(zenodo_fetch(8404991, "Dataset-518.csv", RAW_DIR))
    assert len(d) == 518
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    out = {}
    for name, pre in BLOCKS.items():
        items = [c for c in d.columns if c.startswith(pre) and c[len(pre):].isdigit()]
        out[name] = (long(d, items, covs, valid=range(1, 8)), pv_for(items, range(1, 8)))
    assert [len(out[n][1]) for n in BLOCKS] == [3, 19, 8, 3]
    emit(out)


if __name__ == "__main__":
    main()
