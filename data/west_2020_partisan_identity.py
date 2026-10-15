#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/OF2PIH
# DOI: 10.7910/DVN/OF2PIH (Harvard Dataverse, 2020; West, Emily). "Replication Data for: Partisanship
#   as a Social Identity: Implications for Polarization" (Political Behavior); paper DOI not on the
#   record.
# Data: polbeh_partsocid_dataverse.dta (format=original), 3,824 completed Qualtrics interviews of US
#       adults in two waves (wave 1 before, wave 2 after the Nov 2018 election; contactid links the
#       1,311 panel re-interviews, the rest are fresh respondents). Survey-experiment outcome
#       batteries, shipped as answered: trump_job_app/economy/health_care/immigration/foreign_policy
#       (0-4), trump_qualities_1-7 (1-4), trump_feel_1-6 (1-4), dem/rep-supporters trait ratings
#       (patriotic, selfish, compromise, narrow-minded, compassionate, 1-4), feelingthermointro_4-15
#       twelve 0-100 group thermometers. The character-strength ranking treatment (treat_/control_*),
#       manipulation checks, PCA scores, indices and single policy items are not shipped. The .dta
#       variable labels are the Qualtrics question names, not stems; no codebook in the deposit.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped -- labels are Qualtrics variable names ("Trump_qualities_1"); the
#   questionnaire is not deposited.
#
# Tables: west_2020_trump_approval (5, 0-4), west_2020_trump_qualities (7, 1-4), west_2020_trump_feel
#   (6, 1-4), west_2020_partisan_traits (10, 1-4), west_2020_feeling_thermometer (12, 0-100); each
#   with wave (1, 2).
# Covariates: cov_age, cov_gender (1-3), cov_ethnicity (1-4), cov_income (0-19), cov_education (1-9),
#   cov_party_id (1 Democrat, 3 Republican), cov_ideology (1-7), cov_treat (satreatment 0/1),
#   cov_panel (0/1).
# id: contactid for panel members (same id in both waves); 10000 + row number for the others.
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

RAW_DIR = RAW_ROOT / "dvn_OF2PIH"
FNAME = "polbeh_partsocid_dataverse.dta"


def main() -> None:
    d = pd.read_stata(dv_fetch("10.7910/DVN/OF2PIH", FNAME, RAW_DIR), convert_categoricals=False)
    assert len(d) == 3824
    d["id"] = d["contactid"].where(d["contactid"].notna(), 10000 + pd.Series(range(len(d)))).astype(int)
    assert not d.duplicated(["id", "wave"]).any()
    d["wave"] = d["wave"].astype(int)
    cov = {"cov_age": "age", "cov_gender": "gender", "cov_ethnicity": "ethnicity", "cov_income": "income",
           "cov_education": "education", "cov_party_id": "party_id", "cov_ideology": "ideology1",
           "cov_treat": "satreatment", "cov_panel": "panel"}
    for k, v in cov.items():
        d[k] = d[v].astype("Int64")
    covs = list(cov)
    appr = ["trump_job_app", "trump_economy", "trump_health_care", "trump_immigration", "trump_foreign_policy"]
    qual = [f"trump_qualities_{i}" for i in range(1, 8)]
    feel = [f"trump_feel_{i}" for i in range(1, 7)]
    traits = [c for c in d.columns if re.fullmatch(r"(dem|rep)supporters_\w+", c)]
    therm = [c for c in d.columns if re.fullmatch(r"feelingthermointro_\d+", c)]
    assert len(traits) == 10 and len(therm) == 12
    w = ["wave"]
    emit({"west_2020_trump_approval": (long(d, appr, covs, valid=range(0, 5), extra=w), pv_for(appr, range(0, 5))),
          "west_2020_trump_qualities": (long(d, qual, covs, valid=range(1, 5), extra=w), pv_for(qual, range(1, 5))),
          "west_2020_trump_feel": (long(d, feel, covs, valid=range(1, 5), extra=w), pv_for(feel, range(1, 5))),
          "west_2020_partisan_traits": (long(d, traits, covs, valid=range(1, 5), extra=w), pv_for(traits, range(1, 5))),
          "west_2020_feeling_thermometer": (long(d, therm, covs, valid=range(0, 101), extra=w), None)})


if __name__ == "__main__":
    main()
