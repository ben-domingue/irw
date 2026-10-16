#!/usr/bin/env python3
# Source: https://osf.io/4v8y6/
# DOI: 10.3389/fpsyg.2023.1087977 (Piotrowski, K., Bojanowska, A., Szczygieł, D., Mikolajczak, M., & Roskam, I.
#   (2023). Parental burnout at different stages of parenthood: Links with temperament, Big Five traits, and
#   parental identity. Frontiers in Psychology, 14, 1087977.) Data: OSF node 4v8y6 (CC BY 4.0), 1,471 Polish
#   parents (T1 of the project).
# Data: "Parental burnout at different stages of parenthood_DATA.sav". T1_PBA1-23 = Parental Burnout Assessment
#       (0-6 frequency), T1_IPIP1-20 = IPIP-BFM-20 (1-5), T1_UMICS1-13 = Utrecht-Management of Identity
#       Commitments Scale, parental identity (1-5), T1_FCZKT1-42 = Formal Characteristics of Behaviour -
#       Temperament Inventory, 42 yes/no items (0/1). Subscale means, the recoded temperament scores and the free-
#       text disability descriptions are not shipped. No variable or value labels on the items.
# License: CC BY 4.0 (OSF node licence).
#
# Item text: not shipped -- no variable labels and no value labels on any item (both levels checked); the
#   Polish instruments are not in the deposit (Syntax.sps scores them but holds no wording).
#
# Tables: piotrowski_2024_pba (23), piotrowski_2024_ipip_bfm20 (20), piotrowski_2024_umics (13),
#   piotrowski_2024_fczkt (42).
# Covariates: cov_age, cov_gender (1 female, 2 male), cov_relationship_status (1 married, 2 informal, 3 single),
#   cov_education (1-5), cov_residence (1-4), cov_child_number, cov_youngest_child_age, cov_child_disability (0/1).
# id: row index.
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

RAW_DIR = RAW_ROOT / "osf_4v8y6"


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(str(osf_fetch("4v8y6", "Parental burnout at different stages of parenthood_DATA.sav", RAW_DIR)))
    assert len(d) == 1471
    d["id"] = range(1, len(d) + 1)
    cov = {"cov_age": "T1_age", "cov_gender": "T1_gender", "cov_relationship_status": "T1_relationship_status",
           "cov_education": "T1_education", "cov_residence": "T1_residence", "cov_child_number": "T1_child_nr",
           "cov_youngest_child_age": "youngest_child", "cov_child_disability": "T1_child_disab"}
    for k, v in cov.items():
        d[k] = d[v]
    covs = list(cov)
    blocks = {"piotrowski_2024_pba": ([f"T1_PBA{i}" for i in range(1, 24)], range(0, 7)),
              "piotrowski_2024_ipip_bfm20": ([f"T1_IPIP{i}" for i in range(1, 21)], range(1, 6)),
              "piotrowski_2024_umics": ([f"T1_UMICS{i}" for i in range(1, 14)], range(1, 6)),
              "piotrowski_2024_fczkt": ([f"T1_FCZKT{i}" for i in range(1, 43)], range(0, 2))}
    tabs = {}
    for name, (cols, valid) in blocks.items():
        ren = {c: c[3:] for c in cols}
        tabs[name] = (long(d, cols, covs, valid=valid, rename=ren), pv_for(list(ren.values()), valid))
    emit(tabs)


if __name__ == "__main__":
    main()
