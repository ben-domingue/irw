#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/interest_and_willingness_to_communicate/32052984
# DOI: 10.6084/m9.figshare.32052984 (dataset, 2026; Wang, Juan). "These are the original dataset collected from
#   primary school students (grade 3-6)" -- Chinese primary-school EFL learners, 399 rows per file.
# Data: inclass WTC.xlsx (Q1-Q22, 1-5), OUTCLASS WTC.xlsx (Q1-Q25, 1-5; one Q6 cell of 54 and one Q8 cell of 6
#       are out of range and dropped), INTEREST.xlsx (Q2-Q17, 1-5; the ZQ* columns are z-scores, not shipped).
#       The two WTC files share their NAME column row for row; the INTEREST file does not, and NAME is a
#       within-class number (1-127, 272 duplicates), so the files cannot be linked and ship as three independent
#       tables with their own row-index ids. GRADE and Gender exist only in INTEREST.xlsx (Gender carries a few
#       3/4/5 codes the deposit does not explain, shipped as stored).
# License: CC BY 4.0 (figshare).
#
# Item text: not shipped -- the workbooks carry Q-codes only; the (Chinese) instruments are not in the deposit.
#
# Tables: wang_2026_wtc_inclass (22), wang_2026_wtc_outclass (25), wang_2026_interest (16).
# Covariates: cov_grade, cov_gender (interest table only).
# id: row index per file (not linkable across files).
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


def osf_fetch(node: str, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://api.osf.io/v2/nodes/{node}/files/osfstorage/", headers=UA, timeout=120).json()
        url = [f["links"]["download"] for f in j["data"] if f["attributes"]["name"] == fname][0]
        download(url, p)
    return p

RAW_DIR = RAW_ROOT / "figshare_32052984"


def main() -> None:
    a = pd.read_excel(figshare_fetch(32052984, "inclass WTC.xlsx", RAW_DIR))
    b = pd.read_excel(figshare_fetch(32052984, "OUTCLASS WTC.xlsx", RAW_DIR))
    c = pd.read_excel(figshare_fetch(32052984, "INTEREST.xlsx", RAW_DIR))
    assert len(a) == len(b) == len(c) == 399 and (a["NAME"].values == b["NAME"].values).all()
    assert a["NAME"].duplicated().any(), "NAME is not a person id"
    for df in (a, b, c):
        df["id"] = range(1, len(df) + 1)
    c["cov_grade"] = c["GRADE"]
    c["cov_gender"] = c["Gender"]
    qa = [x for x in a.columns if x.startswith("Q")]
    qb = [x for x in b.columns if x.startswith("Q")]
    qc = [x for x in c.columns if x.startswith("Q") and not x.startswith("ZQ")]
    assert (len(qa), len(qb), len(qc)) == (22, 25, 16)
    oor = ~b[qb].isin([1, 2, 3, 4, 5]) & b[qb].notna()
    assert oor.sum().sum() == 2, oor.sum().sum()
    b[qb] = b[qb].mask(oor)
    r = range(1, 6)
    emit({"wang_2026_wtc_inclass": (long(a, qa, [], valid=r), pv_for(qa, r)),
          "wang_2026_wtc_outclass": (long(b, qb, [], valid=r), pv_for(qb, r)),
          "wang_2026_interest": (long(c, qc, ["cov_grade", "cov_gender"], valid=r), pv_for(qc, r))})


if __name__ == "__main__":
    main()
