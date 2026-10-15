#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Illusion_of_Literacy_-_Dataset_and_Model/32668896
# DOI: 10.6084/m9.figshare.32668896 (dataset, 2026; the record names no published paper)
#   Dhammapeera, P. (2026). Illusion of Literacy - Dataset and Model [for "The illusion of
#   literacy: how generative AI dependency undermines mental health literacy, amplifies stigma,
#   and deters help-seeking"]. figshare.
# Data: Dataset - Illusion of Literacy.sav, 668 Thai GenAI users (online survey, Thai
#       administration): GAID1-11 generative-AI dependency (1-5), MHL1-16 mental health
#       literacy (0-4), MHSAS1-9 Mental Help Seeking Attitudes Scale (semantic differential
#       stored 1-7 for -3..+3), SASS1-12 stigma of seeking help (0-4; self- and other-stigma).
#       The *_R reversed copies and the scale scores are not shipped.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped -- variable labels repeat the code ("GAID1"); value labels hold only
#   the Thai anchors (option text without stems is not shipped, irw#1770). Stems are not in
#   the deposit (only an AMOS model file accompanies the data).
#
# Tables: dhammapeera_2026_gaid (11, 1-5), dhammapeera_2026_mhl (16, 0-4),
#   dhammapeera_2026_mhsas (9, 1-7 as deposited), dhammapeera_2026_sass (12, 0-4).
# Covariates: cov_age (years; a text column in the file, coerced), cov_gender (1 female, 2 male,
#   3 undisclosed, 4 other), cov_education (1-7), cov_region (1-7), cov_employment (1-8),
#   cov_genai_frequency (1 several times a day .. 4).
# id: row index (no respondent identifier in the file).
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

RAW_DIR = RAW_ROOT / "figshare_32668896"
FNAME = "Dataset - Illusion of Literacy.sav"
COVS = {"Age": "cov_age", "Gender": "cov_gender", "Edu_": "cov_education", "Living_": "cov_region",
        "Status_": "cov_employment", "Freq_": "cov_genai_frequency"}
BLOCKS = {"dhammapeera_2026_gaid": ([f"GAID{i}" for i in range(1, 12)], range(1, 6)),
          "dhammapeera_2026_mhl": ([f"MHL{i}" for i in range(1, 17)], range(0, 5)),
          "dhammapeera_2026_mhsas": (["MHSAS1", "MHSAS2_", "MHSAS3", "MHSAS4", "MHSAS5_", "MHSAS6_", "MHSAS7",
                                      "MHSAS8_", "MHSAS9_"], range(1, 8)),
          "dhammapeera_2026_sass": ([f"SASS{i}" for i in range(1, 13)], range(0, 5))}


def main() -> None:
    d, meta = pyreadstat.read_sav(str(figshare_fetch(32668896, FNAME, RAW_DIR)))
    assert len(d) == 668
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    d["cov_age"] = pd.to_numeric(d["cov_age"], errors="coerce")
    for c in covs:
        d[c] = d[c].astype("Int64")
    out = {}
    for t, (items, valid) in BLOCKS.items():
        rename = {c: c.rstrip("_") for c in items}
        out[t] = (long(d, items, covs, valid=valid, rename=rename), pv_for(rename.values(), valid))
    emit(out)


if __name__ == "__main__":
    main()
