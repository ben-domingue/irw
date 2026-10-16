#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Disgust_sensitivity_before_and_after_conception/32957309
# DOI: 10.6084/m9.figshare.32957309 (dataset, 2026; Kaňková, Šárka; Ullmann, Jana). Czech women assessed before
#   conception (T0) and again in early pregnancy (T1a, and a second early-pregnancy visit T1b): STAI-6, Disgust
#   Scale-Revised, Three Domain Disgust Scale and the C-DIS picture-rating task (20 disgust-salient and 20 matched
#   control pictures rated 0-6). No overlap with the lab's other IRW tables (0 shared DS-R vectors).
# Data: Disgust_BeforeAfterConception_dataset_figshare_anonymous.xlsx, sheet "Data" (131 rows) + "Key". T0_/T1a_/
#       T1b_ prefixes = wave 1/2/3. dsr1_R..dsr27 (0-4; items 1, 6, 10 stored reversed; 12/16 absent), tdds_1-21
#       (0-6), stai_1_R..stai_6 (1-4; 1, 4, 5 stored reversed), c-dis<k>_control / c-dis<k>_salient (0-6; T0 and
#       T1b only). Non-integer cells = person-mean imputation, dropped. Scores and eye-tracking not shipped.
# License: CC BY 4.0 (figshare).
#
# Item text: not shipped -- codes only; Czech wording and the C-DIS pictures are not in the deposit.
#
# Tables: kankova_2026_conception_dsr (25), _tdds (21), _stai6 (6), _cdis (40 picture ratings); wave 1 = before
#   conception, 2 = first early-pregnancy visit, 3 = second early-pregnancy visit.
# Covariates: cov_group (G1-G4 as deposited, undocumented), cov_education (1-4), cov_parity (0/1),
#   cov_conception (1 natural, 2 assisted), cov_age (per wave), cov_bmi (per wave), cov_pregnancy_length_days (per
#   wave, blank at T0).
# id: the deposit's id column.
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

RAW_DIR = RAW_ROOT / "figshare_32957309"
DSR = ["dsr1_R", "dsr2", "dsr3", "dsr4", "dsr5", "dsr6_R", "dsr7", "dsr8", "dsr9", "dsr10_R", "dsr11", "dsr13", "dsr14", "dsr15",
       "dsr17", "dsr18", "dsr19", "dsr20", "dsr21", "dsr22", "dsr23", "dsr24", "dsr25", "dsr26", "dsr27"]
TDDS = [f"tdds_{i}" for i in range(1, 22)]
STAI = ["stai_1_R", "stai_2", "stai_3", "stai_4_R", "stai_5_R", "stai_6"]
CDIS = [f"c-dis{i}_{k}" for i in range(1, 21) for k in ("control", "salient")]


def main() -> None:
    d = pd.read_excel(figshare_fetch(32957309, "Disgust_BeforeAfterConception_dataset_figshare_anonymous.xlsx", RAW_DIR), sheet_name="Data")
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == 131 and d["id"].is_unique
    d["id"] = d["id"].astype(int)
    d["cov_group"] = d["group"]; d["cov_education"] = d["T0_education"]; d["cov_parity"] = d["parity"]; d["cov_conception"] = d["conception"]
    covs = ["cov_group", "cov_education", "cov_parity", "cov_conception"]
    pre = {1: "T0_", 2: "T1a_", 3: "T1b_"}
    ex = {"cov_age": {1: "T0_age", 2: "T1a_age", 3: "T1b_age"}, "cov_bmi": {1: "T0_BMI", 2: "T1a_BMI", 3: "T1b_BMI"},
          "cov_pregnancy_length_days": {2: "T1a_pregnancy_lenght_days", 3: "T1b_pregnancy_lenght_days"}}
    tabs = {"kankova_2026_conception_dsr": (stack_waves(d, pre, DSR, covs, range(0, 5), "dsr", ex), pv_for(DSR, range(0, 5))),
            "kankova_2026_conception_tdds": (stack_waves(d, pre, TDDS, covs, range(0, 7), "tdds", ex), pv_for(TDDS, range(0, 7))),
            "kankova_2026_conception_stai6": (stack_waves(d, pre, STAI, covs, range(1, 5), "stai", ex), pv_for(STAI, range(1, 5))),
            "kankova_2026_conception_cdis": (stack_waves(d, {1: "T0_", 3: "T1b_"}, CDIS, covs, range(0, 7), "cdis", ex), pv_for(CDIS, range(0, 7)))}
    emit(tabs)


if __name__ == "__main__":
    main()
