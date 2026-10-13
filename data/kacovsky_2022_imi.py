#!/usr/bin/env python3
# Source: https://zenodo.org/records/6394501
# DOI: 10.5281/zenodo.6394501 (dataset; the record names no paper)
#   Kacovsky, Petr (2022). DATASET associated with the research of students' intrinsic
#   motivation during practical work in physics [Dataset]. Zenodo.
# Data: data_IPL_1805_respondents.sav: 1,805 secondary-school students, 23 items of an
#       Intrinsic Motivation Inventory adaptation on a 1-7 scale where, per the record's
#       legend, 1 = the highest feeling and 7 = the lowest (reversed from the usual IMI
#       direction; shipped as stored). Column names carry the subscale: val value/usefulness,
#       ten tension, eff effort, pc perceived choice, int interest/enjoyment, com perceived
#       competence (item23_com, labelled "23_pc" in the file).
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped -- rights. The IMI is in the Center for Self-Determination Theory
#   library (a `block` row in itemtext/instrument_rights_register.csv); the file's variable
#   labels are positional ("1_val") and it has no value labels for the items.
#
# One table: kacovsky_2022_imi, item = the deposit's column name (item1_val ..), resp 1-7.
# Covariates: cov_gender (1 men, 2 women), cov_stem_intention (1 highest .. 7 lowest, stored
#   1-5), cov_diligence (self-reported, same direction, stored 1-5).
# id: row index of the .sav.

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

RAW_DIR = RAW_ROOT / "10_5281_zenodo_6394501"


def main() -> None:
    d, meta = pyreadstat.read_sav(str(zenodo_fetch(6394501, "data_IPL_1805_respondents.sav", RAW_DIR)))
    assert len(d) == 1805
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns={"gender": "cov_gender", "intention_to_study_STEM": "cov_stem_intention",
                          "self_reported_diligence": "cov_diligence"})
    covs = ["cov_gender", "cov_stem_intention", "cov_diligence"]
    for c in covs:
        d[c] = d[c].astype("Int64")
    items = [c for c in d.columns if c.startswith("item")]
    assert len(items) == 23
    emit({"kacovsky_2022_imi": (long(d, items, covs, valid=range(1, 8)), pv_for(items, range(1, 8)))})


if __name__ == "__main__":
    main()
