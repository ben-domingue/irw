#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/VR7OND
# DOI: 10.7910/DVN/VR7OND (dataset). Paper: Kassas, B., Morgan, S. N., Lai, J., & Kropp, J. D.
#   (2021). Perception versus preference: The role of self-assessed risk measures on individual
#   mitigation behaviors during the COVID-19 pandemic. PLOS ONE (DOI not on the record).
# Data: COVID_data_pone.dta: 970 US adults (online survey, spring 2020) rating how likely they
#       are to be exposed to COVID-19 in 14 settings (1 extremely unlikely .. 5 extremely
#       likely) and reporting seven household mitigation behaviours (0/1), plus demographics,
#       a 0-10 risk-preference self-assessment and a 0-100 probability judgement (prob_covid,
#       not shipped). The "cleaning" column carries the same Stata label as "delivery" in the
#       deposit (a label slip); it ships under its own name. The totals (mitigation_total,
#       riskyplace_total) and the dummy expansions (pol_*, children*, ruc*) are not shipped.
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: shipped for both tables (the .dta variable labels are the questions -- "How likely
#   are you to be exposed to COVID19 at the grocery store?" -- and the value labels give the
#   five likelihood anchors / Yes-No; English administration; built by
#   automated_finding/itemtext_verification/make_itemtext_kassas_2021.py, which imports
#   labels()).
#
# Tables: kassas_2021_covid_exposure (970 x 14, 1-5), kassas_2021_covid_mitigation (970 x 7,
#   0/1), item = the deposit's column name.
# Covariates: cov_age_group (0 <18 .. 6 65+), cov_education (0-5), cov_political_affiliation
#   (1 Republican, 2 Democrat, 3 Independent, 4 Other, 5 No preference), cov_household_income
#   (1-10 brackets), cov_essential_worker (0/1), cov_male (0/1), cov_state (Stata-coded),
#   cov_risk_preference (0 risk averse .. 10 risk loving).
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
import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "10_7910_DVN_VR7OND"
FNAME = "COVID_data_pone.dta"
COVS = {"age": "cov_age_group", "educ": "cov_education", "pol": "cov_political_affiliation",
        "hhinc": "cov_household_income", "essential": "cov_essential_worker", "male": "cov_male",
        "state1": "cov_state", "riskpref": "cov_risk_preference"}
EXP = ["exp_grocery", "exp_hosp", "exp_doctor", "exp_delivery", "exp_restaurant", "exp_gas", "exp_work",
       "exp_home", "exp_rec", "exp_religious", "exp_publictransit", "exp_taxi", "exp_daycare", "exp_school"]
MIT = ["social_distance", "reduce_travel", "wash_hands", "mask", "gloves", "delivery", "cleaning"]


def labels() -> tuple:
    """(variable labels, value labels) from the .dta, for the item text builder."""
    _, meta = pyreadstat.read_dta(str(dv_fetch("10.7910/DVN/VR7OND", FNAME, RAW_DIR)), metadataonly=True)
    return meta.column_names_to_labels, meta.variable_value_labels


def main() -> None:
    d, _ = pyreadstat.read_dta(str(dv_fetch("10.7910/DVN/VR7OND", FNAME, RAW_DIR)))
    assert len(d) == 970
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    emit({
        "kassas_2021_covid_exposure": (long(d, EXP, covs, valid=range(1, 6)), pv_for(EXP, range(1, 6))),
        "kassas_2021_covid_mitigation": (long(d, MIT, covs, valid=(0, 1)), pv_for(MIT, (0, 1))),
    })


if __name__ == "__main__":
    main()
