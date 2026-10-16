#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/6IO5ET
# DOI: 10.7910/DVN/6IO5ET (dataset, 2015; Kam, Cindy D.; Estes, Beth A.). Replication data for "Disgust
#   Sensitivity and Public Demand for Protection" (Journal of Politics): the authors' 2012 CCES team module,
#   N = 1,500 US adults (YouGov).
# Data: "KAM ESTES JOP DATA.dta" (+ CCES12_VAN_OUTPUT_20130311_CODEBOOK.pdf). VAN341-VAN348 = an eight-item
#       disgust-sensitivity battery (toilet, cook, monkey, vomit, soda, chocolate, maggot, milk; 1-5; the monkey
#       item is reverse-keyed per the authors' .do file, shipped as stored), asked either mid-survey (_mid) or at
#       the end (_last) in a placement experiment -- one placement per respondent, kept as cov_placement, item code
#       = the bare variable name. VAN360-VAN369 = TIPI (1-7), VAN381-VAN384 = racial resentment (1-5, agree ->
#       disagree as stored). Codes 8 (skipped) / 9 (not asked) are missing. moral1-4, socdist1-2, the child-rearing
#       pairs and the single policy items are not shipped (undocumented wording or single items).
# License: CC0 1.0 (Harvard Dataverse).
#
# Item text: not shipped -- the .dta labels are short mnemonics ("disgust_toilet", "Resent - Irish", "TIPI -
#   Extraverted, enthusiastic") and the codebook repeats them without the question wording; TIPI stems are only
#   the trait-pair fragments. Value labels (anchors) are in the codebook but no stems.
#
# Tables: kam_2015_disgust8 (8), kam_2015_tipi (10), kam_2015_racial_resentment (4).
# Covariates: cov_placement (mid / last; disgust table only), cov_birth_year, cov_gender (1 male, 2 female),
#   cov_education (1-6), cov_race (1-8), cov_party_id7 (1-7, 8 not sure), cov_ideology (1-6), cov_family_income
#   (1-16, 97 prefer not to say), cov_religion (1-12), cov_born_again (1/2), cov_weight (team weight V102).
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

RAW_DIR = RAW_ROOT / "dvn_6IO5ET"
DIS = [f"VAN34{i}" for i in range(1, 9)]
TIPI = [f"VAN36{i}" for i in range(0, 10)]
RES = [f"VAN38{i}" for i in range(1, 5)]


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_dta(str(dv_fetch("10.7910/DVN/6IO5ET", "KAM ESTES JOP DATA.dta", RAW_DIR)))
    assert len(d) == 1500
    d["id"] = range(1, len(d) + 1)
    cov = {"cov_birth_year": "birthyr", "cov_gender": "gender", "cov_education": "educ", "cov_race": "race", "cov_party_id7": "pid7",
           "cov_ideology": "CC334A", "cov_family_income": "faminc", "cov_religion": "religpew", "cov_born_again": "pew_bornagain", "cov_weight": "V102"}
    for k, v in cov.items():
        d[k] = pd.to_numeric(d[v], errors="coerce")
    covs = list(cov)
    def clean(cols, valid):
        v = d[cols].apply(pd.to_numeric, errors="coerce")
        d[cols] = v.mask(~v.isin(list(valid)))
    # disgust: one placement per respondent
    mid = d[[c + "_mid" for c in DIS]].apply(pd.to_numeric, errors="coerce").isin(range(1, 6)).any(axis=1)
    last = d[[c + "_last" for c in DIS]].apply(pd.to_numeric, errors="coerce").isin(range(1, 6)).any(axis=1)
    assert not (mid & last).any()
    print(f"    [disgust] mid placement {int(mid.sum())}, last placement {int(last.sum())}, neither {int((~mid & ~last).sum())}")
    d["cov_placement"] = pd.Series(pd.NA, index=d.index, dtype="object")
    d.loc[mid, "cov_placement"] = "mid"; d.loc[last, "cov_placement"] = "last"
    for c in DIS:
        a = pd.to_numeric(d[c + "_mid"], errors="coerce"); b = pd.to_numeric(d[c + "_last"], errors="coerce")
        d[c] = a.where(mid, b)
    clean(DIS, range(1, 6)); clean(TIPI, range(1, 8)); clean(RES, range(1, 6))
    emit({"kam_2015_disgust8": (long(d, DIS, ["cov_placement"] + covs, valid=range(1, 6)), pv_for(DIS, range(1, 6))),
          "kam_2015_tipi": (long(d, TIPI, covs, valid=range(1, 8)), pv_for(TIPI, range(1, 8))),
          "kam_2015_racial_resentment": (long(d, RES, covs, valid=range(1, 6)), pv_for(RES, range(1, 6)))})


if __name__ == "__main__":
    main()
