#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/K643HB
# DOI: 10.7910/DVN/K643HB (dataset; the record names no published paper)
#   Hou, Y. (2022). A dataset on the relationship between the Dark Triad and Cyberbullying in
#   college students. Harvard Dataverse, V1.
# Data: 原始数据.sav (format=original): 762 Chinese college students (16-23, offline paper
#       survey) with six self-report blocks: Dirty Dozen Dark Triad (DT, 12 x 1-7), IRI
#       perspective taking (PT, 5 x 1-5), moral disengagement (MD, 8 x 1-7), trait anger
#       (TA, 10 x 1-4), online disinhibition (OD, 11 x 1-4) and cyberbullying perpetration
#       (CB, 12 x 1-5). The composite columns (CB, MD, OD, PT, DT, Mach, Nar, Psy) are the
#       block sums (checked) and are not shipped.
# License: CC0 1.0 (Dataverse record).
#
# Item text: shipped for PT, TA, OD, CB (SPSS variable labels carry the Chinese stems; value
#   labels carry the anchors). Checked both label levels: the variable label of item 1 in each
#   block holds the block's instruction text and is cut off before the stem (SPSS 40-byte
#   truncation), so PT_1, TA_1, OD_1, CB_1 ship with instructions but blank item_text. The DT
#   and MD variable labels are truncated after ~10 characters for every item beyond the first
#   two, so those two tables ship no item text (value labels present on all items).
#
# Tables: hou_2022_dirty_dozen (762 x 12, 1-7), hou_2022_perspective_taking (762 x 5, 1-5),
#   hou_2022_moral_disengagement (762 x 8, 1-7), hou_2022_trait_anger (762 x 10, 1-4),
#   hou_2022_online_disinhibition (762 x 11, 1-4), hou_2022_cyberbullying (762 x 12, 1-5).
# Covariates: cov_sex, cov_age, cov_grade, cov_hometown, cov_only_child (SPSS value labels).
# id: the deposit's 序号 (index) column.
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

RAW_DIR = RAW_ROOT / "dataverse_K643HB"
FNAME = "原始数据.sav"
COVS = {"sex": "cov_sex", "age": "cov_age", "grade": "cov_grade", "hometown": "cov_hometown",
        "only_children": "cov_only_child"}
BLOCKS = {
    "hou_2022_dirty_dozen": ("DT", 12, range(1, 8)),
    "hou_2022_perspective_taking": ("PT", 5, range(1, 6)),
    "hou_2022_moral_disengagement": ("MD", 8, range(1, 8)),
    "hou_2022_trait_anger": ("TA", 10, range(1, 5)),
    "hou_2022_online_disinhibition": ("OD", 11, range(1, 5)),
    "hou_2022_cyberbullying": ("CB", 12, range(1, 6)),
}


def read():
    return pyreadstat.read_sav(dv_fetch("10.7910/DVN/K643HB", FNAME, RAW_DIR))


def labels(block: str):
    """(code, variable label, value labels) per item of a block, straight from the .sav."""
    _, m = read()
    _, n, _ = next(v for v in BLOCKS.values() if v[0] == block)
    return [(f"{block}_{i}", m.column_names_to_labels.get(f"{block}_{i}"),
             m.variable_value_labels.get(f"{block}_{i}")) for i in range(1, n + 1)]


def main() -> None:
    d, m = read()
    assert len(d) == 762 and d["index"].is_unique
    d["id"] = d["index"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        if c != "cov_age":
            d[c] = d[c].astype(int)
    d["cov_age"] = d["cov_age"].astype(int)
    tables = {}
    for name, (block, n, valid) in BLOCKS.items():
        items = [f"{block}_{i}" for i in range(1, n + 1)]
        if block in d:   # CB, MD, OD, PT, DT carry block sums; TA has none
            assert (d[items].sum(axis=1) == d[block]).all(), block
        tables[name] = (long(d, items, covs, valid=valid), pv_for(items, valid))
    emit(tables)


if __name__ == "__main__":
    main()
