#!/usr/bin/env python3
# Source: https://zenodo.org/records/17958610
# DOI: 10.5281/zenodo.17958610 (dataset, 2025; Zhang, Chuntong). Supplementary materials of "How
#   Critical Thinking Modulates the Impact of ChatGPT on Deep Learning: An Empirical Study from a
#   Cognitive Load Perspective"; the record names no paper DOI.
# Data: Dataset.xlsx sheet Dataset, 386 college students (all Validity == 1), 32 five-point agreement
#       items (1 strongly disagree .. 5 strongly agree): EU1-4/DU1-4 ChatGPT learning behaviour
#       (heuristic / dependent use), IL1-2/EL1-3/GL1-3 cognitive load (Leppink et al. 2013), CT1-4
#       critical thinking + IG1-3 intrinsic goal orientation + SE1-3 self-efficacy (all MSLQ,
#       Pintrich et al. 1993), DM1-3/DS1-3 deep motive / deep strategy (R-SPQ-2F, Biggs et al. 2001).
#       Supp_Mat_B_Codebook.docx documents every variable (code -> sub-construct -> keyword);
#       Supp_Mat_A_Survey.docx is the English instrument with the stems in codebook order.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped (stems from Supp_Mat_A_Survey.docx, tied to codes via the per-code keywords of
#   Supp_Mat_B_Codebook.docx; the five anchors from the codebook). Built by
#   automated_finding/itemtext_verification/make_itemtext_zhang_2025.py. The record's description
#   is Chinese and the sample is Chinese college students; the deposited instrument is English, so the
#   administered language is not established (left blank).
#
# Tables: zhang_2025_chatgpt_use (EU+DU, 8), zhang_2025_cognitive_load (IL+EL+GL, 8),
#   zhang_2025_mslq (CT+IG+SE, 10), zhang_2025_deep_learning (DM+DS, 6); all 1-5.
# Covariates: cov_gender (1 male, 2 female), cov_grade (1 freshman .. 5 postgraduate),
#   cov_major (1 humanities/social sciences, 2 STEM, 3 economics/management, 4 other),
#   cov_chatgpt_freq (1 almost never .. 5 > 5 hrs/week).
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

RAW_DIR = RAW_ROOT / "zen_17958610"
BLOCKS = {"zhang_2025_chatgpt_use": ["EU", "DU"], "zhang_2025_cognitive_load": ["IL", "EL", "GL"],
          "zhang_2025_mslq": ["CT", "IG", "SE"], "zhang_2025_deep_learning": ["DM", "DS"]}


def load() -> pd.DataFrame:
    d = pd.read_excel(zenodo_fetch(17958610, "Dataset.xlsx", RAW_DIR), sheet_name="Dataset")
    assert len(d) == 386 and d["ID"].is_unique and (d["Validity"] == 1).all()
    return d


def main() -> None:
    d = load()
    d["id"] = d["ID"].astype(int)
    d["cov_gender"] = d["Gender"]; d["cov_grade"] = d["Grade"]
    d["cov_major"] = d["Major"]; d["cov_chatgpt_freq"] = d["Freq"]
    covs = ["cov_gender", "cov_grade", "cov_major", "cov_chatgpt_freq"]
    items = [c for c in d.columns if re.fullmatch(r"[A-Z]{2}\d", c)]
    assert len(items) == 32
    out = {}
    for name, pre in BLOCKS.items():
        its = [c for c in items if c[:2] in pre]
        out[name] = (long(d, its, covs, valid=range(1, 6)), pv_for(its, range(1, 6)))
    assert sum(len(t[0]["item"].unique()) for t in out.values()) == 32
    emit(out)


if __name__ == "__main__":
    main()
