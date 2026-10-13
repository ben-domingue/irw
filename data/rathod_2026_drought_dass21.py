#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/IRIKMP
# DOI: 10.7910/DVN/IRIKMP (dataset; the record names no published paper)
#   Rathod, K., Haufiku, D., Lendelvo, S., Pinto, M., et al. (2026). Namibian drought
#   adaptation for food security, well-being, and psychosocial outcomes. Harvard Dataverse, V1.
# Data: Namibia_Deidentified.dta: a 730-respondent household survey in four Namibian regions
#       (Kavango West, Kunene, Ohangwena, Oshana) on drought adaptation; it embeds the 21-item
#       Depression Anxiety Stress Scales (DASS-21, 0-3) as one column per item, named by
#       subscale letter and a keyword, with the statement in the variable label. Only the
#       DASS-21 ships; the household, livelihood, food-security and coping sections are not
#       item-response data. The *_total / *_final / *_category / *_binary columns are the
#       authors' scores.
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: shipped (the .dta variable labels are the DASS-21 statements, "I found it hard to
#   wind down"; the items carry no value labels -- the 0-3 anchors are the standard DASS
#   "Did not apply to me at all .. Applied to me very much", taken from the instrument and
#   noted as such; English administration per the survey manual; built by
#   automated_finding/itemtext_verification/make_itemtext_rathod_2026.py, which imports
#   stems()). DASS is a `ship` row in itemtext/instrument_rights_register.csv.
#
# One table: rathod_2026_dass21 (730 x 21, 0-3), item = the deposit's column name (S_ stress,
#   A_ anxiety, D_ depression).
# Covariates: cov_region (1 Kavango West, 2 Kunene, 3 Ohangwena, 4 Oshana), cov_location
#   (1 rural, 2 urban), cov_age (years), cov_gender (1 female, 2 male), cov_household_head
#   (yes/no), cov_marital_status (1 cohabitating, 2 divorced/separated, 3 married, 4 single,
#   5 widowed), cov_employment (text as deposited).
# id: row index (Household_ID repeats for 15 rows).
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

RAW_DIR = RAW_ROOT / "10_7910_DVN_IRIKMP"
FNAME = "Namibia_Deidentified.dta"
COVS = {"region": "cov_region", "HH_location": "cov_location", "age_respondent": "cov_age",
        "gender_respondent": "cov_gender", "are_you_HHH": "cov_household_head",
        "marital_status_respondent": "cov_marital_status", "employment_respondent": "cov_employment"}
# DASS-21 items in the deposit's column order; the code is the subscale letter + the questionnaire
# position within the deposit (the file carries no item numbers)
ITEMS = ["S_wind_down", "A_dryness_mouth", "D_positive_feeling", "A_difficulty_breathing",
         "D_difficulty_initative", "S_over_react", "A_trembling_hands", "S_nervous_energy",
         "A_worry_fool_myself", "D_nothing_look_forward", "S_agitated", "S_difficult_relax",
         "D_down_blue", "S_intolerant", "A_close_panic", "D_unable_enthusiastic", "D_worth_much",
         "S_touchy", "A_heart_action", "A_scared_reason", "D_life_meaningless"]


def stems() -> list:
    """(item code, statement) pairs from the .dta variable labels, in deposit order."""
    _, meta = pyreadstat.read_dta(str(dv_fetch("10.7910/DVN/IRIKMP", FNAME, RAW_DIR)), metadataonly=True)
    return [(c, meta.column_names_to_labels[c].rstrip("'").strip()) for c in ITEMS]


def main() -> None:
    d, meta = pyreadstat.read_dta(str(dv_fetch("10.7910/DVN/IRIKMP", FNAME, RAW_DIR)))
    assert len(d) == 730
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1  # Household_ID is not unique (715 of 730)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in ("cov_region", "cov_location", "cov_gender", "cov_marital_status"):
        d[c] = d[c].astype("Int64")
    d["cov_age"] = d["cov_age"].astype("Int64")
    t = long(d, ITEMS, covs, valid=range(0, 4))
    emit({"rathod_2026_dass21": (t, pv_for(ITEMS, range(0, 4)))})


if __name__ == "__main__":
    main()
