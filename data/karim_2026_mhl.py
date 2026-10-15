#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Mental_health_Literacy_Data/34001664
# DOI: 10.6084/m9.figshare.34001664 (dataset, 2026; the record names no published paper)
#   Karim, M. R. (2026). Mental health Literacy Data. figshare.
# Data: 7_MHL_Clean_S9.sav, 650 adult attendants of patients at a Bangladeshi hospital:
#       MHLq16-MHLq31, 16 agreement items of the Mental Health Literacy questionnaire (1-5,
#       strongly disagree .. strongly agree; knowledge, belief/stereotype, help-seeking and
#       self-help blocks). The MHL9xxREV reversed copies, the sums/averages and the cut-off
#       categories are the authors' scores. 8_S1_Questionnaire.pdf is the instrument.
#       Name and Address columns exist in the file but are entirely empty.
# License: CC BY 4.0 (figshare record).
#
# Item text: shipped (the .sav variable labels are the English stems and the value labels the
#   five anchors; English administration per the deposited questionnaire). Built by
#   automated_finding/itemtext_verification/make_itemtext_karim_2026.py from stems().
#
# Table: karim_2026_mhl (650 x 16, 1-5); item = the deposit's column name.
# Covariates: cov_age (years), cov_gender (0 male, 1 female), cov_marital_status (0-3),
#   cov_religion (0 Muslim, 1 Hindu, 2 Buddhist), cov_occupation (0-8, 99 missing),
#   cov_education (0-6, 99 missing), cov_residence (0 village, 1 urban, 2 suburban, 3 other),
#   cov_family_mental_illness (0 yes, 1 no, 2 don't know).
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

RAW_DIR = RAW_ROOT / "figshare_34001664"
FNAME = "7_MHL_Clean_S9.sav"
COVS = {"Age": "cov_age", "Sex": "cov_gender", "Mar_st": "cov_marital_status", "Religion": "cov_religion",
        "Occup": "cov_occupation", "Edu_quali": "cov_education", "Place_res": "cov_residence",
        "Fam_mi": "cov_family_mental_illness"}
ITEMS = [f"MHLq{i}" for i in range(16, 32)]


def stems() -> list:
    _, meta = pyreadstat.read_sav(str(figshare_fetch(34001664, FNAME, RAW_DIR)), metadataonly=True)
    return [(c, meta.column_names_to_labels[c].strip(), {int(k): v for k, v in meta.variable_value_labels[c].items()})
            for c in ITEMS]


def main() -> None:
    d, meta = pyreadstat.read_sav(str(figshare_fetch(34001664, FNAME, RAW_DIR)))
    assert len(d) == 650 and d["Name"].isna().all() and d["Address"].isna().all()
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d.loc[d[c] == 99, c] = pd.NA
        d[c] = d[c].astype("Int64")
    t = long(d, ITEMS, covs, valid=range(1, 6))
    emit({"karim_2026_mhl": (t, pv_for(ITEMS, range(1, 6)))})


if __name__ == "__main__":
    main()
