#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/y2929y272c
# DOI: 10.17632/y2929y272c (dataset, 2026; Li, Ke). "Reducing Listening Anxiety in Blended Learning:
#   The Role of AI-Driven Feedback and Strategy in EFL Education" (no paper DOI on the record).
# Data: RawData040825.csv, 436 Chinese vocational-college EFL students: LA_1-4 (listening achievement
#       scores 0-100, not shipped), then six 1-7 blocks BK_1-8, LTS_1-8, LCT_1-17, CS_1-6, MS_1-5,
#       PS_1-8 (codes only; the abstract names listening strategies and listening anxiety but the
#       deposit does not expand the block codes). LCT_14 carries six 8s (off-scale) -> set missing.
# License: CC BY 4.0 (Mendeley Data).
#
# Item text: not shipped -- codes only, no codebook in the deposit.
#
# Tables: li_2026_efl_listening_bk (8), _lts (8), _lct (17), _cs (6), _ms (5), _ps (8); 436 ids, 1-7.
#   Block meaning undocumented (data note).
# Covariates: cov_gender (1/2 as deposited), cov_age, cov_grade (1/4).
# id: "No." column.
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

RAW_DIR = RAW_ROOT / "md_y2929y272c"
FNAME = "RawData040825.csv"
BLOCKS = {"bk": [f"BK_{i}" for i in range(1, 9)], "lts": [f"LTS_{i}" for i in range(1, 9)],
          "lct": [f"LCT_{i}" for i in range(1, 18)], "cs": [f"CS_{i}" for i in range(1, 7)],
          "ms": [f"MS_{i}" for i in range(1, 6)], "ps": [f"PS_{i}" for i in range(1, 9)]}


def main() -> None:
    d = pd.read_csv(mendeley_fetch("y2929y272c", FNAME, RAW_DIR), encoding="utf-8-sig")
    d.columns = [c.strip() for c in d.columns]
    assert len(d) == 436 and d["No."].is_unique
    d["id"] = d["No."].astype(int)
    d["cov_gender"] = d["Gender"].astype("Int64")
    d["cov_age"] = d["Age"].astype("Int64")
    d["cov_grade"] = d["Grade"].astype("Int64")
    covs = ["cov_gender", "cov_age", "cov_grade"]
    bad = (d["LCT_14"] == 8).sum()
    assert bad == 6, bad
    d.loc[d["LCT_14"] == 8, "LCT_14"] = pd.NA
    emit({f"li_2026_efl_listening_{k}": (long(d, v, covs, valid=range(1, 8)), pv_for(v, range(1, 8)))
          for k, v in BLOCKS.items()})


if __name__ == "__main__":
    main()
