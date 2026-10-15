#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/33716635
# DOI: 10.6084/m9.figshare.33716635.v1 (dataset, 2026-09-13; de Oliveira, Isabela; Laus, Maria Fernanda;
#   Braga Costa, Telma Maria; Almeida, Sebastiao). "Weight bias internalization, healthcare-related
#   experiences and experienced weight stigma across Body Mass Index categories in Brazilian adults".
# Data: "Dataset.xlsx", sheet Data: 384 Brazilian adults (REDCap): WBIS_2-WBIS_11 = ten items of the
#       Modified Weight Bias Internalization Scale (WBIS-M, Brazilian adaptation; 1-7; item 1 is not
#       in the file), experiences_2-13 = an inventory of healthcare experiences and weight-stigma
#       experiences with item-specific option sets (text values in the data, codes in sheet Codebook).
#       Weight/height/BMI and demographics are free text or numeric.
# License: CC BY 4.0 (figshare).
#
# Item text: healthcare_experiences shipped from sheet Codebook (English stems and option labels keyed
#   by column name; the study was administered in Portuguese and the deposit carries only the English
#   codebook wording, so item_text/option_text are blank and the English sits in the _translated
#   columns with language = Portuguese). WBIS not shipped: codes only in the file (the WBIS-M wording
#   is in the cited PLOS ONE adaptation paper, one hop away).
#
# Tables: oliveira_2026_wbis (10 items, 1-7, codes wbis_2..wbis_11 as deposited),
#   oliveira_2026_healthcare_experiences (11 items, codes from the codebook: experiences_2 1-4,
#   experiences_3 1-5, experiences_4 0/1, experiences_5 1 yes/2 no, experiences_6-8 1-4,
#   experiences_9 1-5, experiences_11-13 1-4); 384 ids (row index; record_id not carried).
# Covariates: cov_age, cov_gender (1 female, 2 male, 3 other), cov_marital (1 single, 2 stable union,
#   3 married, 4 divorced, 5 separated, 6 widowed), cov_skin_color (1 white, 2 brown, 3 black,
#   4 yellow/Asian, 5 indigenous), cov_income (1 <1 MW, 2 1-3, 3 4-5, 4 >5 minimum wages), cov_bmi.
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


def dans_fetch(doi: str, fname: str, raw_dir: Path) -> Path:
    """Download one original-format file of a DANS Data Station (Dataverse) dataset."""
    return dv_fetch(doi, fname, raw_dir, host="ssh.datastations.nl")
RAW_DIR = RAW_ROOT / "C_70_33716635"
FNAME = "Dataset.xlsx"
WBIS = [f"WBIS_{i}" for i in range(2, 12)]
EXP = [f"experiences_{i}" for i in (2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13)]


def codebook():
    """{column: (stem, {code: label})} from sheet Codebook (headerless; row 0 is experiences_2)."""
    cb = pd.read_excel(figshare_fetch(33716635, FNAME, RAW_DIR), sheet_name="Codebook", header=None)
    out = {}
    for _, r in cb.iterrows():
        stem = str(r[1]).strip()
        stem = stem.split(":", 1)[1].strip().strip('"') if ":" in stem else stem
        opts = {}
        for part in str(r[3]).split(";"):
            k, v = part.split("=", 1)
            opts[int(k)] = v.strip()
        out[str(r[0]).strip()] = (stem, opts)
    assert set(out) == set(EXP), set(out) ^ set(EXP)
    return out


def main() -> None:
    d = pd.read_excel(figshare_fetch(33716635, FNAME, RAW_DIR), sheet_name="Data")
    assert len(d) == 384
    d["id"] = d.index + 1
    d["cov_age"] = d["Age"].astype("Int64")
    d["cov_gender"] = d["Gender"].map({"Female": 1, "Male": 2, "Other": 3}).astype("Int64")
    d["cov_marital"] = d["Marital_status"].map({"Single": 1, "Stable union": 2, "Married": 3, "Divorced": 4,
                                                "Separated": 5, "Widowed": 6}).astype("Int64")
    d["cov_skin_color"] = d["Skin_color"].map({"White": 1, "Brown": 2, "Black": 3, "Yellow/Asian": 4,
                                               "Indigenous": 5}).astype("Int64")
    inc = {v: i + 1 for i, v in enumerate(["Less than 1 minimum wage", "1 to 3 minimum wages",
                                           "4 to 5 minimum wages", "More than 5 minimum wages"])}
    d["cov_income"] = d["Income"].map(inc).astype("Int64")
    assert d["cov_income"].notna().all(), d["Income"].unique()
    d["cov_bmi"] = d["BMI"].round(2)
    covs = ["cov_age", "cov_gender", "cov_marital", "cov_skin_color", "cov_income", "cov_bmi"]
    assert d[covs].notna().all().all()
    cb = codebook()
    for c in EXP:
        inv = {v.lower(): k for k, v in cb[c][1].items()}
        d[c] = d[c].astype(str).str.strip().str.lower().map(inv)
        assert d[c].notna().all(), (c, d[c].isna().sum())
    ren = {c: c.lower() for c in WBIS}
    tw = long(d, WBIS, covs, valid=range(1, 8), rename=ren)
    te = long(d, EXP, covs)
    pv_e = {c: set(cb[c][1]) for c in EXP}
    for c in EXP:
        assert set(te.loc[te["item"] == c, "resp"]) <= pv_e[c], c
    emit({"oliveira_2026_wbis": (tw, pv_for(ren.values(), range(1, 8))),
          "oliveira_2026_healthcare_experiences": (te, pv_e)})


if __name__ == "__main__":
    main()
