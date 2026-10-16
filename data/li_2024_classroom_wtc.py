#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/4jfcp2psxf (also https://data.mendeley.com/datasets/38ddjj8tcb and
#   https://data.mendeley.com/datasets/394x5ynsd8 -- three deposits of the same 457 respondents)
# DOI: 10.17632/4jfcp2psxf.1 (2024; Li, Muzi; Yap, Teng Teng; Chew, Fong Peng), 10.17632/38ddjj8tcb.1 (2025; Li,
#   Muzi), 10.17632/394x5ynsd8.1 (2024; Li, Muzi). International students learning Chinese as a second language
#   (Asian and non-Asian backgrounds); one survey, published across three papers on classroom social climate,
#   self-confidence, enjoyment and willingness to communicate (WTC).
# Data: three .sav files, 457 rows each. CSC1-13 (classroom social climate, 1-5 agreement) and the demographics
#       are byte-identical between the first two deposits; WTC1-11 (cross-setting WTC, 1-5 "definitely not
#       willing" .. "definitely willing") are identical between the second and third; the first deposit's WTC1-4
#       are a different, digital-context WTC block; SC1-8 = self-confidence (1-5); EN1-11 = enjoyment (1-5). The
#       authors' subscale means (CSCa/b/c, WTCa/b/c, SC, EN) are not shipped. Rows are matched by position.
# License: CC BY 4.0 (Mendeley Data), all three deposits.
#
# Item text: not shipped -- no variable labels (stems) in any of the three .sav files; value labels carry only
#   the anchors ("strongly disagree" .. "strongly agree"; "definitely not willing" .. "definitely willing").
#
# Tables: li_2024_csc (13), li_2024_self_confidence (8), li_2024_wtc_digital (4), li_2024_wtc_cross_setting (11),
#   li_2024_enjoyment (11); N = 457 each, same ids.
# Covariates: cov_gender (1 male, 2 female), cov_age (1 <18, 2 18-20, 3 21-23, 4 24-26, 5 >26),
#   cov_cultural_background (1 Asia, 2 non-Asia), cov_mother_language (free text as deposited).
# id: row index (shared across the five tables).
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

RAW = RAW_ROOT / "mendeley_li_2024"
F1 = ("The Full Mediating Role of Self-confidence in the Relationship between Classroom Social Climate and "
      "Willingness to Communicate in Digital Contexts.sav")
F2 = "Linking classroom social climate to cross-setting willingness to communicate.sav"
F3 = "dataset of Enjoyment and WTC.sav"


def main() -> None:
    a, ma = pyreadstat.read_sav(str(mendeley_fetch("4jfcp2psxf", F1, RAW)))
    b, mb = pyreadstat.read_sav(str(mendeley_fetch("38ddjj8tcb", F2, RAW)))
    c, mc = pyreadstat.read_sav(str(mendeley_fetch("394x5ynsd8", F3, RAW)))
    assert len(a) == len(b) == len(c) == 457
    csc = [f"CSC{i}" for i in range(1, 14)]
    sc = [f"SC{i}" for i in range(1, 9)]
    wtc4 = [f"WTC{i}" for i in range(1, 5)]
    wtc11 = [f"WTC{i}" for i in range(1, 12)]
    en = [f"EN{i}" for i in range(1, 12)]
    assert not any(ma.column_names_to_labels.get(x) for x in csc + sc + wtc4), "stems would be cheap item text"
    assert not any(mb.column_names_to_labels.get(x) for x in wtc11) and not any(mc.column_names_to_labels.get(x) for x in en)
    assert a[csc].equals(b[csc]) and a[["Gender", "Age", "MotherLanguage"]].equals(b[["Gender", "Age", "MotherLanguage"]])
    assert b[wtc11].equals(c[wtc11]) and (a["AsiaNonAsia"].values == c["culturalbackgrounds"].values).all()
    assert not a[wtc4].equals(b[wtc4]), "the digital-context WTC block is a different instrument"
    d = a[["Gender", "Age", "AsiaNonAsia", "MotherLanguage", *csc, *sc, *wtc4]].copy()
    d.columns = ["Gender", "Age", "AsiaNonAsia", "MotherLanguage", *csc, *sc, *[f"WTCd{i}" for i in range(1, 5)]]
    for col in wtc11:
        d[col] = b[col].values
    for col in en:
        d[col] = c[col].values
    d["id"] = range(1, len(d) + 1)
    d["cov_gender"] = d["Gender"]
    d["cov_age"] = d["Age"]
    d["cov_cultural_background"] = d["AsiaNonAsia"]
    d["cov_mother_language"] = d["MotherLanguage"].str.strip()
    covs = ["cov_gender", "cov_age", "cov_cultural_background", "cov_mother_language"]
    r = range(1, 6)
    wtcd = [f"WTCd{i}" for i in range(1, 5)]
    emit({"li_2024_csc": (long(d, csc, covs, valid=r), pv_for(csc, r)),
          "li_2024_self_confidence": (long(d, sc, covs, valid=r), pv_for(sc, r)),
          "li_2024_wtc_digital": (long(d, wtcd, covs, valid=r, rename={x: x.replace("WTCd", "WTC") for x in wtcd}), pv_for(wtc4, r)),
          "li_2024_wtc_cross_setting": (long(d, wtc11, covs, valid=r), pv_for(wtc11, r)),
          "li_2024_enjoyment": (long(d, en, covs, valid=r), pv_for(en, r))})


if __name__ == "__main__":
    main()
