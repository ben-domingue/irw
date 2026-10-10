#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.12480350.v1
# DOI: 10.6084/m9.figshare.12480350.v1 (dataset; the record names no paper)
#   Spasovski, Ognen (2020). Well-being in pandemic_Raw Data_Spasovski_Kenig.sav. figshare.
# Data: the .sav: 510 students of the largest university in North Macedonia, surveyed online
#       in April 2020 one month into the COVID-19 lockdown. The PERMA-Profiler (Butler &
#       Kern 2016), 23 items on 0-10, administered in Macedonian: variable labels carry the
#       Profiler's own item codes (P1-3, E1-3, R1-3, M1-3, A1-3, N1-3, H1-3, LON, Hap)
#       followed by the Macedonian stem; v21 is an attention check and is dropped.
# License: CC0 1.0 (figshare record).
#
# Item text: not shipped -- rights. The PERMA-Profiler is a `block` row in
#   itemtext/instrument_rights_register.csv (all items incl. translations). The Macedonian
#   stems are in the .sav variable labels (checked; no value labels on the items).
#
# One table: spasovski_2020_perma, item = the PERMA-Profiler code read from the variable
#   label (P1 .. Hap), resp 0-10.
# Covariates: cov_gender (1 male, 2 female), cov_age (years), cov_ethnicity (code 1-7 as
#   deposited: 1 mac, 2 alb, 3 tur, 4 vlach ...), cov_days_in_isolation (v2, 1-4).
# id: the deposit's id.

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

import re  # noqa: E402

import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "10_6084_m9_figshare_12480350_v1"
FNAME = "Well-being in pandemic_Raw Data_Spasovski_Kenig.sav"
CODES = {f"{p}{k}" for p in "PERMANH" for k in (1, 2, 3)} | {"LON", "Hap"}


def main() -> None:
    d, meta = pyreadstat.read_sav(str(figshare_fetch(12480350, FNAME, RAW_DIR)))
    assert len(d) == 510 and d["id"].is_unique
    rename = {}
    for c in [f"v{k}" for k in range(10, 33)] + ["Вокојамерасечувствувашсакано"]:
        lab = meta.column_names_to_labels.get(c) or ""
        m = re.match(r"\s*(P[123]|E[123]|R[123]|M[123]|A[123]|N[123]|H[123]|LON|Hap)(?![A-Za-z0-9])", lab)
        if m:
            rename[c] = m.group(1)
    assert set(rename.values()) == CODES and len(rename) == 23, rename
    assert "v21" not in rename  # the attention check
    d = d.rename(columns={"Пол": "cov_gender", "Возраствогодини": "cov_age", "v2": "cov_days_in_isolation"})
    d["cov_ethnicity"] = pd.to_numeric(d["Етничкаприпадност"], errors="coerce").astype("Int64")
    covs = ["cov_gender", "cov_age", "cov_ethnicity", "cov_days_in_isolation"]
    for c in ("cov_gender", "cov_age", "cov_days_in_isolation"):
        d[c] = d[c].astype("Int64")
    t = long(d, list(rename), covs, valid=range(0, 11), rename=rename)
    emit({"spasovski_2020_perma": (t, pv_for(CODES, range(0, 11)))})


if __name__ == "__main__":
    main()
