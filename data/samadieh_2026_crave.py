#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Data_and_Analysis_Materials_for_The_CRAVE_Scale_to_Measure_Motivational_States_for_Physical_Activity_and_Sedentary_Behavior_Psychometric_Properties_and_Psychophysical_Correlates/33964891
# DOI: 10.6084/m9.figshare.33964891 (dataset, 2026; Samadieh, Hadi; Tanhaye Reshvanloo, Farhad;
#   Stults-Kolehmainen, Matthew A.). Persian validation of the CRAVE scale (Cravings for Rest and Volitional
#   Energy Expenditure) in three Iranian adult samples (Study 1 n = 313, Study 2 n = 346, Study 3 n = 244).
# Data: STUDY 1.sav, STUDY 2.sav, STUDY 3.sav (no variable or value labels on the items). N1-N13 = CRAVE "right
#       now" items, W1-W13 = CRAVE "past week" items (0-10). Study 3 adds S1-S7 (physical dysfunction, 0-3) and
#       V1-V6 (subjective vitality, 1-7). The authors' Move/Rest subscale sums are not shipped. Whether the three
#       samples share respondents is not stated; they are pooled with cov_study and separate id ranges.
# License: CC BY 4.0 (figshare).
#
# Item text: not shipped -- the .sav files have no variable labels and no value labels on any item (both
#   levels checked; value labels exist only on gender, marital status, education and employment); the Persian
#   CRAVE wording is in the paper, not the deposit.
#
# Tables: samadieh_2026_crave_now (13, N = 903), samadieh_2026_crave_week (13, N = 903),
#   samadieh_2026_physical_dysfunction (7, Study 3), samadieh_2026_vitality (6, Study 3).
# Covariates: cov_study (1/2/3), cov_gender (1 female, 2 male), cov_age, cov_marital_status (1 single, 2 married),
#   cov_education (1 undergraduate, 2 MA/MSc, 3 PhD/MD), cov_employed (0/1), cov_bmi.
# id: 1000 * study + the file's `sort` column.
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
import pyreadstat

RAW_DIR = RAW_ROOT / "figshare_33964891"


def load(study: int) -> pd.DataFrame:
    d, meta = pyreadstat.read_sav(str(figshare_fetch(33964891, f"STUDY {study}.sav", RAW_DIR)))
    assert not any(meta.column_names_to_labels.get(c) for c in d.columns if c[0] in "NWSV")
    d["id"] = 1000 * study + d["sort"].astype(int)
    d["cov_study"] = study
    for k, v in {"cov_gender": "gender", "cov_age": "age", "cov_marital_status": "maritalStat",
                 "cov_education": "educLevel", "cov_employed": "EmployStat", "cov_bmi": "BMI"}.items():
        d[k] = d[v]
    return d


def main() -> None:
    s = {k: load(k) for k in (1, 2, 3)}
    assert tuple(len(v) for v in s.values()) == (313, 346, 244)
    covs = ["cov_study", "cov_gender", "cov_age", "cov_marital_status", "cov_education", "cov_employed", "cov_bmi"]
    n = [f"N{i}" for i in range(1, 14)]
    w = [f"W{i}" for i in range(1, 14)]
    sd = [f"S{i}" for i in range(1, 8)]
    v = [f"V{i}" for i in range(1, 7)]
    pooled = pd.concat(s.values(), ignore_index=True)
    r11 = range(0, 11)
    emit({"samadieh_2026_crave_now": (long(pooled, n, covs, valid=r11), pv_for(n, r11)),
          "samadieh_2026_crave_week": (long(pooled, w, covs, valid=r11), pv_for(w, r11)),
          "samadieh_2026_physical_dysfunction": (long(s[3], sd, covs, valid=range(0, 4)), pv_for(sd, range(0, 4))),
          "samadieh_2026_vitality": (long(s[3], v, covs, valid=range(1, 8)), pv_for(v, range(1, 8)))})


if __name__ == "__main__":
    main()
