#!/usr/bin/env python3
# Source: https://zenodo.org/records/5023051
# DOI: 10.5281/zenodo.5023051 (dataset, 2018; Liuzza, Marco Tullio; Lindholm, Torun; Hawley, Caitlin B.;
#   Gustafsson Sendén, Marie; Ekström, Ingrid; Olsson, Mats J.; Olofsson, Jonas K.). Data from "Body odour
#   disgust sensitivity predicts authoritarian attitudes" (Royal Society Open Science, 2018,
#   10.1098/rsos.171091). Three online samples of US adults (Study 1 n = 201, Study 2 n = 159, Study 3 n = 391).
# Data: Study1_raw.csv, Study2_raw.csv, Study3_raw.csv (README.txt is the codebook). BODS = Body Odour Disgust
#       Sensitivity scale (12 items, 1-5; all studies), RWA = Right-Wing Authoritarianism (15 items, 1-7; all
#       studies), TDD = Three Domain Disgust Scale (21 items, 1-7, Study 1; a 7-item subset labelled TDD1-TDD7 in
#       Study 2 whose mapping to the 21 is not documented, shipped as its own table), DSS = Disgust Scale-Revised
#       (27 items, 1-5, Study 2; DSS12_C and DSS16_C are the catch items, not shipped), PVD = Perceived
#       Vulnerability to Disease (15 items, Study 2, stored as 19-25 -- a 7-point scale with an export offset,
#       shipped as stored), SDO = Social Dominance Orientation (16 items, 1-7, Study 3). The README says the
#       suffix _R "means that that item must be reverse scored", i.e. the values are as answered.
# License: CC0 1.0 (Zenodo).
#
# Item text: not shipped -- the CSVs carry codes only and the README names the instruments, not the items.
#
# Tables: liuzza_2018_bods (12, N = 751), liuzza_2018_rwa (15, N = 751), liuzza_2018_tdds (21, Study 1),
#   liuzza_2018_tdds_short (7, Study 2), liuzza_2018_dsr (25, Study 2), liuzza_2018_pvd (15, Study 2),
#   liuzza_2018_sdo (16, Study 3).
# Covariates: cov_study (1/2/3), cov_gender (M/F), cov_age, cov_education (1 no school .. 10 PhD); Study 1 also
#   cov_moral_liberalism, cov_social_liberalism, cov_fiscal_liberalism; Study 3 cov_right (left-right
#   self-placement) and cov_conservative.
# id: 1000 * study + row index within the study file.
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
import re

RAW_DIR = RAW_ROOT / "zenodo_5023051"


def load(study: int) -> pd.DataFrame:
    d = pd.read_csv(zenodo_fetch(5023051, f"Study{study}_raw.csv", RAW_DIR))
    d = d.rename(columns={"Gender": "GENDER", "Age": "AGE"})
    d["id"] = 1000 * study + pd.RangeIndex(1, len(d) + 1)
    d["cov_study"] = study
    d["cov_gender"] = d["GENDER"]
    d["cov_age"] = d["AGE"]
    d["cov_education"] = d["EDU"]
    return d


def block(d: pd.DataFrame, prefix: str) -> list:
    return [c for c in d.columns if re.fullmatch(rf"{prefix}\d+(_R)?", c)]


def main() -> None:
    s1, s2, s3 = load(1), load(2), load(3)
    assert (len(s1), len(s2), len(s3)) == (201, 159, 391)
    base = ["cov_study", "cov_gender", "cov_age", "cov_education"]
    for k, v in {"cov_moral_liberalism": "MOR_IDEO", "cov_social_liberalism": "SOC_IDEO",
                 "cov_fiscal_liberalism": "FIS_IDEO"}.items():
        s1[k] = s1[v]
    s3["cov_right"] = s3["Right"]
    s3["cov_conservative"] = s3["Conservaive"]
    pooled = pd.concat([s1, s2, s3], ignore_index=True)
    bods, rwa = block(s1, "BODS"), block(s1, "RWA")
    assert bods == block(s2, "BODS") == block(s3, "BODS") and rwa == block(s2, "RWA") == block(s3, "RWA")
    tdd1, tdd2 = block(s1, "TDD"), block(s2, "TDD")
    dss = [c for c in s2.columns if re.fullmatch(r"DSS\d+(_R)?", c)]
    pvd, sdo = block(s2, "PVD"), block(s3, "SDO")
    assert (len(bods), len(rwa), len(tdd1), len(tdd2), len(dss), len(pvd), len(sdo)) == (12, 15, 21, 7, 25, 15, 16)
    c1 = base + ["cov_moral_liberalism", "cov_social_liberalism", "cov_fiscal_liberalism"]
    c3 = base + ["cov_right", "cov_conservative"]
    r5, r7 = range(1, 6), range(1, 8)
    emit({"liuzza_2018_bods": (long(pooled, bods, base, valid=r5), pv_for(bods, r5)),
          "liuzza_2018_rwa": (long(pooled, rwa, base, valid=r7), pv_for(rwa, r7)),
          "liuzza_2018_tdds": (long(s1, tdd1, c1, valid=r7), pv_for(tdd1, r7)),
          "liuzza_2018_tdds_short": (long(s2, tdd2, base, valid=r7), pv_for(tdd2, r7)),
          "liuzza_2018_dsr": (long(s2, dss, base, valid=r5), pv_for(dss, r5)),
          "liuzza_2018_pvd": (long(s2, pvd, base, valid=range(19, 26)), pv_for(pvd, range(19, 26))),
          "liuzza_2018_sdo": (long(s3, sdo, c3, valid=r7), pv_for(sdo, r7))})


if __name__ == "__main__":
    main()
