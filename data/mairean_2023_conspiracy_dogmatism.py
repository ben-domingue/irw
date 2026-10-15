#!/usr/bin/env python3
# Source: https://zenodo.org/records/7946176
# DOI: 10.5281/zenodo.7946176 (dataset, 2023; Mairean, Cornelia). "It's All Just A Lie. I Know It!
#   COVID-19 Conspiracy Beliefs and COVID-19 Anxiety Versus the War in Ukraine: The Role of Dogmatism".
# Data: "BD Ucraina Conspiracy.sav", 196 Romanian young adults (18-30): dog1-23 dogmatism (1-5),
#       IU1-iu12 intolerance of uncertainty (1-5), CM1-cm5 conspiracy mentality (1-5), covid.anxiety1-5
#       and ucraina.anxiety1-5 (1-5 frequency anchors), C1-c6 COVID conspiracy beliefs and
#       consp.ucraina1-5 (0/1). Only the first item of each block carries a (block-name) label; the
#       sums, z-scores and interaction terms are the authors'.
# License: CC BY 4.0 (Zenodo).
#
# Item text: not shipped -- variable labels name the block only, value labels exist on the first
#   covid.anxiety item alone; no instrument in the deposit (Romanian administration).
#
# Tables: mairean_2023_dogmatism (23), mairean_2023_ius12 (12), mairean_2023_cmq (5),
#   mairean_2023_covid_anxiety (5), mairean_2023_ukraine_anxiety (5), mairean_2023_covid_conspiracy
#   (6, 0/1), mairean_2023_ukraine_conspiracy (5, 0/1); 196 ids. Item codes lower-cased from the mixed-case
#   source names (IU1 -> iu1, CM1 -> cm1, C1 -> c1).
# Covariates: cov_gender (0 male, 1 female), cov_age, cov_education (1-4).
# id: row index.
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

RAW_DIR = RAW_ROOT / "zn_7946176"
FNAME = "BD Ucraina Conspiracy.sav"
BLOCKS = {"dogmatism": ([f"dog{i}" for i in range(1, 24)], range(1, 6)),
          "ius12": (["IU1", "IU2", "IU3"] + [f"iu{i}" for i in range(4, 13)], range(1, 6)),
          "cmq": (["CM1"] + [f"cm{i}" for i in range(2, 6)], range(1, 6)),
          "covid_anxiety": ([f"covid.anxiety{i}" for i in range(1, 6)], range(1, 6)),
          "ukraine_anxiety": ([f"ucraina.anxiety{i}" for i in range(1, 6)], range(1, 6)),
          "covid_conspiracy": (["C1"] + [f"c{i}" for i in range(2, 7)], (0, 1)),
          "ukraine_conspiracy": ([f"consp.ucraina{i}" for i in range(1, 6)], (0, 1))}


def main() -> None:
    d, meta = pyreadstat.read_sav(str(zenodo_fetch(7946176, FNAME, RAW_DIR)))
    assert len(d) == 196
    d["id"] = d.index + 1
    d["cov_gender"] = d["gen"].astype("Int64")
    d["cov_age"] = d["varsta"].astype("Int64")
    d["cov_education"] = d["studii"].astype("Int64")
    covs = ["cov_gender", "cov_age", "cov_education"]
    out = {}
    for k, (cols, valid) in BLOCKS.items():
        ren = {c: c.lower() for c in cols}
        t = long(d, cols, covs, valid=valid, rename=ren)
        out[f"mairean_2023_{k}"] = (t, pv_for(ren.values(), valid))
    emit(out)


if __name__ == "__main__":
    main()
