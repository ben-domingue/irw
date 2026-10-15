#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/8hz6bxdtnk
# DOI: 10.17632/8hz6bxdtnk (Mendeley Data, 2026; Zhao, Dayu). "Parental Burnout Network"; no linked
#   article.
# Data: "Network Analysis Data.xlsx", 1,062 employed Chinese parents (748 mothers, 314 fathers; May
#       2024). PBA01-PBA23 Parental Burnout Assessment (Roskam et al. 2018; 0-6 frequency), Pc01-07
#       psychological control, Bc01-05 behavioural control, Pv01-04 parental violence, Pn01-06
#       parental neglect, Pr01-04 parental rejection (all 1-5), WFC01-02 work-family and FWC01-02
#       family-work conflict (1-5). Construct names are the record's description read against the
#       column prefixes; no codebook in the deposit.
# License: CC BY 4.0 (Mendeley record).
#
# Item text: not shipped -- codes only in the workbook, no codebook or questionnaire deposited; the
#   Chinese wording is not available anywhere in the record.
#
# Tables: zhao_2026_pba (23, 0-6), zhao_2026_parental_control (Pc+Bc, 12, 1-5),
#   zhao_2026_parenting_practices (Pv+Pn+Pr, 14, 1-5), zhao_2026_work_family_conflict (WFC+FWC, 4,
#   1-5).
# Covariates: cov_gender (ParentGender as coded: 2 = 748 rows, 1 = 314 rows, which against the
#   description's 748 mothers / 314 fathers reads 2 = mother, 1 = father; undocumented), cov_age.
# id: the file's ID column.
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

RAW_DIR = RAW_ROOT / "mdl_8hz6bxdtnk"
BLOCKS = {"zhao_2026_pba": (r"PBA\d+", range(0, 7)), "zhao_2026_parental_control": (r"(Pc|Bc)\d+", range(1, 6)),
          "zhao_2026_parenting_practices": (r"(Pv|Pn|Pr)\d+", range(1, 6)),
          "zhao_2026_work_family_conflict": (r"(WFC|FWC)\d+", range(1, 6))}


def main() -> None:
    d = pd.read_excel(mendeley_fetch("8hz6bxdtnk", "Network Analysis Data.xlsx", RAW_DIR))
    assert len(d) == 1062 and d["ID"].is_unique
    print("ParentGender counts:", d["ParentGender"].value_counts().to_dict())
    d["id"] = d["ID"].astype(int)
    d["cov_gender"] = d["ParentGender"].astype(int); d["cov_age"] = d["ParentAge"].astype(int)
    out = {}
    for table, (pat, valid) in BLOCKS.items():
        its = [c for c in d.columns if re.fullmatch(pat, c)]
        out[table] = (long(d, its, ["cov_gender", "cov_age"], valid=valid), pv_for(its, valid))
    assert [len(set(t[0]["item"])) for t in out.values()] == [23, 12, 14, 4]
    emit(out)


if __name__ == "__main__":
    main()
