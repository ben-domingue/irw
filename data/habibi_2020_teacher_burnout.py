#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/6jmv43nffk
# DOI: 10.17632/6jmv43nffk (dataset, 2020; Habibi, Akhmad). "Dataset for Factors Affecting Teachers'
#   Burnout: A SEM Analysis in an Asian Context"; no paper DOI on the record.
# Data: "2. Response.xlsx" (Google Forms export), 876 Indonesian teachers: TSC1-5 teacher self-concept,
#       TE1-5 teacher efficacy, EE1-5 emotional exhaustion, DE1-3 depersonalisation, RPA1-5 reduced
#       personal accomplishment, all 1-5. "1. Instrument in English and Indonesian.docx" is the
#       instrument (its RPA block lists 7 statements where the data carry 5 columns). No demographics
#       in the response sheet.
# License: CC BY 4.0 (Mendeley Data).
#
# Item text: shipped for tsc and te (instrument docx, Indonesian stems with the authors' English in
#   `_translated`, by block position = code number; anchors not printed in the docx -> option_text
#   blank). burnout: not shipped -- EE/DE/RPA are an MBI-ES adaptation (blocked in the rights register)
#   and the RPA block count does not match. Built by
#   automated_finding/itemtext_verification/make_itemtext_habibi_2020.py.
#
# Tables: habibi_2020_tsc (876 x 5), habibi_2020_te (876 x 5), habibi_2020_burnout (876 x 13: EE1-5,
#   DE1-3, RPA1-5); all 1-5.
# Covariates: none in the file.
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

RAW_DIR = RAW_ROOT / "md_6jmv43nffk"
FNAME = "2. Response.xlsx"
TSC = [f"TSC{i}" for i in range(1, 6)]
TE = [f"TE{i}" for i in range(1, 6)]
BURN = [f"EE{i}" for i in range(1, 6)] + [f"DE{i}" for i in range(1, 4)] + [f"RPA{i}" for i in range(1, 6)]


def main() -> None:
    d = pd.read_excel(mendeley_fetch("6jmv43nffk", FNAME, RAW_DIR))
    assert len(d) == 876 and list(d.columns) == TSC + TE + BURN
    d["id"] = d.index + 1
    emit({"habibi_2020_tsc": (long(d, TSC, [], valid=range(1, 6)), pv_for(TSC, range(1, 6))),
          "habibi_2020_te": (long(d, TE, [], valid=range(1, 6)), pv_for(TE, range(1, 6))),
          "habibi_2020_burnout": (long(d, BURN, [], valid=range(1, 6)), pv_for(BURN, range(1, 6)))})


if __name__ == "__main__":
    main()
