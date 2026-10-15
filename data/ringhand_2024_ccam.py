#!/usr/bin/env python3
# Source: https://zenodo.org/records/14394129
# DOI: 10.5281/zenodo.14394129 (dataset; EU project SINFONICA, no paper named on the record)
#   Ringhand, M., & Anke, J. (2024). SINFONICA - Online survey data - Survey on the user factors
#   that affect the future deployment of CCAM. Zenodo.
# Data: 2024-12-06_Zenodo.sav (4,472 respondents, EU-wide online survey, March-June 2024,
#       administered in eight languages: English, German, Italian, Dutch, Greek, Spanish, Polish,
#       French). Two blocks ship: 15 importance ratings of public-transport service attributes
#       (1 "very unimportant" .. 101 "very important" slider) and 12 Theory-of-Planned-Behaviour /
#       trust items about using CCAM (connected, cooperative and automated mobility) vehicles
#       (1-5). Modal-split frequencies, familiarity, impairment and demographic items do not ship.
#       The deposit's variable/value label CSVs mirror the .sav metadata.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped for ringhand_2024_ccam_tpb (the .sav variable labels are the English stems,
#   value labels the five anchors -- endpoint-only on the AT semantic-differential items);
#   language lists all eight administered languages, English wording shipped. Not shipped for
#   ringhand_2024_ccam_importance: a 101-point slider labelled only at its endpoints.
#
# Tables: ringhand_2024_ccam_importance (15 items, 1-101), ringhand_2024_ccam_tpb (12 items, 1-5).
# Covariates: cov_language (1 eng, 2 ger, 3 ita, 4 dut, 5 gre, 6 spa, 7 pol, 8 fre), cov_age
#   (years), cov_gender (1 female, 2 male, 3 non-binary, 4 self-description), cov_country (code
#   per the value labels), cov_education, cov_employment. Negative codes are missing.
# id: CASE, the deposit's interview number.
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

RAW_DIR = RAW_ROOT / "zenodo_14394129"
FNAME = "2024-12-06_Zenodo.sav"
COVS = {"LANGUAGE": "cov_language", "SD_age": "cov_age", "SD_gender": "cov_gender",
        "SD_countr": "cov_country", "SD_edu": "cov_education", "SD_empl": "cov_employment"}
IMPORTANCE = ["Avail_Dist", "Avail_Conn", "Avail_Time", "Avail_Info_Dig", "Avail_Info_Pers", "Avail_Lugg",
              "Acces_Barr", "Acces_Ease", "Acces_Kid", "Affor_Price", "Accep_Clean", "Accep_Safe",
              "Accep_Secure", "Accep_Influ", "Accep_Sustai"]
TPB = ["AT01_TPB", "AT02_TPB", "AT03_TPB", "AT04_TPB", "IN_CCAM_TPB", "PBC_CCAM_TPB", "PBC_PT_TPB",
       "SN01_TPB", "SN02_TPB", "TR01_TPB", "TR02_TPB", "TR03_TPB"]


def stems() -> list:
    """(code, variable label, {value: label}) for the TPB items, from the .sav metadata."""
    _, meta = pyreadstat.read_sav(str(zenodo_fetch(14394129, FNAME, RAW_DIR)), metadataonly=True)
    return [(c, meta.column_names_to_labels[c], {int(k): v for k, v in meta.variable_value_labels[c].items() if k > 0})
            for c in TPB]


def main() -> None:
    d, meta = pyreadstat.read_sav(str(zenodo_fetch(14394129, FNAME, RAW_DIR)))
    assert len(d) == 4472 and d["CASE"].is_unique
    d = d.rename(columns={"CASE": "id", **COVS})
    covs = list(COVS.values())
    for c in covs:
        d.loc[d[c] < 0, c] = pd.NA
        d[c] = d[c].astype("Int64")
    for c in IMPORTANCE + TPB:
        d.loc[d[c] < 1, c] = pd.NA
    d["id"] = d["id"].astype(int)
    imp = long(d, IMPORTANCE, covs, valid=range(1, 102))
    tpb = long(d, TPB, covs, valid=range(1, 6))
    emit({"ringhand_2024_ccam_importance": (imp, pv_for(IMPORTANCE, range(1, 102))),
          "ringhand_2024_ccam_tpb": (tpb, pv_for(TPB, range(1, 6)))})


if __name__ == "__main__":
    main()
