#!/usr/bin/env python3
# Source: https://zenodo.org/records/22375285
# DOI: 10.5281/zenodo.22375285 (dataset, 2026; Cordellieri, Giannini & Nori). "When the Mind Leaves
#   the Road: Development and Preliminary Psychometric Evaluation of the Scale of Cognitive and
#   Emotional Distraction in Driving (SCEDD)"; manuscript, no DOI on the record.
# Data: SCEDD_public_dataset_full.csv, 701 Italian secondary-school students aged 18-22 (the EFA and
#       CFA split files are subsets): SCEDD_1-29 initial item pool (1-5), RdS_1-8 BSSS-8 sensation
#       seeking (1-5), RPoDD_* nine distracted-driving risk-perception items (1-4), PR and Concerne
#       single 10-point crash-risk items (shipped as covariates). SCEDD_codebook.xlsx gives the Italian
#       wording per variable.
# License: CC BY 4.0 (Zenodo).
#
# Item text: shipped for all three (deposited codebook keyed by variable name, Italian administration;
#   scale anchors from the codebook's response-scale column where it names them, else blank). Built by
#   automated_finding/itemtext_verification/make_itemtext_cordellieri_2026.py.
#
# Tables: cordellieri_2026_scedd (701 x 29, 1-5), cordellieri_2026_bsss8 (701 x 8, 1-5),
#   cordellieri_2026_rpodd (701 x 9, 1-4).
# Covariates: cov_age (18-22), cov_gender (Femmina/Maschio), cov_sample (EFA/CFA),
#   cov_crash_risk_perception (1-10), cov_crash_concern (1-10).
# id: participant_id.
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

import re  # noqa: E402

RAW_DIR = RAW_ROOT / "zn_22375285"
FNAME = "SCEDD_public_dataset_full.csv"
CODEBOOK = "SCEDD_codebook.xlsx"


def codebook() -> pd.DataFrame:
    return pd.read_excel(zenodo_fetch(22375285, CODEBOOK, RAW_DIR), sheet_name="Codebook")


def main() -> None:
    d = pd.read_csv(zenodo_fetch(22375285, FNAME, RAW_DIR), encoding="utf-8-sig")
    assert len(d) == 701 and d["participant_id"].is_unique
    d["id"] = d["participant_id"].astype(int)
    d["cov_age"] = d["Età"].astype("Int64")
    d["cov_gender"] = d["Genere"]
    d["cov_sample"] = d["Sample"]
    d["cov_crash_risk_perception"] = d["PR"].astype("Int64")
    d["cov_crash_concern"] = d["Concerne"].astype("Int64")
    covs = ["cov_age", "cov_gender", "cov_sample", "cov_crash_risk_perception", "cov_crash_concern"]
    sc = [f"SCEDD_{i}" for i in range(1, 30)]
    rds = [f"RdS_{i}" for i in range(1, 9)]
    rp = [c for c in d.columns if re.fullmatch(r"RPoDD_\d+", c)]
    assert len(rp) == 9
    emit({"cordellieri_2026_scedd": (long(d, sc, covs, valid=range(1, 6)), pv_for(sc, range(1, 6))),
          "cordellieri_2026_bsss8": (long(d, rds, covs, valid=range(1, 6)), pv_for(rds, range(1, 6))),
          "cordellieri_2026_rpodd": (long(d, rp, covs, valid=range(1, 5)), pv_for(rp, range(1, 5)))})


if __name__ == "__main__":
    main()
