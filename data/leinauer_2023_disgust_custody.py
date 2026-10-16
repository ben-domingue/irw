#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Pathogenic_disgust_sensitivity_predicts_bias_against_gay_male_fathers_but_not_lesbian_mothers_in_child_custody_hearings/15157869
# DOI: 10.6084/m9.figshare.15157869 (dataset, 2023; Leinauer, Mark). Vignette experiment on MTurk,
#   "Pathogenic disgust sensitivity predicts bias against gay male fathers but not lesbian mothers in
#   child custody hearings"; no paper DOI on the record.
# Data: DisgustDataAfterRunningSyntax.dta, 381 MTurk adults. Background measures answered by all:
#       dsr1-27 Disgust Scale-Revised (0-4), grb1-10 Gender Role Beliefs Scale short form (1-7),
#       atg1-3 + atl1-3 Attitudes Toward Lesbians and Gay Men short form (1-7), mt1-4 NES Moral
#       Traditionalism (1-5). Shipped as answered (the *Rev copies, sums and quartiles are the authors'
#       scoring). The custody vignette DVs (condition-specific, n ~ 48 each), the word-fragment and
#       distraction tasks and the manipulation checks are not shipped. The .dta variable labels name
#       the instrument, not the item.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped -- variable labels are instrument names ("DS-R Disgust Sensitivity Scale
#   Revised"), not stems; no codebook deposited.
#
# Tables: leinauer_2023_dsr (27, 0-4), leinauer_2023_gender_role_beliefs (10, 1-7),
#   leinauer_2023_atlg (6, 1-7), leinauer_2023_moral_traditionalism (4, 1-5).
# Covariates: cov_vignette_homosexual (HScond 0/1), cov_vignette_father (0 mother, 1 father),
#   cov_vignette_son (0 daughter, 1 son). No demographics in the file.
# id: the file's id column.
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

RAW_DIR = RAW_ROOT / "fs_15157869"


def main() -> None:
    d = pd.read_stata(figshare_fetch(15157869, "DisgustDataAfterRunningSyntax.dta", RAW_DIR), convert_categoricals=False)
    assert len(d) == 381 and d["id"].is_unique
    d["id"] = d["id"].astype(int)
    d["cov_vignette_homosexual"] = d["HScond"].astype(int); d["cov_vignette_father"] = d["Fathercond"].astype(int)
    d["cov_vignette_son"] = d["SONcond"].astype(int)
    covs = ["cov_vignette_homosexual", "cov_vignette_father", "cov_vignette_son"]
    dsr = [f"dsr{i}" for i in range(1, 28)]; grb = [f"grb{i}" for i in range(1, 11)]
    atlg = [f"atg{i}" for i in range(1, 4)] + [f"atl{i}" for i in range(1, 4)]; mt = [f"mt{i}" for i in range(1, 5)]
    emit({"leinauer_2023_dsr": (long(d, dsr, covs, valid=range(0, 5)), pv_for(dsr, range(0, 5))),
          "leinauer_2023_gender_role_beliefs": (long(d, grb, covs, valid=range(1, 8)), pv_for(grb, range(1, 8))),
          "leinauer_2023_atlg": (long(d, atlg, covs, valid=range(1, 8)), pv_for(atlg, range(1, 8))),
          "leinauer_2023_moral_traditionalism": (long(d, mt, covs, valid=range(1, 6)), pv_for(mt, range(1, 6)))})


if __name__ == "__main__":
    main()
