#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Associations_between_nausea_and_vomiting_in_pregnancy_disgust_sensitivity_and_first-trimester_maternal_serum_free-_hCG_and_PAPP-A/20509353
# DOI: 10.6084/m9.figshare.20509353 (dataset, 2023; Kaňková, Šárka; Ullmann, Jana; Fiurašková, Kateřina; Havlíček,
#   Jan; Calda, Pavel; Dlouhá, Daniela; Roberts, S. Craig). Pregnant women at their first-trimester screening (General University Hospital, Prague),
#   two samples (202 + 397).
# Data: Data_NVPdisgustPAPPAhCG_FIGSHARE.xlsx, sheet "List1" (599 rows) + "Key" (covariate codes). INVR1-8 =
#       Rhodes Index of Nausea, Vomiting and Retching (0-4), DS-R x 25 = Disgust Scale-Revised without the two
#       catch items (0-4), TDDS3/6/9/12/15/18/21 = the pathogen subscale of the Three Domain Disgust Scale
#       (0-6), stai1-6 = six-item state anxiety (1-4). Columns marked "(revers)" are stored already reversed
#       and ship with an _R suffix. Scores, PAPP-A and hCG MoM values ship as covariates, not items.
#       The 550 women of the lab's earlier deposit 10.6084/m9.figshare.16843210 ("Disgust sensitivity increases
#       in early pregnancy ...", lead 30 of repos_leads_2026-10-15) are a strict subset of these 599 (DS-R
#       item vector + age match 550/550), so that deposit is not shipped separately.
# License: CC BY 4.0 (figshare).
#
# Item text: not shipped -- codes only; the Key sheet documents covariates, not items; Czech wording not deposited.
#
# Tables: kankova_2023_dsr (25), kankova_2023_invr (8), kankova_2023_tdds_pathogen (7), kankova_2023_stai6 (6).
# Covariates: cov_sample (1/2), cov_chronic_disease (0/1), cov_current_health_problems (0/1), cov_age,
#   cov_parity (0 primipara / 1 multipara), cov_residence_size (1-5), cov_education (1-3), cov_household_income
#   (1-5), cov_pregnancy_length_days, cov_papp_a_mom, cov_hcg_mom, cov_rhodes_index.
# id: row index (no respondent code in the deposit).
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

RAW_DIR = RAW_ROOT / "figshare_20509353"


def code(c: str) -> str:
    return c.strip().replace("(revers)", "_R")


def main() -> None:
    d = pd.read_excel(figshare_fetch(20509353, "Data_NVPdisgustPAPPAhCG_FIGSHARE.xlsx", RAW_DIR), sheet_name="List1")
    d.columns = [c.strip() for c in d.columns]
    assert len(d) == 599
    d["id"] = range(1, len(d) + 1)
    cov = {"cov_sample": "sample", "cov_chronic_disease": "chronic or autoimmune diseases (1=yes)",
           "cov_current_health_problems": "current health probems (1=yes)", "cov_age": "age", "cov_parity": "parity",
           "cov_residence_size": "residence size", "cov_education": "education",
           "cov_household_income": "household_income", "cov_pregnancy_length_days": "pregnancy_lenght_questionaire",
           "cov_papp_a_mom": "PAPP_MoM", "cov_hcg_mom": "HCG_MoM", "cov_rhodes_index": "RHODES_index"}
    for k, v in cov.items():
        d[k] = d[v]
    covs = list(cov)
    invr = [c for c in d.columns if c.startswith("INVR")]
    dsr = [c for c in d.columns if c.startswith("DS-R") and c[4:].replace("(revers)", "").isdigit()]
    tdds = [c for c in d.columns if c.startswith("TDDS") and c[4:].isdigit()]
    stai = [c for c in d.columns if c.startswith("stai") and c[4:].replace("(revers)", "").isdigit()]
    assert (len(invr), len(dsr), len(tdds), len(stai)) == (8, 25, 7, 6)
    ren = {c: code(c) for c in invr + dsr + tdds + stai}
    tabs = {}
    for name, cols, valid in (("kankova_2023_dsr", dsr, range(0, 5)), ("kankova_2023_invr", invr, range(0, 5)),
                              ("kankova_2023_tdds_pathogen", tdds, range(0, 7)), ("kankova_2023_stai6", stai, range(1, 5))):
        t = long(d, cols, covs, valid=valid, rename=ren)
        tabs[name] = (t, pv_for([ren[c] for c in cols], valid))
    emit(tabs)


if __name__ == "__main__":
    main()
