#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/9b26sb2k4g
# DOI: 10.17632/9b26sb2k4g (dataset; the record names no published paper)
#   Ginting, W. O., Nasution, M. A., Lumbanraja, V., & Trimurni, F. (2026). Dataset on Digital
#   Competence, AI Literacy, Generative AI Use, Organizational Support, Public Service
#   Motivation, and Work Performance among Indonesian Civil Servants. Mendeley Data, V1.
# Data: FINAL_DATASET_ASN_DIGITAL_AI_PSM_N1000.xlsx, sheet RAW_SOURCE (item columns identical
#       to CLEAN_DATASET, checked): 1,000 Indonesian civil servants (Google Forms, Mar-Jun 2026,
#       purposive/snowball), 45 five-point items in five blocks: Digital Competence (DC 6), AI
#       Literacy (AIL 10), Perceived Organizational Support (POS 6), Public Service Motivation
#       (PSM 12), Work Performance (WP 11). The ids are labelled SYN0001-SYN1000; the README
#       sheet states in capitals that the file is actual empirical data, "not synthetic,
#       simulated, reconstructed, or calibrated", and the respondent profile and item
#       missingness look like survey data. The GAI1-7 use indicators (branching, categorical)
#       and the construct/subscale mean scores are not shipped.
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: not shipped -- the CODEBOOK sheet labels each item positionally ("Digital
#   Competence item 1"); no stems and no anchors in the deposit (xlsx, no value labels).
#
# Tables: ginting_2026_digital_competence (1,000 x 6), ginting_2026_ai_literacy (1,000 x 10),
#   ginting_2026_org_support (1,000 x 6), ginting_2026_psm (1,000 x 12),
#   ginting_2026_work_performance (1,000 x 11); all 1-5.
# Covariates (Indonesian category labels as deposited): cov_age_group, cov_gender,
#   cov_education, cov_tenure, cov_institution_type, cov_job_type, cov_province.
# id: the numeric part of the deposit's ID (SYN0001 -> 1).
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


RAW_DIR = RAW_ROOT / "mendeley_9b26sb2k4g"
FNAME = "FINAL_DATASET_ASN_DIGITAL_AI_PSM_N1000.xlsx"
COVS = {"AGE": "cov_age_group", "GENDER": "cov_gender", "EDUC": "cov_education", "TENURE": "cov_tenure",
        "INST_TYPE": "cov_institution_type", "JOB_TYPE": "cov_job_type", "PROVINCE": "cov_province"}
BLOCKS = {"ginting_2026_digital_competence": ("DC", 6), "ginting_2026_ai_literacy": ("AIL", 10),
          "ginting_2026_org_support": ("POS", 6), "ginting_2026_psm": ("PSM", 12),
          "ginting_2026_work_performance": ("WP", 11)}


def main() -> None:
    p = mendeley_fetch("9b26sb2k4g", FNAME, RAW_DIR)
    d = pd.read_excel(p, sheet_name="RAW_SOURCE")
    c = pd.read_excel(p, sheet_name="CLEAN_DATASET")
    assert len(d) == 1000 and d["ID"].is_unique and (d["DATA_STATUS"] == "ACTUAL_MAIN_DATASET").all()
    d["id"] = d["ID"].str[3:].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    tables = {}
    for name, (block, n) in BLOCKS.items():
        items = [f"{block}{i}" for i in range(1, n + 1)]
        assert d[items].fillna(-1).equals(c[items].fillna(-1)), block
        tables[name] = (long(d, items, covs, valid=range(1, 6)), pv_for(items, range(1, 6)))
    emit(tables)


if __name__ == "__main__":
    main()
