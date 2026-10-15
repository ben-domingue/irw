#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/jz6vbvv5t8
# DOI: 10.17632/jz6vbvv5t8 (dataset, 2026; Setsoafia, Essel & Tachie-Menson). "Dataset on Digital
#   Literacy, Creative Thinking Disposition, And Generative Artificial Intelligence Literacy as
#   Predictors of Academic Performance of Pre-service Visual Art Teachers in Ghana".
# Data: "S'FIA_DATASET103.xlsx" sheet SPDATASET, 258 Ghanaian pre-service visual-art teachers:
#       CTD_1-25 creative thinking disposition (1-5), GENAI_1-12 generative-AI literacy (1-7; the
#       R-prefixed names RGENAI_2, RGENAI_5, RGENA_11 mark reverse-worded items, kept as deposited),
#       DL_1-10 digital literacy (1-7; one DL_2 entry of 66 set missing), SDR_1-7 social desirability
#       (1-7). AP_1-4 (self-rated academic performance) and RVAR are not shipped.
# License: CC BY 4.0 (Mendeley Data).
#
# Item text: not shipped -- codes only, no instrument in the deposit.
#
# Tables: setsoafia_2026_ctd (25, 1-5), setsoafia_2026_genai_literacy (12, 1-7),
#   setsoafia_2026_digital_literacy (10, 1-7), setsoafia_2026_sdr (7, 1-7); 258 ids.
# Covariates: cov_age (0 -> missing), cov_gender (1/2), cov_academic_level (1-4), cov_cgpa,
#   cov_location (1/2).
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

import re  # noqa: E402

RAW_DIR = RAW_ROOT / "md_jz6vbvv5t8"
FNAME = "S'FIA_DATASET103.xlsx"


def main() -> None:
    d = pd.read_excel(mendeley_fetch("jz6vbvv5t8", FNAME, RAW_DIR), sheet_name="SPDATASET")
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == 258
    d["id"] = d.index + 1
    d["cov_age"] = d["Age"].replace(0, pd.NA).astype("Int64")
    d["cov_gender"] = d["Gender"].astype("Int64")
    d["cov_academic_level"] = d["Academic Level"].astype("Int64")
    d["cov_cgpa"] = d["CGPA"]
    d["cov_location"] = d["Location"].astype("Int64")
    covs = ["cov_age", "cov_gender", "cov_academic_level", "cov_cgpa", "cov_location"]
    ctd = [f"CTD_{i}" for i in range(1, 26)]
    gen = [c for c in d.columns if re.fullmatch(r"R?GENAI?_\d+", c)]
    dl = [f"DL_{i}" for i in range(1, 11)]
    sdr = [f"SDR_{i}" for i in range(1, 8)]
    assert len(gen) == 12
    assert (d["DL_2"] == 66).sum() == 1
    d.loc[d["DL_2"] == 66, "DL_2"] = pd.NA
    emit({"setsoafia_2026_ctd": (long(d, ctd, covs, valid=range(1, 6)), pv_for(ctd, range(1, 6))),
          "setsoafia_2026_genai_literacy": (long(d, gen, covs, valid=range(1, 8)), pv_for(gen, range(1, 8))),
          "setsoafia_2026_digital_literacy": (long(d, dl, covs, valid=range(1, 8)), pv_for(dl, range(1, 8))),
          "setsoafia_2026_sdr": (long(d, sdr, covs, valid=range(1, 8)), pv_for(sdr, range(1, 8)))})


if __name__ == "__main__":
    main()
