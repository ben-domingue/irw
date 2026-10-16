#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/DATA_Comparing_disgust_sensitivity_in_women_in_early_pregnancy_and_non-pregnant_women_in_the_follicular_and_luteal_phases_of_the_menstrual_cycle/23807697
# DOI: 10.6084/m9.figshare.23807697 (dataset, 2023; Dlouhá, Daniela; Ullmann, Jana; Takács, Lea; Šeda, Jan; Nouzová,
#   Kamila; Hrbáčková, Hana; Kaňková, Šárka). Czech women: 172 in early pregnancy (first-trimester screening, ~10th gestational week)
#   and 354 non-pregnant women in the follicular or luteal phase of the menstrual cycle, recruited at
#   gynaecological check-ups in Prague.
# Data: DATA_Comparing ... .xlsx, sheet "Data" (526 rows) + sheet "Key" (covariate codes only). DS-R1_R ..
#       DS-R27 = Disgust Scale-Revised (0-4; items 1, 6, 10 stored already reversed, suffix _R; items 12 and 16
#       are the DS-R catch items, suffix _control, not shipped), tdds1-21 = Three Domain Disgust Scale (0-6).
#       Subscale and total scores, the C-DIS and the salient/control picture scores are not shipped.
#       Fractional cells (26 in the DS-R, 6 in the TDDS; e.g. 1.909 = 21/11) are person-mean imputations over
#       the other items of the subscale -- dropped, not shipped. One DS-R3 cell of 41 and one DS-R4 cell of 6
#       are out of range and dropped.
# License: CC BY 4.0 (figshare).
#
# Item text: not shipped -- the workbook carries codes only (the Key sheet documents the covariates, not the
#   items); the Czech DS-R / TDDS wording is not in the deposit.
#
# Tables: dlouha_2023_dsr (25 items), dlouha_2023_tdds (21 items).
# Covariates: cov_age, cov_pregnant (0/1), cov_gestation_age_days, cov_parity (0 primipara / 1 multipara),
#   cov_education (1 elementary, 2 secondary, 3 university), cov_residence (1-5 population bands),
#   cov_income (1-5 monthly bands), cov_partner (0/1), cov_cycle_phase (pregnant / follicular / luteal).
# id: row index (the deposit's K-codes are not shipped).
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

RAW_DIR = RAW_ROOT / "figshare_23807697"
FNAME = ("DATA_Comparing disgust sensitivity in women in early pregnancy and non-pregnant women in the "
         "follicular and luteal phases of the menstrual cycle.xlsx")


def main() -> None:
    d = pd.read_excel(figshare_fetch(23807697, FNAME, RAW_DIR), sheet_name="Data")
    d.columns = [c.strip() for c in d.columns]
    assert len(d) == 526 and d["ID"].is_unique
    d["id"] = range(1, len(d) + 1)
    d["cov_cycle_phase"] = d["cycle_phase"].str.strip()
    cov = {"cov_age": "age", "cov_pregnant": "pregnant", "cov_gestation_age_days": "gestation_age_days",
           "cov_parity": "parity", "cov_education": "education", "cov_residence": "place_now",
           "cov_income": "income", "cov_partner": "partner"}
    for k, v in cov.items():
        d[k] = d[v]
    covs = list(cov) + ["cov_cycle_phase"]
    dsr = [c for c in d.columns if c.startswith("DS-R") and c[4:].split("_")[0].isdigit() and "control" not in c]
    tdds = [c for c in d.columns if c.startswith("tdds")]
    assert len(dsr) == 25 and len(tdds) == 21, (len(dsr), len(tdds))
    dropped = {"fractional": 0, "out_of_range": 0}
    for cols, valid in ((dsr, range(0, 5)), (tdds, range(0, 7))):
        for c in cols:
            s = pd.to_numeric(d[c], errors="coerce")
            frac = s.notna() & (s % 1 != 0)
            oor = s.notna() & ~frac & ~s.isin(list(valid))
            dropped["fractional"] += int(frac.sum())
            dropped["out_of_range"] += int(oor.sum())
            d[c] = s.mask(frac | oor)
    print("dropped cells:", dropped)
    assert dropped == {"fractional": 32, "out_of_range": 2}, dropped
    emit({"dlouha_2023_dsr": (long(d, dsr, covs, valid=range(0, 5)), pv_for(dsr, range(0, 5))),
          "dlouha_2023_tdds": (long(d, tdds, covs, valid=range(0, 7)), pv_for(tdds, range(0, 7)))})


if __name__ == "__main__":
    main()
