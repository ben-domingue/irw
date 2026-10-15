#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Working_conditions_and_burnout_among_elementary_school_teachers_The_moderating_influence_of_work_settings/32359092
# DOI: 10.6084/m9.figshare.32359092 (dataset, 2026; Timbreza, Candace Aila). The record names no paper DOI.
# Data: "Working Conditions and Burnout - DATA.xlsx" sheet Valid, 231 elementary-school teachers in
#       Northern Luzon, Philippines; second header row holds the codes. North Carolina Teacher Working
#       Conditions Survey WCT1-8 WCF9-16 WCC17-24 WCM25-32 WCL33-40 WCS41-48 WCP49-56 WCI57-64 (64
#       items, 1-4; one WCP56 entry of 44 set missing) and MBI-ES "B1 (EE)" .. "B22 (DP)" (22 items, 0-6). Sum/Ave/SD columns are the
#       authors' scores.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped -- codes only; the NCTWCS and MBI-ES wording is not in the deposit (MBI is
#   blocked in the rights register in any case).
#
# Tables: timbreza_2026_nctwcs (231 x 64, 1-4), timbreza_2026_mbi_es (231 x 22, 0-6; item = B01_EE ..
#   B22_DP, the header "B1 (EE)" with the subscale tag kept).
# Covariates: cov_age, cov_sex, cov_civil_status, cov_ses, cov_work_setting (Public/Private),
#   cov_employment_status (labels as deposited, whitespace stripped).
# id: participant code P1..P231 -> integer.
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

import re  # noqa: E402

RAW_DIR = RAW_ROOT / "fs_32359092"
FNAME = "Working Conditions and Burnout - DATA.xlsx"


def main() -> None:
    x = pd.read_excel(figshare_fetch(32359092, FNAME, RAW_DIR), sheet_name="Valid", header=None)
    d = x.iloc[2:].copy()
    d.columns = [str(c).strip() for c in x.iloc[1]]
    d = d.reset_index(drop=True)
    assert len(d) == 231
    d["id"] = d["Participant Code."].str.extract(r"P(\d+)")[0].astype(int)
    assert d["id"].is_unique
    covs = {"Age": "cov_age", "Sex": "cov_sex", "Civil Status": "cov_civil_status", "SES": "cov_ses",
            "Work Setting": "cov_work_setting", "Employment Status": "cov_employment_status"}
    d = d.rename(columns=covs)
    for c in covs.values():
        d[c] = d[c].astype(str).str.strip()
    d["cov_age"] = pd.to_numeric(d["cov_age"], errors="coerce").astype("Int64")
    wc = [c for c in d.columns if re.fullmatch(r"WC[A-Z]\d+", c)]
    mbi = [c for c in d.columns if re.fullmatch(r"B\d+ \([A-Z]+\)", c)]
    assert len(wc) == 64 and len(mbi) == 22
    for c in wc + mbi:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    assert (d["WCP56"] == 44).sum() == 1
    d.loc[d["WCP56"] == 44, "WCP56"] = pd.NA  # one off-scale entry (typo), set missing
    ren = {c: f"B{int(re.match(r'B(\d+)', c).group(1)):02d}_{re.search(r'\((\w+)\)', c).group(1)}" for c in mbi}
    cv = list(covs.values())
    emit({"timbreza_2026_nctwcs": (long(d, wc, cv, valid=range(1, 5)), pv_for(wc, range(1, 5))),
          "timbreza_2026_mbi_es": (long(d, mbi, cv, valid=range(0, 7), rename=ren), pv_for(ren.values(), range(0, 7)))})


if __name__ == "__main__":
    main()
