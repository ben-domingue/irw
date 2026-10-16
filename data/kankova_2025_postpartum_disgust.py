#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_b_The_impact_of_maternal_disgust_sensitivity_b_b_from_pregnancy_until_three_years_b_b_postpartum_b_b_on_the_early_development_of_disgust_sensitivity_in_the_child_b_/29590139
# DOI: 10.6084/m9.figshare.29590139 (dataset, 2025; Kaňková, Šárka). Czech mothers followed from the first
#   trimester (1T) to 6 weeks (6w), 1 year (1y) and 3 years (3y) postpartum: DS-R, TDDS, STAI-6, PSS-10, PANAS at
#   each wave, and at 3y the mother's report of the child's disgust (CDS, 14 items). Overlap with the lab's other
#   deposits: 120 of the 159 1T DS-R vectors match the first-trimester women of 10.6084/m9.figshare.20509353
#   (kankova_2023_*) and 37 match T1 of 10.6084/m9.figshare.25039721 (kankova_2025_trimester_*); the postpartum
#   waves are unique to this deposit. Shipped per deposit with a data note.
# Data: "Data_child disgust_figshare.xlsx", sheet "Data" (163 rows) + "Key". DS-R1_R..DS-R27 (0-4; 1, 6, 10
#       stored reversed; 12/16 = catch items, not shipped), tdds1-21 (0-6), stai1_R..stai6 (1-4), pss1..pss10
#       (0-4; 4, 5, 7, 8 stored reversed), panas1p..panas20n (1-5; p/n suffix = positive/negative affect),
#       3y_cds1..cds14 (0-2; 3, 4, 11, 12, 14 stored reversed). The Key says a person-mean was written in when up
#       to a fifth of a scale's answers were missing -- those non-integer cells are dropped. Scores not shipped.
# License: CC BY 4.0 (figshare).
#
# Item text: not shipped -- codes only; Czech wording not in the deposit.
#
# Tables: kankova_2025_postpartum_dsr (25), _tdds (21), _stai6 (6), _pss10 (10), _panas (20); wave 1 = first
#   trimester, 2 = 6 weeks, 3 = 1 year, 4 = 3 years postpartum. kankova_2025_child_disgust (CDS, 14 items,
#   mother-reported at 3 years, no wave column).
# Covariates: cov_place_recruitment (0/1), cov_age, cov_weight_prepregnancy, cov_education (1-4),
#   cov_family_income (1-7), cov_parity (0/1), cov_child_sex (0 girl / 1 boy), cov_delivery_mode (1-4);
#   per wave: cov_pregnancy_length_days (1T), cov_child_age_days (6w), cov_child_age_months (1y, 3y).
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

RAW_DIR = RAW_ROOT / "figshare_29590139"
DSR = ["DS-R1_R", "DS-R2", "DS-R3", "DS-R4", "DS-R5", "DS-R6_R", "DS-R7", "DS-R8", "DS-R9", "DS-R10_R", "DS-R11", "DS-R13",
       "DS-R14", "DS-R15", "DS-R17", "DS-R18", "DS-R19", "DS-R20", "DS-R21", "DS-R22", "DS-R23", "DS-R24", "DS-R25", "DS-R26", "DS-R27"]
TDDS = [f"tdds{i}" for i in range(1, 22)]
STAI = ["stai1_R", "stai2", "stai3", "stai4_R", "stai5_R", "stai6"]
PSS = ["pss1", "pss2", "pss3", "pss4_R", "pss5_R", "pss6", "pss7_R", "pss8_R", "pss9", "pss10"]
PANAS = ["panas1p", "panas2n", "panas3p", "panas4n", "panas5p", "panas6n", "panas7n", "panas8n", "panas9p", "panas10p",
         "panas11n", "panas12p", "panas13n", "panas14p", "panas15n", "panas16p", "panas17p", "panas18n", "panas19p", "panas20n"]
CDS = ["cds1", "cds2", "cds3_R", "cds4_R", "cds5", "cds6", "cds7", "cds8", "cds9", "cds10", "cds11_R", "cds12_R", "cds13", "cds14_R"]


def main() -> None:
    d = pd.read_excel(figshare_fetch(29590139, "Data_child disgust_figshare.xlsx", RAW_DIR), sheet_name="Data")
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == 163
    d["id"] = range(1, len(d) + 1)
    cov = {"cov_place_recruitment": "place_recruitment", "cov_age": "age", "cov_weight_prepregnancy": "weight_prepregnancy",
           "cov_education": "education", "cov_family_income": "family_income", "cov_parity": "parity",
           "cov_child_sex": "child_sex", "cov_delivery_mode": "delivery_mode"}
    for k, v in cov.items():
        d[k] = d[v]
    covs = list(cov)
    pre = {1: "1T_", 2: "6w_", 3: "1y_", 4: "3y_"}
    ex = {"cov_pregnancy_length_days": {1: "1Ta_pregnancy_length_days"}, "cov_child_age_days": {2: "6wa_child_age_days"},
          "cov_child_age_months": {3: "1y_child_age_months", 4: "3y_child_age_months"}}
    tabs = {"kankova_2025_postpartum_dsr": (stack_waves(d, pre, DSR, covs, range(0, 5), "dsr", ex), pv_for(DSR, range(0, 5))),
            "kankova_2025_postpartum_tdds": (stack_waves(d, pre, TDDS, covs, range(0, 7), "tdds", ex), pv_for(TDDS, range(0, 7))),
            "kankova_2025_postpartum_stai6": (stack_waves(d, pre, STAI, covs, range(1, 5), "stai", ex), pv_for(STAI, range(1, 5))),
            "kankova_2025_postpartum_pss10": (stack_waves(d, pre, PSS, covs, range(0, 5), "pss", ex), pv_for(PSS, range(0, 5))),
            "kankova_2025_postpartum_panas": (stack_waves(d, pre, PANAS, covs, range(1, 6), "panas", ex), pv_for(PANAS, range(1, 6)))}
    c = d[["id", *covs] + ["3y_" + i for i in CDS] + ["3y_child_age_months"]].copy().rename(columns={"3y_child_age_months": "cov_child_age_months"})
    c = drop_frac(c, ["3y_" + i for i in CDS], "cds").rename(columns={"3y_" + i: i for i in CDS})
    tabs["kankova_2025_child_disgust"] = (long(c, CDS, covs + ["cov_child_age_months"], valid=range(0, 3)), pv_for(CDS, range(0, 3)))
    emit(tabs)


if __name__ == "__main__":
    main()
