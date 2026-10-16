#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Data_from_Parental_Phubbing_and_Academic_Burnout_in_Adolescents_The_Mediating_Role_of_Family_Cohesion_and_Core_Self-Evaluation_and_the_Moderating_Role_of_Perceived_Social_Support/29891609
# DOI: 10.6084/m9.figshare.29891609 (dataset, 2025; Huang, Jingting; Fu, Mei). "Data from Parental Phubbing and
#   Academic Burnout in Adolescents: The Mediating Role of Family Cohesion and Core Self-Evaluation and the
#   Moderating Role of Perceived Social Support" -- 787 Chinese adolescents (grades 7, 8, 10; Anhui and Guangdong).
# Data: data_Parental phubbing and adolescents' academic burnout.xlsx. PH-1..9 = parental phubbing (1-5),
#       FC-1..16 = family cohesion (1-5), CSE-1..8 = Core Self-Evaluations Scale (1-5), PSS-1..12 =
#       Multidimensional Scale of Perceived Social Support (1-7), AB-1..16 = academic burnout (1-5). The record
#       says missing values were replaced by the mean; those non-integer cells are dropped. Item codes keep the
#       source headers (hyphen included).
# License: CC BY 4.0 (figshare).
#
# Item text: not shipped -- codes only; the Chinese instruments are not in the deposit.
#
# Tables: huang_2025_parental_phubbing (9), huang_2025_family_cohesion (16), huang_2025_core_self_evaluation (8),
#   huang_2025_perceived_social_support (12), huang_2025_academic_burnout (16).
# Covariates: cov_gender (1 boy, 2 girl), cov_age, cov_grade (1 seventh, 2 eighth, 3 tenth), cov_only_child (1
#   only child, 2 not), cov_region (1 Anhui, 2 Guangdong).
# id: row index (the Sample column has a duplicate).
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

RAW_DIR = RAW_ROOT / "figshare_29891609"


def main() -> None:
    d = pd.read_excel(figshare_fetch(29891609, "data_Parental phubbing and adolescents’ academic burnout.xlsx", RAW_DIR))
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == 787
    d["id"] = range(1, len(d) + 1)
    ren = {c: "cov_" + c.split("(")[0].strip().lower().replace(" ", "_") for c in d.columns if "(" in c}
    d = d.rename(columns=ren).rename(columns={"cov_only_child_status": "cov_only_child", "Age": "cov_age"})
    covs = ["cov_gender", "cov_age", "cov_grade", "cov_only_child", "cov_region"]
    blocks = {"huang_2025_parental_phubbing": ("PH-", 9, range(1, 6)), "huang_2025_family_cohesion": ("FC-", 16, range(1, 6)),
              "huang_2025_core_self_evaluation": ("CSE-", 8, range(1, 6)), "huang_2025_perceived_social_support": ("PSS-", 12, range(1, 8)),
              "huang_2025_academic_burnout": ("AB-", 16, range(1, 6))}
    tabs = {}
    for name, (pre, n, valid) in blocks.items():
        cols = [f"{pre}{i}" for i in range(1, n + 1)]
        d = drop_frac(d, cols, name)
        tabs[name] = (long(d, cols, covs, valid=valid), pv_for(cols, valid))
    emit(tabs)


if __name__ == "__main__":
    main()
