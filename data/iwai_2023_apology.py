#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/sgn96vfxr4
# DOI: 10.17632/sgn96vfxr4 (dataset, 2023; Iwai, Tatiana; Carvalho, João Vinícius). Data and materials for "How
#   Transgressor's Moral Identity Leads to High-Quality Apologies: The Positive Role of Guilt": three Brazilian
#   studies with an autobiographical-recall paradigm (Study 1 two-wave, N = 133; Study 2 experiment, N = 212;
#   Study 3, N = 241).
# Data: Study1_finalpublic.xlsx, Study2_finalpublic.xlsx, Study3_finalpublic.xlsx (Portuguese administration;
#       questionnaires in the four .docx files). Moral identity internalization, 5 items (Study 1 MI_1-5, Study 3
#       MI1, MI2, MI3R, MI4R, MI5; 1-5; the R items are the reverse-worded items stored as answered -- the _INV /
#       _Inv copies are the depositor's reversals and are not shipped) pooled over Studies 1 and 3 with cov_study;
#       shame (5 items, 1-5) pooled over Studies 2 and 3; guilt (3 items, 1-5) pooled over all three; PANAS
#       short form (PAN1_N..PAN10_P, 1-5, Study 3); apology quality ratings (APOL1-8, 1-7, Study 2). Means,
#       severity/intention single items and the coded apology components are not shipped.
# License: CC BY 4.0 (Mendeley Data).
#
# Item text: not shipped -- the workbooks carry codes only; the .docx questionnaires hold the Portuguese
#   wording but the codes are not printed beside the items, so the mapping would be positional.
#
# Tables: iwai_2023_moral_identity (5), iwai_2023_shame (5), iwai_2023_guilt (3), iwai_2023_panas10 (10),
#   iwai_2023_apology_quality (8).
# Covariates: cov_study (1-3), cov_gender (Study 1 text recoded 1 female / 2 male; Studies 2-3 as deposited),
#   cov_age, cov_education, cov_condition (Study 2: 1 moral-identity prime, 0 control).
# id: row index within study, offset by 1000 x study (Study 1's ID column has a duplicate; Study 3 has none).
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

RAW_DIR = RAW_ROOT / "mendeley_sgn96vfxr4"


def main() -> None:
    s1 = pd.read_excel(mendeley_fetch("sgn96vfxr4", "Study1_finalpublic.xlsx", RAW_DIR))
    s2 = pd.read_excel(mendeley_fetch("sgn96vfxr4", "Study2_finalpublic.xlsx", RAW_DIR))
    s3 = pd.read_excel(mendeley_fetch("sgn96vfxr4", "Study3_finalpublic.xlsx", RAW_DIR))
    for k, s in ((1, s1), (2, s2), (3, s3)):
        s.columns = [str(c).strip() for c in s.columns]
        s["id"] = k * 1000 + pd.RangeIndex(1, len(s) + 1)
        s["cov_study"] = k
        s["cov_age"] = s["Age"]
    s1["cov_gender"] = s1["Gender"].map({"Feminino": 1, "Masculino": 2})
    s2["cov_gender"] = s2["Gender"]; s3["cov_gender"] = s3["Gender"]
    s1["cov_education"] = pd.NA; s2["cov_education"] = s2["Education"]; s3["cov_education"] = s3["Education"]
    s2["cov_condition"] = s2["COND"]
    covs = ["cov_study", "cov_gender", "cov_age", "cov_education"]
    mi1 = s1.rename(columns={f"MI_{i}": f"MI{i}" for i in range(1, 6)})
    mi3 = s3.rename(columns={"MI3R": "MI3", "MI4R": "MI4"})
    mi = [f"MI{i}" for i in range(1, 6)]
    tabs = {}
    tabs["iwai_2023_moral_identity"] = (long(pd.concat([mi1[["id", *covs] + mi], mi3[["id", *covs] + mi]]), mi, covs, valid=range(1, 6)), pv_for(mi, range(1, 6)))
    sh = [f"Shame{i}" for i in range(1, 6)]
    sh2 = s2.rename(columns={f"Shame_{i}": f"Shame{i}" for i in range(1, 6)})
    tabs["iwai_2023_shame"] = (long(pd.concat([sh2[["id", *covs] + sh], s3[["id", *covs] + sh]]), sh, covs, valid=range(1, 6)), pv_for(sh, range(1, 6)))
    gu = [f"Guilt{i}" for i in range(1, 4)]
    gu2 = s2.rename(columns={f"Guilt_{i}": f"Guilt{i}" for i in range(1, 4)})
    tabs["iwai_2023_guilt"] = (long(pd.concat([s1[["id", *covs] + gu], gu2[["id", *covs] + gu], s3[["id", *covs] + gu]]), gu, covs, valid=range(1, 6)), pv_for(gu, range(1, 6)))
    pan = [c for c in s3.columns if c.startswith("PAN") and "_" in c]
    assert len(pan) == 10
    tabs["iwai_2023_panas10"] = (long(s3, pan, covs, valid=range(1, 6)), pv_for(pan, range(1, 6)))
    ap = [f"APOL{i}" for i in range(1, 9)]
    tabs["iwai_2023_apology_quality"] = (long(s2, ap, covs + ["cov_condition"], valid=range(1, 8)), pv_for(ap, range(1, 8)))
    emit(tabs)


if __name__ == "__main__":
    main()
