#!/usr/bin/env python3
# Source: https://osf.io/ny7ew/
# DOI: none (OSF project ny7ew, 2025; Meule, Adrian; Kolar, David). "Effects of emetophobia symptoms,
#   disgust propensity, and disgust sensitivity on state disgust and behavioral avoidance of a
#   vomit-like stimulus" (preregistration, code and data).
# Data: opendata.csv, 126 German-speaking adults (students and others). spovi01-14 Specific Phobia of
#       Vomiting Inventory (0-4), qadpbrief01-10 brief Questionnaire for the Assessment of Disgust
#       Propensity (0-4), sads01-07 the disgust-sensitivity scale (0-4; sum "sads" in the file),
#       sds01-15_pre / _post a 15-item state disgust scale before and after the stimulus (0-4; shipped
#       with wave 1 = pre, 2 = post). Physiology, the behavioural approach task (bat) and sums are not
#       shipped. opencode.R documents which columns form each scale.
# License: CC BY 4.0 (OSF node licence).
#
# Item text: not shipped -- the CSV has codes only; the German item wording is not in the node (the
#   preregistration names the instruments).
#
# Tables: meule_2025_spovi (14), meule_2025_qadp_brief (10), meule_2025_disgust_sensitivity (7),
#   meule_2025_state_disgust (15 x 2 waves).
# Covariates: cov_age, cov_sex, cov_anxiety_disorder, cov_other_disorder, cov_occupation,
#   cov_nationality (German/other), cov_bmi.
# id: the file's id column.
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

RAW_DIR = RAW_ROOT / "osf_ny7ew"


def main() -> None:
    d = pd.read_csv(osf_fetch("ny7ew", "opendata.csv", RAW_DIR))
    assert len(d) == 126 and d["id"].is_unique
    cov = {"cov_age": "age", "cov_sex": "sex", "cov_anxiety_disorder": "anxiety_disorder",
           "cov_other_disorder": "other_disorder", "cov_occupation": "occupation",
           "cov_nationality": "nationality", "cov_bmi": "bmi"}
    for k, v in cov.items():
        d[k] = d[v]
    covs = list(cov)
    for pre in ("spovi", "qadpbrief", "sads", "sds"):
        cols = [c for c in d.columns if re.fullmatch(rf"{pre}\d+(_pre|_post)?", c)]
        print(pre, len(cols), "range", d[cols].min().min(), d[cols].max().max())
    spovi = [c for c in d.columns if re.fullmatch(r"spovi\d+", c)]
    qadp = [c for c in d.columns if re.fullmatch(r"qadpbrief\d+", c)]
    sads = [c for c in d.columns if re.fullmatch(r"sads\d+", c)]
    pre = [c for c in d.columns if re.fullmatch(r"sds\d+_pre", c)]
    post = [c for c in d.columns if re.fullmatch(r"sds\d+_post", c)]
    sds = pd.concat([d.rename(columns={c: c[:-4] for c in pre}).assign(wave=1),
                     d.rename(columns={c: c[:-5] for c in post}).assign(wave=2)], ignore_index=True)
    sds_items = [c[:-4] for c in pre]
    rng = range(0, 5)
    emit({"meule_2025_spovi": (long(d, spovi, covs, valid=rng), pv_for(spovi, rng)),
          "meule_2025_qadp_brief": (long(d, qadp, covs, valid=rng), pv_for(qadp, rng)),
          "meule_2025_disgust_sensitivity": (long(d, sads, covs, valid=rng), pv_for(sads, rng)),
          "meule_2025_state_disgust": (long(sds, sds_items, covs, valid=rng, extra=["wave"]), pv_for(sds_items, rng))})


if __name__ == "__main__":
    main()
