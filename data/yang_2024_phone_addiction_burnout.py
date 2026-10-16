#!/usr/bin/env python3
# Source: https://frontiersin.figshare.com/articles/dataset/DataSheet_1_Mobile_phone_addiction_and_academic_burnout_the_mediating_role_of_technology_conflict_and_the_protective_role_of_mindfulness_xlsx/25332781
# DOI: 10.3389/fpsyt.2024.1365914.s001 (supplementary data, 2024; Yang, Guang-Hui; Cao, Xiao-Xuan; Fu, Yan-Yan;
#   Wang, Ning-Dan; Lian, Shuai-Lei). "Mobile phone addiction and academic burnout: the mediating role of
#   technology conflict and the protective role of mindfulness", Frontiers in Psychiatry 15:1365914
#   (10.3389/fpsyt.2024.1365914). 752 Chinese university students.
# Data: DataSheet_1_... .xlsx, one sheet (its Chinese name says missing values were completed and scale scores
#       computed). Four item blocks: v201-v217 (mobile phone addiction, 17 items, 1-5 -- the authors' mean
#       `phoneaddiction` reproduces from these), v701-v715 (mindfulness, 15 items, 1-4; the deposit's v7xxr
#       columns are 6 - v7xx, so the scale is 1-5 with 5 never endorsed -- shipped as answered), v1601-v1610
#       (academic burnout, 10 items, 1-4), v2101-v2106 (technology conflict, 6 items, 1-7). A 0 in any item column
#       is a missing code (v703r is blank wherever v703 is 0) and is dropped. Block-to-construct assignment
#       follows the composite names ZN (正念, mindfulness), XYJD (学业倦怠, academic burnout), JSCT (技术冲突,
#       technology conflict); the z-scored columns are not shipped.
# License: CC BY 4.0 (Frontiers / figshare).
#
# Item text: not shipped -- codes only; the Chinese instruments are not in the deposit.
#
# Tables: yang_2024_mobile_phone_addiction (17), yang_2024_mindfulness (15), yang_2024_academic_burnout (10),
#   yang_2024_technology_conflict (6).
# Covariates: cov_gender (1/2), cov_age, cov_grade (1-3), cov_years (years of phone use).
# id: the deposit's id column (1-752).
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

RAW_DIR = RAW_ROOT / "figshare_25332781"
FNAME = ("DataSheet_1_Mobile phone addiction and academic burnout: the mediating role of technology conflict and "
         "the protective role of mindfulness.xlsx")


def main() -> None:
    d = pd.read_excel(figshare_fetch(25332781, FNAME, RAW_DIR))
    assert len(d) == 752 and d["id"].is_unique
    d["id"] = d["id"].astype(int)
    for k, v in {"cov_gender": "Gender", "cov_age": "age", "cov_grade": "grade", "cov_years": "years"}.items():
        d[k] = d[v]
    covs = ["cov_gender", "cov_age", "cov_grade", "cov_years"]
    blk = {"v2": [c for c in d.columns if re.fullmatch(r"v2\d\d", c)], "v7": [c for c in d.columns if re.fullmatch(r"v7\d\d", c)],
           "v16": [c for c in d.columns if re.fullmatch(r"v16\d\d", c)], "v21": [c for c in d.columns if re.fullmatch(r"v21\d\d", c)]}
    assert {k: len(v) for k, v in blk.items()} == {"v2": 17, "v7": 15, "v16": 10, "v21": 6}
    assert (abs(d[blk["v2"]].mean(axis=1) - d["phoneaddiction"]) < 1e-6).all()
    zero_na = d["v703"].eq(0) & d["v703r"].isna()
    assert zero_na.sum() == d["v703"].eq(0).sum() > 0, "0 is the missing code"
    for cols in blk.values():
        d[cols] = d[cols].replace(0, float("nan"))
    tabs = {}
    for name, key, valid in (("yang_2024_mobile_phone_addiction", "v2", range(1, 6)), ("yang_2024_mindfulness", "v7", range(1, 6)),
                             ("yang_2024_academic_burnout", "v16", range(1, 5)), ("yang_2024_technology_conflict", "v21", range(1, 8))):
        tabs[name] = (long(d, blk[key], covs, valid=valid), pv_for(blk[key], valid))
    emit(tabs)


if __name__ == "__main__":
    main()
