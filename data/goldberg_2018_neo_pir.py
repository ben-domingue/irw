#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/HE6LJR
# DOI: 10.7910/DVN/HE6LJR (Eugene-Springfield Community Sample collection, dataset ( 3))
#   Goldberg, L. R. (2018). ( 3) NEO-PI-R. Eugene-Springfield Community Sample. Harvard
#   Dataverse, V1.
# Data: NEO_PIR.tab (format=original -> NEO_PIR.sav): 857 ESCS participants x 276 columns:
#       i1..i240 are the 240 NEO-PI-R item responses, 0-4 (no value labels; the inventory is
#       Costa & McCrae's, 5-point strongly disagree .. strongly agree), followed by the five
#       domain and thirty facet scores (n, n1..n6, e, ...), which are derived and skipped.
#       data/goldberg_2018_escs.py excluded this dataset because its 275 columns span 175
#       distinct values; that is the facet/domain scores, which this script separates out.
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: not shipped. No variable labels on i1..i240 and no value labels (both levels
#   checked, both empty); the NEO-PI-R is a copyrighted PAR instrument.
#
# Covariates (cov_sex, cov_age, cov_educ, cov_ethnic, cov_employ, cov_marital) are joined
# from the collection's demographics file (DVN/VGMXJX), as in goldberg_2018_escs.py.

RAW_KEY = "10.7910_dvn_he6ljr"
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
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / RAW_KEY
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def dv_fetch(doi: str, fname: str, raw_dir: Path = None,
             host: str = "dataverse.harvard.edu") -> Path:
    """Fetch a Harvard Dataverse file by its ORIGINAL name, as format=original
    (never the lossy .tab conversion)."""
    raw_dir = raw_dir or RAW_DIR
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"].get("originalFileName", f["dataFile"]["filename"]) == fname][0]
        download(f"https://{host}/api/access/datafile/{fid}?format=original", p)
    return p


def to_long(d: pd.DataFrame, items, id_col="id", extra=(), rename=None) -> pd.DataFrame:
    """Melt `items` (wide columns) to id/item/resp, carrying `extra` columns."""
    keep = [id_col] + list(extra)
    t = d[keep + list(items)].melt(id_vars=keep, value_vars=list(items),
                                   var_name="item", value_name="resp")
    if rename:
        t["item"] = t["item"].map(lambda c: rename.get(c, c))
    t = t.dropna(subset=["resp"])
    if id_col != "id":
        t = t.rename(columns={id_col: "id"})
    lead = ["id", "item", "resp"] + [c for c in ("wave", "treat", "rt", "date") if c in t.columns]
    cov = [c for c in t.columns if c.startswith("cov_")]
    tail = [c for c in ("rater", "item_family") if c in t.columns]
    return t[lead + cov + tail].reset_index(drop=True)


def emit(tables: dict) -> None:
    """tables: name -> (long df, permitted_values or None). QC + validate + write."""
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in names:
        assert not (OUT_DIR / f"{name}.csv").exists() or os.environ.get("IRW_OVERWRITE"), \
            f"{name}.csv already staged; set IRW_OVERWRITE=1 to rebuild"
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"] + [c for c in ("wave", "rater") if c in t]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, (name, t["id"].nunique())
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


import pyreadstat  # noqa: E402

DOI = "10.7910/DVN/HE6LJR"
DEMOGRAPHICS = ("10.7910/DVN/VGMXJX", "demographics-1.sav")  # the unsuffixed copy is a .por
COVS = {"SEX": "cov_sex", "AGE": "cov_age", "EDUC": "cov_educ", "ETHNIC": "cov_ethnic",
        "EMPLOY": "cov_employ", "MARITAL": "cov_marital"}


def demographics() -> pd.DataFrame:
    p = dv_fetch(*DEMOGRAPHICS, raw_dir=RAW_DIR.parent / "10.7910_dvn_vgmxjx")
    dem, _ = pyreadstat.read_sav(str(p))
    dem.columns = [c.upper() for c in dem.columns]
    dem = dem.rename(columns={"ID": "id"})
    return dem[["id"] + [c for c in COVS if c in dem]].rename(columns=COVS)


def main() -> None:
    d, meta = pyreadstat.read_sav(str(dv_fetch(DOI, "NEO_PIR.sav")))
    assert d["id"].is_unique and len(d) == 857
    items = [f"i{k}" for k in range(1, 241)]
    assert all(c in d.columns for c in items)
    assert all(not meta.column_names_to_labels.get(c) for c in items)
    skipped = [c for c in d.columns if c not in items and c != "id"]
    print(f"skipping {len(skipped)} derived score columns: {skipped[:8]} ...")
    for c in items:
        assert d[c].dropna().isin([0, 1, 2, 3, 4]).all(), c
    d = d.merge(demographics(), on="id", how="left")
    cov = [c for c in d.columns if c.startswith("cov_")]
    t = to_long(d, items, extra=cov, rename={c: "neo" + c[1:] for c in items})
    emit({"goldberg_2018_neo_pir": (t, [0, 1, 2, 3, 4])})


if __name__ == "__main__":
    main()
