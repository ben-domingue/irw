#!/usr/bin/env python3
# Source: https://zenodo.org/records/20080845
# DOI: 10.5281/zenodo.20080845 (dataset, 2026; Atoum & Al-Adamat). "Exploring the Relationships Between
#   Mind Wandering, Academic Entitlement, and Cognitive Dissonance"; no paper DOI on the record.
# Data: Datax.xlsx sheet Data1, 308 Jordanian university students (Arabic deposit; header row 2 holds
#       the codes): c1-c18 cognitive dissonance (0/1; seven c1 cells of 2, off the 0/1 scale, set missing), m1-m12 mind
#       wandering (1-5), e1-e22 academic entitlement (1-5). cognitive1-6 / mw1-3 / ec1-7 and the totals
#       are the authors' subscale means.
# License: CC BY 4.0 (Zenodo).
#
# Item text: not shipped -- codes only, no instrument in the deposit (the ec* subscale headers carry
#   Arabic subscale names, not item stems).
#
# Tables: atoum_2026_cognitive_dissonance (308 x 18, 0/1), atoum_2026_mind_wandering (308 x 12, 1-5),
#   atoum_2026_academic_entitlement (308 x 22, 1-5).
# Covariates: cov_sex (1/2 as deposited), cov_college (1/2).
# id: row index.
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

RAW_DIR = RAW_ROOT / "zn_20080845"
FNAME = "Datax.xlsx"
CD = [f"c{i}" for i in range(1, 19)]
MW = [f"m{i}" for i in range(1, 13)]
AE = [f"e{i}" for i in range(1, 23)]


def main() -> None:
    d = pd.read_excel(zenodo_fetch(20080845, FNAME, RAW_DIR), sheet_name="Data1", header=1)
    d = d.rename(columns={"Sex": "cov_sex", "College": "cov_college"})
    assert len(d) == 308, len(d)
    d["id"] = d.index + 1
    for c in CD + MW + AE + ["cov_sex", "cov_college"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    assert (d["c1"] == 2).sum() == 7
    d.loc[d["c1"] == 2, "c1"] = pd.NA
    covs = ["cov_sex", "cov_college"]
    for c in covs:
        d[c] = d[c].astype("Int64")
    emit({"atoum_2026_cognitive_dissonance": (long(d, CD, covs, valid=(0, 1)), pv_for(CD, (0, 1))),
          "atoum_2026_mind_wandering": (long(d, MW, covs, valid=range(1, 6)), pv_for(MW, range(1, 6))),
          "atoum_2026_academic_entitlement": (long(d, AE, covs, valid=range(1, 6)), pv_for(AE, range(1, 6)))})


if __name__ == "__main__":
    main()
