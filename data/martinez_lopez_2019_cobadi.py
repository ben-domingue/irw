#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/x4r7hpn4cz
# DOI: 10.17632/x4r7hpn4cz (dataset, 2019-04-24; Martinez-Lopez, Ruth). "Dataset of the type of the
#   Internet use and web 2.0 digital competence of students in a Russian University".
# Data: "Data Matrix_COBADI_Sp.xlsx", 205 students of a Russian university who completed the Russian
#       version of the COBADI (Competencia Basica Digital 2.0) questionnaire. q26.1-q26.13 (block 1),
#       q27.1-q27.12 (block 2), q28.1-q28.5 (block 3), q29.1-q29.4 (block 4) are the 34 COBADI
#       self-rated competence items on a 1-4 scale. q15-q25 (1/2 yes/no uses of the Internet) and the
#       free-text q4/q13/q14 are not shipped.
# License: CC BY 4.0 (Mendeley Data).
#
# Item text: not shipped -- the workbook has code headers only, no instrument file in the deposit
#   (Russian administration; the Spanish-origin COBADI wording is a hop away).
#
# Tables: martinez_lopez_2019_cobadi (34 items, 1-4; the four blocks are kept in one table, item codes
#   q26.1 ... q29.4 with the "_blokN" suffix of the first item of each block stripped); 205 ids (row
#   index). Covariates: cov_gender (q1: 1/2 as coded), cov_age (q2, years).
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
RAW_DIR = RAW_ROOT / "C_55_x4r7hpn4cz"
FNAME = "Data Matrix_COBADI_Sp.xlsx"


def main() -> None:
    d = pd.read_excel(mendeley_fetch("x4r7hpn4cz", FNAME, RAW_DIR))
    assert len(d) == 205
    d["id"] = d.index + 1
    d["cov_gender"] = d["q1"].astype("Int64")
    d["cov_age"] = d["q2"].astype("Int64")
    cols = [c for c in d.columns if c.startswith(("q26.", "q27.", "q28.", "q29."))]
    assert len(cols) == 34, cols
    ren = {c: c.split("_")[0] for c in cols}
    t = long(d, cols, ["cov_gender", "cov_age"], valid=range(1, 5), rename=ren)
    emit({"martinez_lopez_2019_cobadi": (t, pv_for(ren.values(), range(1, 5)))})


if __name__ == "__main__":
    main()
