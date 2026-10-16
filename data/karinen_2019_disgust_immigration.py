#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/rgy8jngdrz
# DOI: 10.1016/j.jesp.2019.103817 (Karinen, A. K., Molho, C., Kupfer, T. R., & Tybur, J. M. (2019). Disgust
#   sensitivity and opposition to immigration: Does contact avoidance or resistance to foreign norms explain the
#   relationship? Journal of Experimental Social Psychology, 84, 103817.) Data: Mendeley 10.17632/rgy8jngdrz,
#   US online sample (N = 1,307 Qualtrics rows; 1,089 finished).
# Data: DataForJESP.sav (Qualtrics export with full variable labels and value labels). TDDS1-7 = pathogen
#       disgust items of the Three Domain Disgust Scale (0-6), SDO1-SDO16_R = SDO7 (1-7), ASC1_R-ASC6 =
#       traditionalism (1-7), Imm1_R-Imm6 = attitudes toward the described immigrant "Ngolo" (1-7) in a 2x2
#       vignette experiment (contact x assimilation; conditions kept as covariates), Mc_ items = manipulation
#       checks (not shipped), SOI2-4 = three sociosexuality items (1-9; not shipped, 3 items). Items with _R are
#       stored reverse-coded by the authors, shipped as stored. Preview rows (DistributionChannel = preview) are
#       dropped; the authors' exclusion flags ship as covariates rather than filtering. ResponseId (platform ID)
#       is replaced by the row index; the Qualtrics timestamps are not shipped.
# License: CC BY 4.0 (Mendeley Data).
#
# Item text: shipped (SPSS variable labels = stems, value labels = anchors, both present on every shipped item)
#   -- itemtext_output/karinen_2019_*__items.csv.
#
# Tables: karinen_2019_tdds_pathogen (7), karinen_2019_sdo7 (16), karinen_2019_traditionalism (6),
#   karinen_2019_immigrant_attitudes (6).
# Covariates: cov_age, cov_gender (1-3), cov_education (1-7), cov_income (1-28), cov_social_class (1-9),
#   cov_political_social, cov_political_economic (1-7), cov_contact (0 low / 1 high vignette condition),
#   cov_assimilation (0/1), cov_excluded (authors' combined exclusion flag, 0/1).
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

RAW_DIR = RAW_ROOT / "mendeley_rgy8jngdrz"
TDDS = [f"TDDS{i}" for i in range(1, 8)]
SDO = ["SDO1", "SDO2", "SDO3", "SDO4", "SDO5_R", "SDO6_R", "SDO7_R", "SDO8_R", "SDO9", "SDO10", "SDO11", "SDO12", "SDO13_R", "SDO14_R", "SDO15_R", "SDO16_R"]
ASC = ["ASC1_R", "ASC2", "ASC3", "ASC4_R", "ASC5_R", "ASC6"]
IMM = ["Imm1_R", "Imm2_R", "Imm3_R", "Imm4", "Imm5", "Imm6"]


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(str(mendeley_fetch("rgy8jngdrz", "DataForJESP.sav", RAW_DIR)))
    n0 = len(d)
    d = d[d["DistributionChannel"] != "preview"].copy()
    print(f"    {n0 - len(d)} preview row(s) dropped; {len(d)} remain")
    d["id"] = range(1, len(d) + 1)
    cov = {"cov_age": "Age", "cov_gender": "Gender", "cov_education": "Education", "cov_income": "Income", "cov_social_class": "Social_Class",
           "cov_political_social": "Pol_social", "cov_political_economic": "Pol_economic", "cov_contact": "Contact",
           "cov_assimilation": "Assimilation", "cov_excluded": "Excluded_everythingCombined"}
    for k, v in cov.items():
        d[k] = d[v]
    covs = list(cov)
    emit({"karinen_2019_tdds_pathogen": (long(d, TDDS, covs, valid=range(0, 7)), pv_for(TDDS, range(0, 7))),
          "karinen_2019_sdo7": (long(d, SDO, covs, valid=range(1, 8)), pv_for(SDO, range(1, 8))),
          "karinen_2019_traditionalism": (long(d, ASC, covs, valid=range(1, 8)), pv_for(ASC, range(1, 8))),
          "karinen_2019_immigrant_attitudes": (long(d, IMM, covs, valid=range(1, 8)), pv_for(IMM, range(1, 8)))})


if __name__ == "__main__":
    main()
