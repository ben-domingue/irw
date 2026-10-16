#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/DATA1_Longitudinal_changes_in_disgust_sensitivity_during_pregnancy_and_the_early_postpartum_period_and_the_role_of_recent_health_problems_xlsx/19354577
# DOI: 10.6084/m9.figshare.19354577 (dataset, 2022; Dlouhá, Daniela; Roberts, S. Craig; Ullmann, Jana; Nouzová,
#   Kamila; Kaňková, Šárka). Czech women followed through pregnancy: Disgust Scale-Revised in each trimester
#   (I, II, III) and 6 weeks postpartum (P). The sibling deposits 10.6084/m9.figshare.19354688 (v4 "DATA",
#   106 rows = the 106 women retained after exclusions here, identical DS-R vectors by ID) and
#   10.6084/m9.figshare.19354643 ("DATA2", long-format subscale scores only) are not shipped separately.
#   No overlap with the lab's other IRW tables (kankova_2023_*, dlouha_2023_*, kankova_2025_*, benesova_2026_*):
#   0 shared first-trimester DS-R vectors.
# Data: DATA1 ... .xlsx, sheet "Data" (119 rows) + "Key". <wave>.DS-R<k> = DS-R items (0-4; k = 1..27 without
#       the catch items 12 and 16; items 1, 6, 10 stored already reversed, suffix _R). Non-integer cells are
#       the lab's person-mean imputation of a missing answer and are dropped. Subscale/total scores not shipped.
# License: CC BY 4.0 (figshare).
#
# Item text: not shipped -- codes only (the Key sheet documents the covariates, not the items); Czech DS-R
#   wording is not in the deposit.
#
# Tables: dlouha_2022_pregnancy_dsr (25 items, wave 1-3 = trimester, 4 = 6 weeks postpartum).
# Covariates: cov_age, cov_height, cov_parity (0 primiparous / 1 multiparous), cov_education (1-4),
#   cov_residency (1-6 population bands), cov_income (1-7 bands), cov_smoking_now, cov_smoking_before (1-5),
#   cov_excluded (1 = excluded from the authors' analysis), cov_miscarriage (0/1), cov_fetus_sex (0 female,
#   1 male), cov_gest_age_weeks (per wave; blank postpartum), cov_recent_health_problems (per wave, 0/1).
# id: row index (the deposit's G-codes are not shipped).
import os
import sys
from pathlib import Path

import pandas as pd
import requests

import warnings

warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

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

def drop_frac(d: pd.DataFrame, cols: list, label: str) -> pd.DataFrame:
    """Blank non-integer cells (the lab's person-mean imputation of missing answers) and say how many."""
    v = d[cols].apply(pd.to_numeric, errors="coerce")
    frac = (v.notna() & (v % 1 != 0))
    n = int(frac.values.sum())
    if n:
        print(f"    [{label}] {n} fractional (imputed) cell(s) of {int(v.notna().values.sum())} dropped")
    d[cols] = v.mask(frac)
    return d


def stack_waves(d: pd.DataFrame, prefixes: dict, items: list, covs: list, valid, label: str,
                extra_cov_by_wave: dict | None = None) -> pd.DataFrame:
    """prefixes: wave number -> column prefix; items: bare item codes (prefix + code = source column).
    Returns long with a `wave` column; waves with no answers for a respondent drop out."""
    parts = []
    for w, pre in prefixes.items():
        cols = [pre + i for i in items]
        missing = [c for c in cols if c not in d.columns]
        assert not missing, (label, w, missing)
        sub = d[["id", *covs] + cols].copy()
        if extra_cov_by_wave:
            for k, v in extra_cov_by_wave.items():
                sub[k] = d[v[w]] if v.get(w) in d.columns else pd.NA
        sub = drop_frac(sub, cols, f"{label} wave {w}")
        sub = sub.rename(columns={pre + i: i for i in items})
        sub["wave"] = w
        ex = list(extra_cov_by_wave) if extra_cov_by_wave else []
        t = long(sub, items, covs + ex, valid=valid, extra=["wave"])
        parts.append(t)
    t = pd.concat(parts, ignore_index=True)
    return t.sort_values(["id", "wave", "item"]).reset_index(drop=True)

RAW_DIR = RAW_ROOT / "figshare_19354577"
FNAME = "DATA1_Longitudinal changes in disgust sensitivity during pregnancy and the early postpartum period, and the role of recent health problems.xlsx"
DSR = ["DS-R1_R", "DS-R2", "DS-R3", "DS-R4", "DS-R5", "DS-R6_R", "DS-R7", "DS-R8", "DS-R9", "DS-R10_R", "DS-R11", "DS-R13",
       "DS-R14", "DS-R15", "DS-R17", "DS-R18", "DS-R19", "DS-R20", "DS-R21", "DS-R22", "DS-R23", "DS-R24", "DS-R25", "DS-R26", "DS-R27"]


def main() -> None:
    d = pd.read_excel(figshare_fetch(19354577, FNAME, RAW_DIR), sheet_name="Data")
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == 119 and d["ID"].is_unique
    d["id"] = range(1, len(d) + 1)
    cov = {"cov_age": "age", "cov_height": "height", "cov_parity": "parity", "cov_education": "education",
           "cov_residency": "residency", "cov_income": "income", "cov_smoking_now": "smoking_now",
           "cov_smoking_before": "smoking_before", "cov_excluded": "excluded", "cov_miscarriage": "abort", "cov_fetus_sex": "fetus_sex"}
    for k, v in cov.items():
        d[k] = d[v]
    pre = {1: "I.", 2: "II.", 3: "III.", 4: "P."}
    t = stack_waves(d, pre, DSR, list(cov), range(0, 5), "dsr",
                    extra_cov_by_wave={"cov_gest_age_weeks": {1: "I.tr.gest_age_weeks", 2: "II.tr.gest_age_weeks", 3: "III.tr.gest_age_weeks"},
                                       "cov_recent_health_problems": {1: "I.tr.recent_health_problems", 2: "II.tr.recent_health_problems", 3: "III.tr.recent_health_problems"}})
    emit({"dlouha_2022_pregnancy_dsr": (t, pv_for(DSR, range(0, 5)))})


if __name__ == "__main__":
    main()
