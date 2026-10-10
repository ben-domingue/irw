#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.24955368.v2
# DOI: 10.6084/m9.figshare.24955368.v2 (dataset; the record names no paper)
#   Pinheiro, Francisco Pablo Huascar Aragão (2024). Datasets used to evaluate the
#   psychometric properties of the Negative Acts Questionnaire-Revised (NAQ-R). figshare.
# Data: sample1.csv and sample2.csv (5,074 Brazilian teachers each; total_sample.csv is
#       their concatenation, asserted below): the NAQ-R (n1-n22, 1-5) and the WHO
#       Self-Reporting Questionnaire (srq_1-srq_20, 0/1), with Portuguese-coded demographics.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. NAQ-R: rights (a `block` row in
#   itemtext/instrument_rights_register.csv). SRQ-20 ships with a WHO credit under the
#   register, but the deposit has codes only (srq_1 ..) and no questionnaire.
#
# Tables (item = the deposit's column name): pinheiro_2024_naqr (22, 1-5),
#   pinheiro_2024_srq20 (20, 0/1); cov_sample = 1 / 2 (the two split-half files).
# Covariates: cov_sample, cov_sex, cov_race, cov_education (edu_bg), cov_region,
#   cov_teaching_level (edu_levels), cov_age, cov_teaching_years.
# id: cov_sample * 10000 + row index within the sample file.

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

RAW_DIR = RAW_ROOT / "10_6084_m9_figshare_24955368_v2"
COVS = {"sex": "cov_sex", "race": "cov_race", "edu_bg": "cov_education", "region": "cov_region",
        "edu_levels": "cov_teaching_level", "age": "cov_age", "teaching_xp": "cov_teaching_years"}


def main() -> None:
    s1 = pd.read_csv(figshare_fetch(24955368, "sample1.csv", RAW_DIR))
    s2 = pd.read_csv(figshare_fetch(24955368, "sample2.csv", RAW_DIR))
    tot = pd.read_csv(figshare_fetch(24955368, "total_sample.csv", RAW_DIR))
    assert len(s1) == len(s2) == 5074 and len(tot) == 10148
    naq = [f"n{k}" for k in range(1, 23)]
    srq = [f"srq_{k}" for k in range(1, 21)]
    key = naq + srq + ["age", "teaching_xp"]
    both = pd.concat([s1, s2], ignore_index=True)
    assert both[key].sort_values(key).reset_index(drop=True).equals(
        tot[key].sort_values(key).reset_index(drop=True)), "total_sample is not sample1 + sample2"
    s1["cov_sample"], s2["cov_sample"] = 1, 2
    d = pd.concat([s1, s2], ignore_index=True)
    d["id"] = d["cov_sample"] * 10000 + d.groupby("cov_sample").cumcount() + 1
    d = d.rename(columns=COVS)
    d["cov_teaching_years"] = d["cov_teaching_years"].astype("Int64")
    covs = ["cov_sample"] + list(COVS.values())
    emit({"pinheiro_2024_naqr": (long(d, naq, covs, valid=range(1, 6)), pv_for(naq, range(1, 6))),
          "pinheiro_2024_srq20": (long(d, srq, covs, valid=(0, 1)), pv_for(srq, (0, 1)))})


if __name__ == "__main__":
    main()
