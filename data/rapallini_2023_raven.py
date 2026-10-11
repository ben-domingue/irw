#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/FSRV5D
# DOI: 10.7910/DVN/FSRV5D (dataset; the record names no published paper)
#   Rapallini, C., Minello, A., Vignoli, D., & Rustichini, A. (2023). Replication Data for:
#   Fluid intelligence and fertility intentions. Harvard Dataverse, V1.
# Data: DatTrueCouples.dta (format=original): 1,678 partnered adults (both partners of 839
#       couples) surveyed in 2019 in Florence, Italy (800) and Oslo, Norway (878), one row per
#       person. Shipped: the 12-item Raven-type matrices test (D1-D12, the option chosen, 1-8)
#       with per-item times (D1t-D12t, seconds). The deposit gives the total score (Raven, 0-12)
#       but no key; the key is derived here from the responses -- for each item, the one option
#       that makes the item-correct sum equal the deposited total for every one of the 1,676 fully
#       scored respondents (least-squares on option indicators, then an exact check). resp is
#       1 correct / 0 incorrect against that key. Not shipped: the fertility-intention and
#       attitude blocks (Q1-Q13, Q22-Q64; no codebook or do-file labels, so the items cannot be
#       named), the ten TIPI columns (BIG5a-l, letter codes only), the lottery choice lists
#       (Q14/Q15), and the derived/standardised columns.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped -- matrices are image stimuli; the deposit has no item material.
#   Checked both label levels: variable labels are the column names, value labels only on
#   covariates.
#
# Tables: rapallini_2023_raven (1,677 x 12, 0/1, rt in seconds; one respondent has a partial answer set).
# Covariates: cov_country (Italy/Norway), cov_sex, cov_age, cov_education, cov_occupation,
#   cov_civil_status, cov_children (Stata value labels).
# id: the row index of the .dta. The deposit's Cod_ind is reused across sessions within Italy
#   (126 codes carry two different people), so it is not an identifier.
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


import numpy as np  # noqa: E402
import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "dataverse_FSRV5D"
FNAME = "DatTrueCouples.dta"
COVS = {"country": "cov_country", "sex": "cov_sex", "Age": "cov_age", "Education": "cov_education",
        "Occupation": "cov_occupation", "civils": "cov_civil_status", "children": "cov_children"}
ITEMS = [f"D{i}" for i in range(1, 13)]


def derive_key(d: pd.DataFrame) -> dict:
    """Option per item that reproduces the deposited total exactly for every respondent."""
    x = d.dropna(subset=ITEMS + ["Raven"])
    X = np.column_stack([(x[c].values == k).astype(float) for c in ITEMS for k in range(1, 9)])
    coef = np.linalg.lstsq(X, x["Raven"].values, rcond=None)[0].reshape(12, 8)
    key = {c: int(np.argmax(coef[i]) + 1) for i, c in enumerate(ITEMS)}
    score = sum((x[c] == key[c]).astype(int) for c in ITEMS)
    assert (score == x["Raven"]).all(), "derived key does not reproduce the deposited total"
    return key


def main() -> None:
    d, m = pyreadstat.read_dta(dv_fetch("10.7910/DVN/FSRV5D", FNAME, RAW_DIR))
    assert len(d) == 1678 and (d["TrueCouple"] == 1).all()
    d["id"] = range(1, len(d) + 1)
    for c in ITEMS + [f"{c}t" for c in ITEMS] + ["Raven"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    key = derive_key(d)
    print("derived key:", key)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = pd.to_numeric(d[c], errors="coerce").astype("Int64")
    rows = []
    for c in ITEMS:
        sub = d.loc[d[c].notna(), ["id", c, f"{c}t", *covs]].copy()
        assert sub[c].between(1, 8).all(), c
        sub["item"] = c
        sub["resp"] = (sub[c] == key[c]).astype(int)
        sub["rt"] = sub[f"{c}t"].astype(float)
        rows.append(sub[["id", "item", "resp", "rt", *covs]])
    t = pd.concat(rows).sort_values(["id", "item"]).reset_index(drop=True)
    emit({"rapallini_2023_raven": (t, pv_for(ITEMS, (0, 1)))})


if __name__ == "__main__":
    main()
