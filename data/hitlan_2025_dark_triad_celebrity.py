#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/E9WMPW
# DOI: 10.7910/DVN/E9WMPW (dataset; the record cites "The Dark Triad, Emotional Regulation,
#   and Celebrity Admiration" without a DOI)
#   Hitlan, R. (2025). Replication Data for: Dark Triad 2025. Harvard Dataverse, V1.
# Data: Dark_Triad_recoded_Repository.sav (format=original): 264 US undergraduates at four
#       universities (Qualtrics, Jan-Apr 2025) with the 16-item DERS-16 (1-5), the Dirty Dozen
#       Dark Triad (12 x 1-9) and an 8-item celebrity-attitude block (1-5). The record says
#       "select cas_08=0 and run": cas_8 flags 17 respondents who failed attention checks
#       ("cas4 or cas5"), so those 17 and one with cas_8 missing are dropped (246 ids ship).
#       Composite columns (emotion and triad are the block means, checked; Catt/Cattheal/
#       Cattunh, mach, psycho, narc, lgpsycho, lgunheal are subset scores) are not shipped.
# License: CC0 1.0 (Dataverse record).
#
# Item text: shipped for all three tables -- the SPSS variable labels hold the Qualtrics
#   instruction text and the stem ("<instructions> - <stem>"), split on the last " - ", and
#   the value labels hold the anchors. Both label levels checked and complete.
#
# Tables: hitlan_2025_ders16 (246 x 16, 1-5), hitlan_2025_dirty_dozen (246 x 12, 1-9),
#   hitlan_2025_celebrity_attitude (246 x 8, 1-5).
# Covariates: cov_age, cov_sex, cov_gender, cov_ethnicity, cov_relationship_status,
#   cov_location (SPSS value labels). The free-text "other" columns are not shipped.
# id: the row index of the .sav (no id column in the deposit).
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

RAW_DIR = RAW_ROOT / "dataverse_E9WMPW"
FNAME = "Dark_Triad_recoded_Repository.sav"
COVS = {"age": "cov_age", "sex_": "cov_sex", "gender": "cov_gender", "ethnicity": "cov_ethnicity",
        "relatstatus": "cov_relationship_status", "location": "cov_location"}
BLOCKS = {
    "hitlan_2025_ders16": ("EmReg", 16, range(1, 6), "emotion"),
    "hitlan_2025_dirty_dozen": ("DT", 12, range(1, 10), "triad"),
    "hitlan_2025_celebrity_attitude": ("celeb", 8, range(1, 6), None),
}


def read():
    return pyreadstat.read_sav(dv_fetch("10.7910/DVN/E9WMPW", FNAME, RAW_DIR))


def labels(block: str):
    """(code, instructions, stem, value labels) per item, split from the .sav variable label."""
    _, m = read()
    _, n, _, _ = next(v for v in BLOCKS.values() if v[0] == block)
    out = []
    for i in range(1, n + 1):
        c = f"{block}_{i}"
        instr, stem = m.column_names_to_labels[c].rsplit(" - ", 1)
        out.append((c, instr.strip(), stem.strip(), m.variable_value_labels[c]))
    return out


def main() -> None:
    d, m = read()
    assert len(d) == 264
    d["id"] = range(1, len(d) + 1)
    d = d[d["cas_8"] == 0].copy()
    assert len(d) == 246
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    tables = {}
    for name, (block, n, valid, comp) in BLOCKS.items():
        items = [f"{block}_{i}" for i in range(1, n + 1)]
        if comp:   # emotion and triad are the block means; Catt is a subset score, not checked
            ok = d[items].notna().all(axis=1)
            assert ((d.loc[ok, items].mean(axis=1) - d.loc[ok, comp]).abs() < 1e-6).mean() > 0.98, comp
        tables[name] = (long(d, items, covs, valid=valid), pv_for(items, valid))
    emit(tables)


if __name__ == "__main__":
    main()
