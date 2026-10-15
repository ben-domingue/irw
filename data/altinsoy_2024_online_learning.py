#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/h8s8vxz3fb
# DOI: 10.17632/h8s8vxz3fb (dataset, 2024; the record names no published paper)
#   Altınsoy, E., & Boyraz, S. (2024). The mediating role of engagement in online learning
#   between online learning readiness and online learning satisfaction. Mendeley Data, V1.
# Data: 946.sav, 945 Turkish university students in a compulsory online foreign-language
#       course; three Turkish scales, 1-5: ÇÖH1-18 online learning readiness (çevrimiçi öğrenme
#       hazırbulunuşluğu; subscale sums COHBIL/OZG/OGK/OM/OZY), ÇÖB1-19 online learning
#       engagement (bağlılık; COBDAV/DUY/BIL), ÇDM1-10 online course satisfaction (ders
#       memnuniyeti). The TOTAL columns are the authors' sums; the single "Memnuniyet" item
#       does not ship.
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: not shipped -- the .sav variable labels repeat the code ("ÇDM1") and no item carries
#   value labels (both levels checked); the Turkish wording is not in the deposit.
#
# Tables: altinsoy_2024_ol_readiness (18), altinsoy_2024_ol_engagement (19),
#   altinsoy_2024_ol_satisfaction (10), all 1-5.
# Covariates: cov_gender (1 female "Kız", 2 male), cov_age (1 18, 2 19, 3 20, 4 21, 5 22+),
#   cov_school (1 faculty, 2 vocational school MYO).
# id: row index (no respondent identifier in the file).
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

RAW_DIR = RAW_ROOT / "10_17632_h8s8vxz3fb"
FNAME = "946.sav"
COVS = {"Cinsiyet": "cov_gender", "Yasiniz": "cov_age", "Okulunuz": "cov_school"}
BLOCKS = {"altinsoy_2024_ol_readiness": [f"ÇÖH{i}" for i in range(1, 19)],
          "altinsoy_2024_ol_engagement": [f"ÇÖB{i}" for i in range(1, 20)],
          "altinsoy_2024_ol_satisfaction": [f"ÇDM{i}" for i in range(1, 11)]}


def main() -> None:
    d, meta = pyreadstat.read_sav(str(mendeley_fetch("h8s8vxz3fb", FNAME, RAW_DIR)))
    assert len(d) == 945
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    emit({t: (long(d, items, covs, valid=range(1, 6)), pv_for(items, range(1, 6))) for t, items in BLOCKS.items()})


if __name__ == "__main__":
    main()
