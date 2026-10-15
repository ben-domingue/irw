#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/ZESEYD
# DOI: 10.7910/DVN/ZESEYD (dataset; paper 10.5534/wjmh.220081)
#   Cho, M. C., et al. (2023). Does preoperative bladder compliance affect long-term functional
#   outcomes after laser prostatectomy? World Journal of Men's Health. Dataset deposited by
#   Park, Hyun Jun; dataset author Min Chul Cho (Seoul National University Boramae Medical Center).
# Data: bladdercompliance_anony.sav, one row per patient (1,985 men, laser prostatectomy
#       2008-2014) with the 7-item International Prostate Symptom Score (IPSS, 0-5) and the 4-item
#       Overactive Bladder Symptom Score (OABSS, 0-2/0-3/0-5/0-5) at baseline and at 1, 3, 6 and 12
#       months and 2, 3 and 4 years (OABSS also 5 years) after surgery, plus urodynamic, PSA and
#       medication columns that are not item-response data. The *_C / *_P columns are change
#       scores; IPSS_total / QOL_index are the authors' summaries. Baseline and follow-up columns
#       ship under `wave` (0 = preoperative, then months: 1, 3, 6, 12, 24, 36, 48, 60).
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: not shipped -- the .sav carries no variable labels and no value labels for the
#   IPSS/OABSS items (both levels empty; codes are IPSS_Q1..Q7 / OABSS_Q1..Q4); the IPSS wording
#   is the standard AUA instrument, not in the deposit.
#
# Tables: cho_2023_ipss (7 items x up to 8 waves), cho_2023_oabss (4 items x up to 9 waves).
# Cleaning: a handful of fractional cells (e.g. 0.44 at 4 years) and out-of-range codes (an
#   OABSS_Q1 of 6 on a 0-2 item) are dropped as entry errors; counts are printed.
# Covariates: cov_age (years), cov_procedure (1 HPS photoselective vaporisation, 2 HoLEP).
# id: row index (the file has no patient identifier). Operation dates are not shipped.
import os
import sys
from pathlib import Path

import pandas as pd
import requests

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

import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "10_7910_DVN_ZESEYD"
FNAME = "bladdercompliance_anony.sav"
WAVES = {"": 0, "_1mo": 1, "_3mo": 3, "_6mo": 6, "_12mo": 12, "_2yr": 24, "_3yr": 36, "_4yr": 48, "_5yr": 60}
IPSS = {f"IPSS_Q{i}": range(0, 6) for i in range(1, 8)}
OABSS = {"OABSS_Q1": range(0, 3), "OABSS_Q2": range(0, 4), "OABSS_Q3": range(0, 6), "OABSS_Q4": range(0, 6)}


def stack(d: pd.DataFrame, items: dict, covs: list, name: str) -> pd.DataFrame:
    parts = []
    for suf, wave in WAVES.items():
        cols = [c for c in items if f"{c}{suf}" in d.columns]
        if not cols:
            continue
        w = d[["id", *covs] + [f"{c}{suf}" for c in cols]].rename(columns={f"{c}{suf}": c for c in cols})
        w["wave"] = wave
        parts.append(w)
    wide = pd.concat(parts, ignore_index=True)
    dropped = 0
    for c, valid in items.items():
        v = pd.to_numeric(wide[c], errors="coerce")
        bad = v.notna() & ((v % 1 != 0) | ~v.isin(list(valid)))
        dropped += int(bad.sum())
        wide.loc[bad, c] = pd.NA
    print(f"    {name}: dropped {dropped} fractional/out-of-range cells")
    t = long(wide, list(items), covs, extra=["wave"])
    return t


def main() -> None:
    d, meta = pyreadstat.read_sav(str(dv_fetch("10.7910/DVN/ZESEYD", FNAME, RAW_DIR)))
    assert len(d) == 1985
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns={"Age": "cov_age", "Tx_group_bi": "cov_procedure"})
    covs = ["cov_age", "cov_procedure"]
    for c in covs:
        d[c] = d[c].astype("Int64")
    ipss = stack(d, IPSS, covs, "ipss")
    oabss = stack(d, OABSS, covs, "oabss")
    emit({"cho_2023_ipss": (ipss, IPSS), "cho_2023_oabss": (oabss, OABSS)})


if __name__ == "__main__":
    main()
