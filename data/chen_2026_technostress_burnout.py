#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_b_Technostress_and_Digital_Textbook_Adoption_Among_Higher_Vocational_Teachers_The_Mediating_Roles_of_Work_Engagement_and_Burnout_With_the_Moderating_Role_of_Organizational_Support_b_/31968699
# DOI: 10.6084/m9.figshare.31968699 (dataset, 2026; the record names no published paper)
#   Chen, Jiuke (2026). Technostress and Digital Textbook Adoption Among Higher Vocational
#   Teachers: The Mediating Roles of Work Engagement and Burnout With the Moderating Role of
#   Organizational Support. figshare.
# Data: 341704130_800_800.sav, 800 Chinese higher-vocational teachers; five Likert blocks with
#       the Chinese stem in each variable label and 7-point anchors in the value labels:
#       technostress (Q8, 15 items), perceived organisational support (Q9, 8), work engagement
#       (Q10, 9, UWES-9 frequency anchors 从不..总是), burnout (Q11, 12, the four BAT-12 facets),
#       digital-textbook use intention (Q12, 3). UB1-4 (unlabelled) and the scale means are not
#       shipped.
# License: CC BY 4.0 (figshare record).
#
# Item text: shipped for chen_2026_technostress, chen_2026_pos and chen_2026_dt_intention (Chinese
#   stems = .sav variable labels with the "8、技术压力 —" block prefix stripped; anchors = value
#   labels; IRW English in *_translated). NOT shipped for chen_2026_uwes9 and chen_2026_bat12:
#   the UWES and the Burnout Assessment Tool are `block` rows in
#   itemtext/instrument_rights_register.csv (translations covered).
#   Built by automated_finding/itemtext_verification/make_itemtext_chen_2026.py from stems().
#
# Tables: chen_2026_technostress (15, 1-7), chen_2026_pos (8, 1-7), chen_2026_uwes9 (9, 1-7),
#   chen_2026_bat12 (12, 1-7), chen_2026_dt_intention (3, 1-7).
# Covariates: cov_gender (1 male, 2 female), cov_teaching_years (1 <2y .. 5 >8y), cov_school_type
#   (1 public double-high, 2 public other, 3 private), cov_title (1 assistant .. 4 professor),
#   cov_education (1 bachelor, 2 master, 3 doctor), cov_discipline (1-19), cov_region (1 east,
#   2 central, 3 west).
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

import re  # noqa: E402

import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "figshare_31968699"
FNAME = "341704130_800_800.sav"
COVS = {"Q1": "cov_gender", "Q2": "cov_teaching_years", "Q3": "cov_school_type", "Q4": "cov_title",
        "Q5": "cov_education", "Q6": "cov_discipline", "Q7": "cov_region"}
BLOCKS = {"chen_2026_technostress": [f"Q8_Row{i}" for i in range(1, 16)],
          "chen_2026_pos": [f"Q9_Row{i}" for i in range(1, 9)],
          "chen_2026_uwes9": [f"Q10_Row{i}" for i in range(1, 10)],
          "chen_2026_bat12": [f"Q11_Row{i}" for i in range(1, 13)],
          "chen_2026_dt_intention": [f"Q12_Row{i}" for i in range(1, 4)]}


def stems() -> dict:
    """table -> [(code, Chinese stem, {value: anchor})]; the block title prefix on item 1 is dropped."""
    _, meta = pyreadstat.read_sav(str(figshare_fetch(31968699, FNAME, RAW_DIR)), metadataonly=True)
    out = {}
    for t, items in BLOCKS.items():
        rows = []
        for c in items:
            lab = re.sub(r"^\d+、[^—]*—\s*", "", meta.column_names_to_labels[c]).strip()
            rows.append((c, lab, {int(k): v for k, v in meta.variable_value_labels[c].items()}))
        out[t] = rows
    return out


def main() -> None:
    d, meta = pyreadstat.read_sav(str(figshare_fetch(31968699, FNAME, RAW_DIR)))
    assert len(d) == 800
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    emit({t: (long(d, items, covs, valid=range(1, 8)), pv_for(items, range(1, 8))) for t, items in BLOCKS.items()})


if __name__ == "__main__":
    main()
