#!/usr/bin/env python3
# Source: https://zenodo.org/records/14803512
# DOI: 10.5281/zenodo.14803512 (dataset, 2025; Bock, Franziska; Pfenninger, Stefan). Survey data for
#   Bock & Pfenninger-Lee (2025), "Rarely Pure and Never Simple: Exploring Perceptions of Truth and
#   Objectivity in Energy Modelling and Scenarios" (paper DOI not given on the record).
# Data: Survey-Data.csv, 166 energy-model builders and users (TU Delft Qualtrics, Nov 2023).
#       Q1_1-Q1_12 and Q2_1-Q2_6: 18 epistemic-belief statements answered as text
#       (Strongly disagree .. Strongly agree), recoded 1-5 here. Q3_A1-A6/Q3_B1-B2 (modeller vs
#       decision-maker), Q4_A1-A6/Q4_B1-B2 (same, modeller from another country) and Q5_A6/Q5_B1-B2
#       (modeller vs scenario-user): 19 responsibility / information-balance sliders 0 (modeller) ..
#       10 (decision-maker or scenario-user). Survey-Questionnaire.pdf reproduces every item with
#       its code; README.md documents the columns.
# License: CC BY-SA 4.0 (Zenodo record).
#
# Item text: shipped (stems, section prompts and anchors transcribed from Survey-Questionnaire.pdf,
#   whose item codes Q1_1 .. Q5_B2 are the data columns). Built by
#   automated_finding/itemtext_verification/make_itemtext_bock_2025.py. English administration.
#
# Tables: bock_2025_epistemic_beliefs (18, 1-5), bock_2025_responsibility (19, 0-10).
# Covariates: cov_age_group, cov_gender, cov_education, cov_modelling_experience, cov_organisation,
#   cov_country_current (ISO3), cov_education_field (text labels as deposited).
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

RAW_DIR = RAW_ROOT / "zen_14803512"
LIK = {"Strongly disagree": 1, "Somewhat disagree": 2, "Neither agree nor disagree": 3,
       "Somewhat agree": 4, "Strongly agree": 5}


def load() -> pd.DataFrame:
    d = pd.read_csv(zenodo_fetch(14803512, "Survey-Data.csv", RAW_DIR), encoding="utf-8-sig", sep=";")
    assert len(d) == 166 and d["ID"].is_unique
    return d


def main() -> None:
    d = load()
    d["id"] = d["ID"].astype(int)
    cov = {"cov_age_group": "Age", "cov_gender": "Gender", "cov_education": "Edu_Lvl",
           "cov_modelling_experience": "Mod_Exp", "cov_organisation": "Orga",
           "cov_country_current": "Loc_Cur", "cov_education_field": "Edu_Backg"}
    for k, v in cov.items():
        d[k] = d[v]
    covs = list(cov)
    lik = [c for c in d.columns if re.fullmatch(r"Q[12]_\d+", c)]
    sld = [c for c in d.columns if re.fullmatch(r"Q[345]_[AB]\d", c)]
    assert len(lik) == 18 and len(sld) == 19
    for c in lik:
        bad = set(d[c].dropna()) - set(LIK)
        assert not bad, (c, bad)
        d[c] = d[c].map(LIK)
    emit({"bock_2025_epistemic_beliefs": (long(d, lik, covs, valid=range(1, 6)), pv_for(lik, range(1, 6))),
          "bock_2025_responsibility": (long(d, sld, covs, valid=range(0, 11)), pv_for(sld, range(0, 11)))})


if __name__ == "__main__":
    main()
