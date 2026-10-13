#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/XWRMAK
# DOI: 10.7910/DVN/XWRMAK (dataset; the record cites no paper DOI -- "Early adversity and
#   changes in cortisol and negative affect in response to interpersonal threats", IJERPH)
#   Wendel, Christopher (2022). Replication Data for Early adversity and changes in cortisol
#   and negative affect in response to interpersonal threats. Harvard Dataverse, V1.
# Data: "IJERPH ms data.sav": 161 participants of a laboratory interpersonal-threat study;
#       the Risky Families Questionnaire (rfq1-rfq10, 1-5; items 1, 3 and 6 marked
#       "*reverse scored" in the variable labels, shipped as stored) plus study factors.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Variable labels carry only the reverse-scoring flags; no value
#   labels on the items; the RFQ wording (Taylor et al. 2004) is not in the deposit.
#
# One table: wendel_2022_rfq, item = rfq1 .. rfq10, resp 1-5.
# Covariates: cov_sex (0 male, 1 female), cov_age, cov_parental_income (pinc code).
# id: the deposit's ID1.

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

import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "10_7910_dvn_xwrmak"


def main() -> None:
    d, meta = pyreadstat.read_sav(str(dv_fetch("10.7910/DVN/XWRMAK", "IJERPH ms data.sav", RAW_DIR)))
    assert len(d) == 161 and d["ID1"].is_unique
    d = d.rename(columns={"ID1": "id", "sex": "cov_sex", "age": "cov_age", "pinc": "cov_parental_income"})
    d["id"] = d["id"].astype(int)
    covs = ["cov_sex", "cov_age", "cov_parental_income"]
    for c in covs:
        d[c] = pd.to_numeric(d[c], errors="coerce").astype("Int64")
    items = [f"rfq{k}" for k in range(1, 11)]
    emit({"wendel_2022_rfq": (long(d, items, covs, valid=range(1, 6)), pv_for(items, range(1, 6)))})


if __name__ == "__main__":
    main()
