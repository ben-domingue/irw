#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Burnout_Process_Questionnaire_MPLUS_kovariances_dat/20788174
# DOI: 10.6084/m9.figshare.20788174 (dataset, 2022; the record names no published paper)
#   Szigeti, R. (2022). Burnout Process Questionnaire_MPLUS_kovariances.dat. figshare.
# Data: adatok_618fo_3tetel nelkul_kovarianciakhoz.sav, 618 Hungarian teachers (recruited at
#       conferences, in-service training and 12 schools): kfk1-26 the Burnout Process
#       Questionnaire (Kiégés Folyamat Kérdőív, 0-4), mbi1-22 the Maslach Burnout Inventory
#       Educators Survey (0-6; 231 teachers), ces1-20 the CES-D (0-3), eri1-6 the ERI
#       overcommitment scale (0-3). The Hungarian stem is in each variable label; no value
#       labels on any item. The seven trailing columns are the authors' subscale means.
# License: CC BY 4.0 (figshare record).
#
# Item text: shipped for szigeti_2022_bpq, szigeti_2022_cesd (ship_with_note row in the rights
#   register) and szigeti_2022_eri_oc -- Hungarian stems from the variable labels, option_text
#   blank on every point because the file carries no value labels (checked both levels); IRW
#   English in item_text_translated. NOT shipped for szigeti_2022_mbi_es (MBI is a `block`
#   row). Built by automated_finding/itemtext_verification/make_itemtext_szigeti_2022.py.
#
# Tables: szigeti_2022_bpq (26, 0-4), szigeti_2022_mbi_es (22, 0-6), szigeti_2022_cesd (20,
#   0-3), szigeti_2022_eri_oc (6, 0-3); item = the deposit's column name.
# Covariates: cov_source (kod, 1 conference, 2 in-service training, 3-14 schools), cov_gender
#   (0 male, 1 female), cov_age (years), cov_partnered (1 single/divorced/widowed, 2 in a
#   relationship), cov_school_type (1 primary, 2 vocational secondary, 3 gimnázium, 4 other,
#   5 several), cov_weekly_hours.
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

RAW_DIR = RAW_ROOT / "figshare_20788174"
FNAME = "adatok_618fo_3tetel nelkul_kovarianciakhoz.sav"
COVS = {"kod": "cov_source", "Nem": "cov_gender", "Kor": "cov_age", "csaladibinaris": "cov_partnered",
        "isktipus": "cov_school_type", "Hetiora": "cov_weekly_hours"}
BLOCKS = {"szigeti_2022_bpq": ([f"kfk{i}" for i in range(1, 27)], range(0, 5)),
          "szigeti_2022_mbi_es": ([f"mbi{i}" for i in range(1, 23)], range(0, 7)),
          "szigeti_2022_cesd": ([f"ces{i}" for i in range(1, 21)], range(0, 4)),
          "szigeti_2022_eri_oc": ([f"eri{i}" for i in range(1, 7)], range(0, 4))}


def stems(table: str) -> list:
    """(code, Hungarian stem) from the .sav variable labels; the leading item number is dropped."""
    import re
    _, meta = pyreadstat.read_sav(str(figshare_fetch(20788174, FNAME, RAW_DIR)), metadataonly=True)
    return [(c, re.sub(r"^\d+\.\s*", "", meta.column_names_to_labels[c]).strip()) for c in BLOCKS[table][0]]


def main() -> None:
    d, meta = pyreadstat.read_sav(str(figshare_fetch(20788174, FNAME, RAW_DIR)))
    assert len(d) == 618
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        if c != "cov_weekly_hours":  # fractional hours occur
            d[c] = d[c].astype("Int64")
    emit({t: (long(d, items, covs, valid=valid), pv_for(items, valid)) for t, (items, valid) in BLOCKS.items()})


if __name__ == "__main__":
    main()
