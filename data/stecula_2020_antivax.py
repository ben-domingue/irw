#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/NLDDK8
# DOI: 10.7910/DVN/NLDDK8 (dataset). Paper: Stecula DA, Kuru O, Jamieson KH (2020). How
#   Trust in Experts and Media Use Affect Acceptance of Common Anti-Vaccination Claims.
#   Harvard Kennedy School Misinformation Review 1(1).
# Data: stecula_kuru_jamieson_replication_data.dta: 4,011 US adults (Annenberg Science
#       Knowledge survey panel; `sample` = panel vs control); four anti-vaccination claims
#       rated for accuracy (0 very inaccurate .. 3 very accurate) at two waves, T4
#       (antivax1-4_t4, n=2,771) and T6 (antivax1-4_t6, n=1,924): 1 autism, 2 toxins,
#       3 delay, 4 natural immunity (the variable labels).
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Variable labels are topic tags ("Antivax - Autism"), not the
#   claim wording; value labels give the four anchors. The claims are in the article.
#
# One table: stecula_2020_antivax, item = antivax1 .. antivax4, wave = 4 / 6 (the survey's
#   own wave numbers), resp 0-3.
# Covariates: cov_sample (0 control, 1 panel), cov_female, cov_education (1-6), cov_age,
#   cov_party (1 strong GOP .. 7 strong Dem), cov_religiosity (1-4).
# id: row index of the .dta (the file has no respondent id).

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

RAW_DIR = RAW_ROOT / "10_7910_dvn_nlddk8"
FNAME = "stecula_kuru_jamieson_replication_data.dta"
COVS = {"sample": "cov_sample", "female": "cov_female", "education": "cov_education", "age2": "cov_age",
        "party": "cov_party", "religiosity": "cov_religiosity"}


def main() -> None:
    d, meta = pyreadstat.read_dta(str(dv_fetch("10.7910/DVN/NLDDK8", FNAME, RAW_DIR)))
    assert len(d) == 4011
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = pd.to_numeric(d[c], errors="coerce").astype("Int64")
    parts = []
    for w in (4, 6):
        cols = {f"antivax{k}_t{w}": f"antivax{k}" for k in range(1, 5)}
        x = d[d[list(cols)].notna().any(axis=1)].copy()
        x["wave"] = w
        parts.append(long(x, list(cols), covs, valid=range(0, 4), extra=("wave",), rename=cols))
    t = pd.concat(parts, ignore_index=True)[["id", "item", "resp", "wave"] + covs]
    emit({"stecula_2020_antivax": (t, pv_for([f"antivax{k}" for k in range(1, 5)], range(0, 4)))})


if __name__ == "__main__":
    main()
