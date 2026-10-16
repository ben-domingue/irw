#!/usr/bin/env python3
# Source: https://frontiersin.figshare.com/articles/dataset/Table_1_Parenting_Style_and_Cyber-Aggression_in_Chinese_Youth_The_Role_of_Moral_Disengagement_and_Moral_Identity_XLSX/14058470
# DOI: 10.3389/fpsyg.2021.621878.s001 (supplementary data, 2021; Zhang, Yizhi; Chen, Cheng; Teng, Zhaojun; Guo,
#   Cheng). "Parenting Style and Cyber-Aggression in Chinese Youth: The Role of Moral Disengagement and Moral
#   Identity", Frontiers in Psychology 12:621878 (10.3389/fpsyg.2021.621878). 1,917 Chinese youths aged 14-35.
# Data: Table_1_... .XLSX, Sheet1 (Sheet2/3 empty). MR1-10 = moral identity (1-5), MD1-32 = moral disengagement
#       (1-5), CA1-15 = cyber-aggression (1-4), PS1-42 = parenting style (s-EMBU, 1-4; the paper scores
#       rejection / emotional warmth / over-protection). Column headers that only name the block ("moral
#       identity(MI)") and the authors' scale means are not shipped.
# License: CC BY 4.0 (Frontiers / figshare).
#
# Item text: not shipped -- codes only in the workbook; the Chinese instruments are not in the deposit (the
#   paper names them: Moral Identity Scale, Moral Disengagement Scale, a cyber-aggression scale, s-EMBU).
#
# Tables: zhang_2021_moral_identity (10), zhang_2021_moral_disengagement (32), zhang_2021_cyber_aggression (15),
#   zhang_2021_parenting_style (42).
# Covariates: cov_gender (1 male, 2 female), cov_age.
# id: the deposit's `number` column (1-1917).
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


def osf_fetch(node: str, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://api.osf.io/v2/nodes/{node}/files/osfstorage/", headers=UA, timeout=120).json()
        url = [f["links"]["download"] for f in j["data"] if f["attributes"]["name"] == fname][0]
        download(url, p)
    return p
import re

RAW_DIR = RAW_ROOT / "figshare_14058470"
FNAME = "Table_1_Parenting Style and Cyber-Aggression in Chinese Youth: The Role of Moral Disengagement and Moral Identity.XLSX"


def main() -> None:
    d = pd.read_excel(figshare_fetch(14058470, FNAME, RAW_DIR), sheet_name="Sheet1")
    assert len(d) == 1917 and d["number"].is_unique
    d["id"] = d["number"].astype(int)
    d["cov_gender"] = d["Sex(1=Male,2=Female)"]
    d["cov_age"] = d["age(years)"]
    covs = ["cov_gender", "cov_age"]
    blk = {p: [c for c in d.columns if re.fullmatch(rf"{p}\d+", c)] for p in ("MR", "MD", "CA", "PS")}
    assert {k: len(v) for k, v in blk.items()} == {"MR": 10, "MD": 32, "CA": 15, "PS": 42}
    r5, r4 = range(1, 6), range(1, 5)
    emit({"zhang_2021_moral_identity": (long(d, blk["MR"], covs, valid=r5), pv_for(blk["MR"], r5)),
          "zhang_2021_moral_disengagement": (long(d, blk["MD"], covs, valid=r5), pv_for(blk["MD"], r5)),
          "zhang_2021_cyber_aggression": (long(d, blk["CA"], covs, valid=r4), pv_for(blk["CA"], r4)),
          "zhang_2021_parenting_style": (long(d, blk["PS"], covs, valid=r4), pv_for(blk["PS"], r4))})


if __name__ == "__main__":
    main()
