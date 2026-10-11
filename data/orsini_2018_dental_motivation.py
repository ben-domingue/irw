#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/SHNVHF
# DOI: 10.7910/DVN/SHNVHF (dataset; the file name points to J Educ Eval Health Prof 15:11,
#   Orsini, Binnie & Tricio 2018, "Motivational profiles and their relationships with basic
#   psychological needs, academic performance, study strategies, self-esteem, and vitality
#   in dental students in Chile")
#   Orsini, Cesar A.; Binnie, Vivian I.; Tricio, Jorge A. (2018). Harvard Dataverse, V1.
# Data: "Jeehp_15_11_raw data.xlsx", Sheet1: 924 dental students (years 1-6, Universidad
#       San Sebastián, Chile, spring 2016), five Spanish-administered instruments with
#       positional headers: Academic Motivation Scale (28, 1-7), Basic Psychological Needs
#       (15, 1-5), Learning Strategy (10, 1-5), Vitality (6, 1-7), Self-esteem (10, 1-4;
#       the Rosenberg length and range).
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Headers are positional ("Motivation item 7"); no questionnaire
#   is deposited; the BPNS is in the CSDT library (a `block` row in the rights register).
#
# Tables (item = instrument code + the header's item number): orsini_2018_ams (ams_1-28),
#   orsini_2018_bpns (bpns_1-15), orsini_2018_learning_strategy (ls_1-10),
#   orsini_2018_vitality (vit_1-6), orsini_2018_self_esteem (se_1-10).
# Covariates: cov_year_of_study (1-6), cov_gender (0/1 as coded), cov_age.
# id: row index of the sheet.

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

RAW_DIR = RAW_ROOT / "10_7910_dvn_shnvhf"
BLOCKS = {"orsini_2018_ams": ("Motivation item", "ams", 28, range(1, 8)),
          "orsini_2018_bpns": ("Basic Psychological needs item", "bpns", 15, range(1, 6)),
          "orsini_2018_learning_strategy": ("Learning Strategy item", "ls", 10, range(1, 6)),
          "orsini_2018_vitality": ("Vitality item", "vit", 6, range(1, 8)),
          "orsini_2018_self_esteem": ("Self esteem item", "se", 10, range(1, 5))}


def main() -> None:
    d = pd.read_excel(dv_fetch("10.7910/DVN/SHNVHF", "Jeehp_15_11_raw data.xlsx", RAW_DIR), sheet_name="Sheet1")
    assert len(d) == 924
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns={"Year of study": "cov_year_of_study", "Gender": "cov_gender", "age": "cov_age"})
    d["cov_age"] = d["cov_age"].round().astype("Int64")
    covs = ["cov_year_of_study", "cov_gender", "cov_age"]
    out = {}
    for name, (head, pre, n, valid) in BLOCKS.items():
        rename = {f"{head} {k}": f"{pre}_{k}" for k in range(1, n + 1)}
        assert set(rename) <= set(d.columns), (name, set(rename) - set(d.columns))
        out[name] = (long(d, list(rename), covs, valid=valid, rename=rename), pv_for(rename.values(), valid))
    emit(out)


if __name__ == "__main__":
    main()
