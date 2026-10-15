#!/usr/bin/env python3
# Source: https://zenodo.org/records/22644543
# DOI: 10.5281/zenodo.22644543 (dataset, 2026; Sakal, Sökün & Koçak). "Measuring Workplace Resistance
#   to Artificial Intelligence -- A Scale Development Study" (manuscript, no DOI on the record).
# Data: Sakal_et_al_AI_Resistance_Scale_Dataset_N724.csv, 724 Turkish employees: 27 items BDS_01-10
#       (individual resistance), KDS_13-28 (organizational resistance), KBL_41-45 (acceptance /
#       perceived benefit), 1-5 Strongly Disagree .. Strongly Agree; careless-response screening
#       already applied upstream (Risk_Flag retained, not shipped). CODEBOOK_*.txt lists the Turkish
#       item wording per variable.
# License: CC BY 4.0 (Zenodo).
#
# Item text: shipped (deposited codebook keys each variable name to its Turkish stem; anchors from the
#   codebook's scale line; Turkish administration). Built by
#   automated_finding/itemtext_verification/make_itemtext_sakal_2026.py.
#
# Table: sakal_2026_ai_resistance (724 x 27, 1-5); item = the file's column name.
# Covariates: cov_gender (male/female from Erkek/Kadın), cov_age, cov_education (Turkish label as
#   deposited), cov_years_experience, cov_ai_use_frequency (Turkish label as deposited).
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

RAW_DIR = RAW_ROOT / "zn_22644543"
FNAME = "Sakal_et_al_AI_Resistance_Scale_Dataset_N724.csv"
CODEBOOK = "CODEBOOK_Sakal_et_al_AI_Resistance_Scale.txt"


def stems() -> dict:
    txt = zenodo_fetch(22644543, CODEBOOK, RAW_DIR).read_text(encoding="utf-8")
    return dict(re.findall(r"^([A-Z]{3}_\d{2}) \[[^\]]+\]: (.+)$", txt, flags=re.M))


def main() -> None:
    d = pd.read_csv(zenodo_fetch(22644543, FNAME, RAW_DIR), encoding="utf-8-sig")
    assert len(d) == 724
    d["id"] = d.index + 1
    items = [c for c in d.columns if re.fullmatch(r"[A-Z]{3}_\d{2}", c)]
    assert len(items) == 27 and set(items) == set(stems())
    d["cov_gender"] = d["gender"].map({"Erkek": "male", "Kadın": "female"})
    assert d["cov_gender"].notna().all()
    d["cov_age"] = d["age"].astype("Int64")
    d["cov_education"] = d["education_level"]
    d["cov_years_experience"] = pd.to_numeric(d["years_experience"], errors="coerce")
    d["cov_ai_use_frequency"] = d["ai_use_frequency"]
    covs = ["cov_gender", "cov_age", "cov_education", "cov_years_experience", "cov_ai_use_frequency"]
    emit({"sakal_2026_ai_resistance": (long(d, items, covs, valid=range(1, 6)), pv_for(items, range(1, 6)))})


if __name__ == "__main__":
    main()
