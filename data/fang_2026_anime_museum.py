#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/LWQ2PF
# DOI: 10.7910/DVN/LWQ2PF (dataset; the record names no paper -- "Cultural Reproduction in
#   the Digital Intelligence Era: The Impact of SCAA Qualia Experience Design for Digital
#   Cultural Heritage on Behavioral Intention")
#   Fang, Wen-Ting (2026). Replication Data for: Cultural Reproduction in the Digital
#   Intelligence Era ... Harvard Dataverse, V1.
# Data: "processed versions.xlsx", sheet "Topics (Classified)": 312 users of a virtual
#       anime-themed heritage museum, 38 items on 1-7 with construct codes as headers
#       (IE immersive experience 4, INTER interaction 4, INTEL intelligence 4, AE
#       aesthetic experience 4, EN entertainment 4, KN knowledge 4, EA emotional
#       attachment 5, BI behavioural intention 5, SA self-achievement 4 -- expansions
#       from the Chinese stems). "raw versions.xlsx" holds the same 38 columns in the
#       same order for all 320 responses with the Chinese stems as headers; the processed
#       sheet drops 8 responses. Codes are taken from the processed sheet and stems from
#       the raw sheet by column position (both files list the 38 items in one order).
# License: CC0 1.0 (Dataverse record).
#
# Item text: shipped (the raw workbook's headers are the administered Chinese stems,
#   mapped to the processed sheet's codes by column position; IRW English translation).
#   Built by automated_finding/itemtext_verification/make_itemtext_fang_2026.py.
#
# One table: fang_2026_anime_museum, item = the processed sheet's code (IE1 .. SA4), resp
#   1-7; the nine 4-5 item constructs are the blocks of one questionnaire.
# Covariates: cov_gender, cov_age_group, cov_education, cov_major (integer codes as
#   deposited; "Encoded information.pdf" in the record documents them).
# id: row index of the processed sheet.

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

import re  # noqa: E402

RAW_DIR = RAW_ROOT / "10_7910_dvn_lwq2pf"


def main() -> None:
    d = pd.read_excel(dv_fetch("10.7910/DVN/LWQ2PF", "processed versions.xlsx", RAW_DIR),
                      sheet_name="Topics (Classified)")
    assert len(d) == 312
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns={"Gender": "cov_gender", "Age": "cov_age_group", "Education": "cov_education", "Major": "cov_major"})
    covs = ["cov_gender", "cov_age_group", "cov_education", "cov_major"]
    rename = {c: re.sub(r"\s*\(\d+\)\s*$", "", c) for c in d.columns if re.search(r"\(\d+\)\s*$", str(c))}
    assert len(rename) == 38 and [int(re.search(r"\((\d+)\)", c).group(1)) for c in rename] == list(range(1, 39))
    t = long(d, list(rename), covs, valid=range(1, 8), rename=rename)
    emit({"fang_2026_anime_museum": (t, pv_for(rename.values(), range(1, 8)))})


if __name__ == "__main__":
    main()
