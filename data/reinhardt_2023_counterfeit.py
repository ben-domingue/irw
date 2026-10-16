#!/usr/bin/env python3
# Source: https://osf.io/hmnpt/
# DOI: none on the record (OSF project, 2023; Reinhardt, Nina). "The correlation between Honesty-Humility and
#   attitude towards counterfeit luxury": two MTurk studies (Study 1 Sept 2022, N = 604; Study 2 Jan 2023,
#   N = 503), preregistered (AsPredicted PDFs in the node).
# Data: "Study 1_Raw.sav", "Study 2_Raw.sav" (Unipark exports; the "After Syntax" files are the scored versions).
#       HEXACO Honesty-Humility, 16 items (v_56-v_65, v_167-v_172; 1-5) and attitude toward counterfeit luxury, 15
#       items (v_174-v_189 without the attention check v_180; 1-5), both studies pooled with cov_study. Study 2
#       adds self-concept clarity (v_203-v_214, 12 items, 1-5), risk aversion (6 items, 1-7), materialism (7
#       items, 1-7) and an integrity/rule-following block (v_215-v_221, 7 items, 1-5). Item codes are the
#       export's own column names (kept as the join key); every item carries its stem as the variable label and
#       its anchors as value labels. Respondents who answered "No" to the final data-use consent item (v_913 = 2)
#       are dropped. The MTurk ID column is replaced by the row index; the geolocation columns are constants.
#       Attention checks v_108 / v_180 are constant (all passed) and not shipped.
# License: CC BY 4.0 (OSF node licence).
#
# Item text: shipped (SPSS variable labels = stems, value labels = anchors, both levels present on every shipped
#   item in both files) -- itemtext_output/reinhardt_2023_*__items.csv.
#
# Tables: reinhardt_2023_honesty_humility (16), reinhardt_2023_counterfeit_attitude (15),
#   reinhardt_2023_self_concept_clarity (12), reinhardt_2023_risk_aversion (6), reinhardt_2023_materialism (7),
#   reinhardt_2023_integrity (7).
# Covariates: cov_study (1/2), cov_age, cov_gender (1 female, 2 male, 3 diverse/non-binary), cov_profession
#   (1-5), cov_ethnicity (1-8).
# id: row index within study, offset by 1000 x study.
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

RAW_DIR = RAW_ROOT / "osf_hmnpt"
HH = [f"v_{i}" for i in range(56, 66)] + [f"v_{i}" for i in range(167, 173)]
CF = [f"v_{i}" for i in range(174, 190) if i != 180]
SCC = [f"v_{i}" for i in range(203, 215)]
RISK = ["v_a4c10", "v_d785a", "v_caaa5", "v_8bf4f", "v_4fc1d", "v_0396b"]
MAT = ["v_a3b6f", "v_222", "v_223", "v_224", "v_225", "v_226", "v_b0d0d"]
INT = [f"v_{i}" for i in range(215, 222)]


def load(k: int, fname: str) -> pd.DataFrame:
    import pyreadstat
    d, meta = pyreadstat.read_sav(str(osf_fetch("hmnpt", fname, RAW_DIR)))
    n0 = len(d)
    d = d[d["v_913"] != 2].copy()
    print(f"    [study {k}] {n0 - len(d)} respondent(s) withdrew data-use consent, dropped")
    d["id"] = k * 1000 + pd.RangeIndex(1, len(d) + 1)
    d["cov_study"] = k
    d = d.rename(columns={"v_234": "cov_age", "v_227": "cov_gender", "v_194": "cov_profession", "v_263": "cov_ethnicity"})
    return d


def main() -> None:
    s1 = load(1, "Study 1_Raw.sav"); s2 = load(2, "Study 2_Raw.sav")
    covs = ["cov_study", "cov_age", "cov_gender", "cov_profession", "cov_ethnicity"]
    both = pd.concat([s1[["id", *covs] + HH + CF], s2[["id", *covs] + HH + CF]])
    assert len(MAT) == 7  # v_a3b6f, v_222-226, v_b0d0d
    tabs = {"reinhardt_2023_honesty_humility": (long(both, HH, covs, valid=range(1, 6)), pv_for(HH, range(1, 6))),
            "reinhardt_2023_counterfeit_attitude": (long(both, CF, covs, valid=range(1, 6)), pv_for(CF, range(1, 6))),
            "reinhardt_2023_self_concept_clarity": (long(s2, SCC, covs, valid=range(1, 6)), pv_for(SCC, range(1, 6))),
            "reinhardt_2023_risk_aversion": (long(s2, RISK, covs, valid=range(1, 8)), pv_for(RISK, range(1, 8))),
            "reinhardt_2023_materialism": (long(s2, MAT, covs, valid=range(1, 8)), pv_for(MAT, range(1, 8))),
            "reinhardt_2023_integrity": (long(s2, INT, covs, valid=range(1, 6)), pv_for(INT, range(1, 6)))}
    emit(tabs)


if __name__ == "__main__":
    main()
