#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Enhancing_Chinese_Language_Learning_Through_Virtual_Reality_Cultural_Understanding_Pronunciation_Vocabulary_Engagement_and_Sentence_Construction/34021359
# DOI: 10.6084/m9.figshare.34021359 (dataset; the record names no published paper)
#   Yuan, Y. (2026). Enhancing Chinese Language Learning Through Virtual Reality: Cultural
#   Understanding, Pronunciation, Vocabulary, Engagement, and Sentence Construction. figshare.
# Data: "Data Set.xlsx", sheets "PRE TEST" and "POST TEST": 351 learners of Chinese as a
#       second/foreign language (quasi-experiment, 176 VR-taught vs 175 control), the same 18
#       five-point items (six blocks of three: CCE, PA, VOR, EM, SCS, CCA) before and after the
#       teaching period. Shipped as one table with wave 1 (pre) / 2 (post) and treat 1 for the
#       experimental group. The block abbreviations are as deposited; the record does not expand them.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped -- plain xlsx; the headers are the codes (PRE_CCE1 ...), there is no
#   legend sheet and no questionnaire file in the deposit, so neither stems nor option labels
#   exist in the source (checked: both sheets, no other files on the record).
#
# Tables: yuan_2026_vr_chinese (351 x 18 x 2 waves, 1-5).
# Covariates: cov_age_group, cov_gender, cov_proficiency (as deposited); treat 1 = Experimental.
# id: the deposit's ID (1-351; identical demographics on both sheets, checked).
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


RAW_DIR = RAW_ROOT / "figshare_34021359"
BLOCKS = ["CCE", "PA", "VOR", "EM", "SCS", "CCA"]
ITEMS = [f"{b}{i}" for b in BLOCKS for i in (1, 2, 3)]
COVS = {"AgeGroup": "cov_age_group", "Gender": "cov_gender", "LanguageProficiency": "cov_proficiency"}


def main() -> None:
    p = figshare_fetch(34021359, "Data Set.xlsx", RAW_DIR)
    sheets = pd.read_excel(p, sheet_name=["PRE TEST", "POST TEST"])
    frames = []
    for wave, (sheet, prefix) in enumerate([("PRE TEST", "PRE_"), ("POST TEST", "POST_")], 1):
        d = sheets[sheet].copy()
        assert len(d) == 351 and d["ID"].is_unique
        d = d.rename(columns={f"{prefix}{c}": c for c in ITEMS}).rename(columns=COVS)
        d["id"] = d["ID"].astype(int)
        d["wave"] = wave
        d["treat"] = d["GroupCode"].map({"Experimental": 1, "Control": 0})
        assert d["treat"].notna().all()
        frames.append(d)
    key = ["id", "treat", *COVS.values()]
    assert frames[0][key].sort_values("id").values.tolist() == frames[1][key].sort_values("id").values.tolist()
    d = pd.concat(frames, ignore_index=True)
    t = long(d, ITEMS, list(COVS.values()), valid=range(1, 6), extra=("wave", "treat"))
    emit({"yuan_2026_vr_chinese": (t, pv_for(ITEMS, range(1, 6)))})


if __name__ == "__main__":
    main()
