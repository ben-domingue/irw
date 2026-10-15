#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_b_Determinants_affecting_teacher_burnout_and_performance_Asian_context_b_/31672783
# DOI: 10.6084/m9.figshare.31672783 (dataset, 2026; the record names no published paper)
#   Habibi, A. (2026). Determinants affecting teacher burnout and performance: Asian context.
#   figshare.
# Data: Raw data.xlsx, sheet "Raw": 1,070 Indonesian teachers (Google Forms, April 2025), one
#       column per item with the Indonesian stem as header; sheet "Coded" is the same survey
#       listwise-cleaned to 1,058 rows under codes TSC1-5, TSE1-5, EE1-5, DE1-3, RPA1-7, ANX1-3,
#       WOL1-4, PE1-4 (same column order). The Raw sheet ships (missing cells kept), with the
#       Coded sheet's codes as item names, checked column-by-column against Coded.
# License: CC BY 4.0 (figshare record).
#
# Item text: shipped for habibi_2026_teacher_self_concept, habibi_2026_teacher_self_efficacy,
#   habibi_2026_teaching_anxiety, habibi_2026_workload and habibi_2026_performance (Indonesian
#   stems = Raw headers with the leading number stripped; IRW English in item_text_translated;
#   no anchor text in the deposit, option_text blank). NOT shipped for habibi_2026_burnout: its
#   EE/DE/RPA items are an Indonesian rendering of MBI-Educators items, and the MBI is a `block`
#   row in itemtext/instrument_rights_register.csv (adaptations covered).
#   Built by automated_finding/itemtext_verification/make_itemtext_habibi_2026.py from stems().
#
# Tables (all 1-5): habibi_2026_teacher_self_concept (TSC, 5), habibi_2026_teacher_self_efficacy
#   (TSE, 5), habibi_2026_burnout (EE+DE+RPA, 15), habibi_2026_teaching_anxiety (ANX, 3),
#   habibi_2026_workload (WOL, 4), habibi_2026_performance (PE, 4).
# Covariates: cov_gender (1/2 as deposited), cov_experience (1 <=5 years, 2 >5 years),
#   cov_school_area (1 urban "Kota", 2 rural "Desa").
# id: row index of the Raw sheet (the timestamp column is not shipped).
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

RAW_DIR = RAW_ROOT / "figshare_31672783"
FNAME = "Raw data.xlsx"
CODES = ([f"TSC{i}" for i in range(1, 6)] + [f"TSE{i}" for i in range(1, 6)] + [f"EE{i}" for i in range(1, 6)]
         + [f"DE{i}" for i in range(1, 4)] + [f"RPA{i}" for i in range(1, 8)] + [f"ANX{i}" for i in range(1, 4)]
         + [f"WOL{i}" for i in range(1, 5)] + [f"PE{i}" for i in range(1, 5)])
BLOCKS = {"habibi_2026_teacher_self_concept": CODES[0:5], "habibi_2026_teacher_self_efficacy": CODES[5:10],
          "habibi_2026_burnout": CODES[10:25], "habibi_2026_teaching_anxiety": CODES[25:28],
          "habibi_2026_workload": CODES[28:32], "habibi_2026_performance": CODES[32:36]}
COVS = ["cov_gender", "cov_experience", "cov_school_area"]


def raw() -> pd.DataFrame:
    return pd.read_excel(figshare_fetch(31672783, FNAME, RAW_DIR), sheet_name="Raw")


def stems() -> list:
    """(code, Indonesian stem) pairs, header text with the leading item number stripped."""
    import re
    heads = list(raw().columns[4:])
    assert len(heads) == len(CODES)
    return [(c, re.sub(r"^\d+\.\s*", "", h).strip()) for c, h in zip(CODES, heads)]


def main() -> None:
    x = raw()
    coded = pd.read_excel(figshare_fetch(31672783, FNAME, RAW_DIR), sheet_name="Coded ")
    assert list(coded.columns[3:]) == CODES
    d = pd.DataFrame({"id": x.index + 1, "cov_gender": x["Jenis kelamin"],
                      "cov_experience": x["Pengalaman mengajar"].map({"<5 tahun  atau 5 tahun": 1, "> 5 tahun": 2}),
                      "cov_school_area": x["Area sekolah tempat mengajar"].map({"Kota": 1, "Desa": 2})})
    for c, h in zip(CODES, x.columns[4:]):
        d[c] = x[h]
    for c in COVS:
        d[c] = d[c].astype("Int64")
    assert len(coded) == 1058 and len(x) == 1070
    emit({t: (long(d, items, COVS, valid=range(1, 6)), pv_for(items, range(1, 6))) for t, items in BLOCKS.items()})


if __name__ == "__main__":
    main()
