#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Longitudinal_associations_between_disgust_sensitivity_and_state_anxiety_across_all_three_trimesters_of_pregnancy/25039721
# DOI: 10.6084/m9.figshare.25039721 (dataset, 2025; Kaňková, Šárka). Czech pregnant women (n = 261) completed the
#   Disgust Scale-Revised, the Three Domain Disgust Scale and the six-item state anxiety scale (STAI-6) in each
#   trimester (T1, T2, T3). Overlaps with the lab's other deposits: 152 of the 246 T1 DS-R vectors match the
#   early-pregnancy women of 10.6084/m9.figshare.23807697 (dlouha_2023_*), 253 T3 vectors match the third-
#   trimester wave of 10.6084/m9.figshare.31423337 (benesova_2026_*), 37 T1 vectors match 1T of
#   10.6084/m9.figshare.29590139 (kankova_2025_postpartum_*). Codes differ across deposits, so the tables are
#   shipped per deposit with a data note.
# Data: "Disgust and Anxiety in pregnancy.xlsx", sheet "Data" (261 rows) + "Key". T<k>_DS-R (0-4; items 1, 6, 10
#       stored reversed; catch items 12/16 absent), T<k>_tdds1-21 (0-6), T<k>_stai1-6 (1-4; items 1, 4, 5 stored
#       reversed; the T1 file names stai item 4 "T2_stai4_R" and T2's "T2_stai4_R.1" -- a header slip, mapped by
#       position). Non-integer cells = person-mean imputation, dropped. Scores not shipped.
# License: CC BY 4.0 (figshare).
#
# Item text: not shipped -- codes only; Czech wording not in the deposit.
#
# Tables: kankova_2025_trimester_dsr (25), kankova_2025_trimester_tdds (21), kankova_2025_trimester_stai6 (6);
#   wave 1-3 = trimester.
# Covariates: cov_clinic, cov_age, cov_height, cov_weight_prepregnancy, cov_bmi_prepregnancy,
#   cov_smoking_prepregnancy (1-3), cov_education (1-4), cov_marital_status (1-4), cov_family_income (1-7),
#   cov_residence_size (1-5), cov_parity (0/1), cov_child_sex (0/1), cov_diabetes, cov_hypertension (0/1),
#   cov_pregnancy_length_days (per wave).
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

RAW_DIR = RAW_ROOT / "figshare_25039721"
DSR = ["DS-R1_R", "DS-R2", "DS-R3", "DS-R4", "DS-R5", "DS-R6_R", "DS-R7", "DS-R8", "DS-R9", "DS-R10_R", "DS-R11", "DS-R13",
       "DS-R14", "DS-R15", "DS-R17", "DS-R18", "DS-R19", "DS-R20", "DS-R21", "DS-R22", "DS-R23", "DS-R24", "DS-R25", "DS-R26", "DS-R27"]
TDDS = [f"tdds{i}" for i in range(1, 22)]
STAI = ["stai1_R", "stai2", "stai3", "stai4_R", "stai5_R", "stai6"]


def main() -> None:
    d = pd.read_excel(figshare_fetch(25039721, "Disgust and Anxiety in pregnancy.xlsx", RAW_DIR), sheet_name="Data")
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == 261
    d = d.rename(columns={"T2_stai4_R.1": "T2_stai4_R_fix"})
    # the T1 block's fourth STAI item is headed "T2_stai4_R" in the file (slip); the T2 block's is "T2_stai4_R.1"
    d = d.rename(columns={"T2_stai4_R": "T1_stai4_R", "T2_stai4_R_fix": "T2_stai4_R"})
    d["id"] = range(1, len(d) + 1)
    cov = {"cov_clinic": "clinic", "cov_age": "maternal age", "cov_height": "maternal body height",
           "cov_weight_prepregnancy": "weight_prepregnancy", "cov_bmi_prepregnancy": "BMI_prepregnancy",
           "cov_smoking_prepregnancy": "smoking_prepregnancy", "cov_education": "maternal education",
           "cov_marital_status": "marital_status", "cov_family_income": "family_income", "cov_residence_size": "residence_size",
           "cov_parity": "parity", "cov_child_sex": "child_sex", "cov_diabetes": "diabetes", "cov_hypertension": "hypertension"}
    for k, v in cov.items():
        d[k] = d[v]
    pre = {1: "T1_", 2: "T2_", 3: "T3_"}
    ex = {"cov_pregnancy_length_days": {w: f"T{w}_pregnancy_lenght_days_calculated" for w in (1, 2, 3)}}
    emit({"kankova_2025_trimester_dsr": (stack_waves(d, pre, DSR, list(cov), range(0, 5), "dsr", ex), pv_for(DSR, range(0, 5))),
          "kankova_2025_trimester_tdds": (stack_waves(d, pre, TDDS, list(cov), range(0, 7), "tdds", ex), pv_for(TDDS, range(0, 7))),
          "kankova_2025_trimester_stai6": (stack_waves(d, pre, STAI, list(cov), range(1, 5), "stai", ex), pv_for(STAI, range(1, 5)))})


if __name__ == "__main__":
    main()
