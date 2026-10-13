#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/6sg3x4bchj
# DOI: 10.17632/6sg3x4bchj (dataset; the record names no published paper)
#   Güleç, S., & Yılmaz, Y. (2023). Post-Traumatic Stress Disorder (PTSD) Development in the
#   Aftermath of the Turkey Earthquake: Exploring the Role of Demographic Variables,
#   Personality Traits, and Psychological Vulnerability. Mendeley Data, V1.
# Data: "deprem 22.10. yüklenen veri seti.sav": 503 survivors of the 6 February 2023 Turkey
#       earthquake, surveyed in the third month after it (Turkish): Ten-Item Personality
#       Inventory (10 x 1-7), PTSD Checklist for DSM-5 (TSSB1-20, 0-4) and the Psychological
#       Vulnerability Scale (PKÖ1-6, 1-5). The composite columns (PTSD, five TIPI traits,
#       vulnerability) are block sums (checked) and are not shipped.
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: not shipped. Checked both label levels: no variable labels on any column; value
#   labels present on every item but they are only the Turkish anchors (hiç .. aşırı). The
#   Turkish TIPI / PCL-5 / PVS stems are not in the deposit.
#
# Tables: gulec_2023_tipi (503 x 10, 1-7; item codes are the deposit's trait.k headers),
#   gulec_2023_pcl5 (503 x 20, 0-4), gulec_2023_pvs (503 x 6, 1-5; codes PKO1-6 are the
#   deposit's PKÖ1-6 with the diaeresis dropped).
# Covariates (SPSS value labels, Turkish): cov_age, cov_gender, cov_marital, cov_income,
#   cov_education, cov_employment, cov_physical_illness, cov_psychiatric_illness,
#   cov_home_damage, cov_injured, cov_life_risk, cov_lost_relative, cov_witnessed_injury,
#   cov_witnessed_death, cov_prior_disaster, cov_prior_life_risk.
# id: the row index of the .sav (no id column in the deposit).
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

RAW_DIR = RAW_ROOT / "mendeley_6sg3x4bchj"
FNAME = "deprem 22.10. yüklenen veri seti.sav"
COVS = {"yas": "cov_age", "cinsiyet": "cov_gender", "medendur": "cov_marital", "gelirdüzeyi": "cov_income",
        "egitmdüz": "cov_education", "calısdur": "cov_employment", "bedenselhas": "cov_physical_illness",
        "psikiyathas": "cov_psychiatric_illness", "hasardurum": "cov_home_damage", "fizyaralanma": "cov_injured",
        "hayatirisk": "cov_life_risk", "yakınınıkaybet": "cov_lost_relative", "basyaralansahit": "cov_witnessed_injury",
        "basölümsahit": "cov_witnessed_death", "dahaönceafet": "cov_prior_disaster",
        "dahaöncehayatirisk": "cov_prior_life_risk"}
TIPI = [f"{t}.{k}" for k in (1, 2) for t in ("extrover", "meek", "respons", "emo.sta", "opentoex")]
PCL = [f"TSSB{i}" for i in range(1, 21)]
PVS = [f"PKÖ{i}" for i in range(1, 7)]


def main() -> None:
    d, m = pyreadstat.read_sav(mendeley_fetch("6sg3x4bchj", FNAME, RAW_DIR))
    assert len(d) == 503
    d["id"] = range(1, len(d) + 1)
    assert (d[PCL].sum(axis=1) == d["PTSD"]).all() and (d[PVS].sum(axis=1) == d["vulnerability"]).all()
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    emit({
        "gulec_2023_tipi": (long(d, TIPI, covs, valid=range(1, 8)), pv_for(TIPI, range(1, 8))),
        "gulec_2023_pcl5": (long(d, PCL, covs, valid=range(0, 5)), pv_for(PCL, range(0, 5))),
        "gulec_2023_pvs": (long(d, PVS, covs, valid=range(1, 6), rename={c: c.replace("Ö", "O") for c in PVS}),
                           pv_for([c.replace("Ö", "O") for c in PVS], range(1, 6))),
    })


if __name__ == "__main__":
    main()
