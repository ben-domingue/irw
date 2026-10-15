#!/usr/bin/env python3
# Source: https://frontiersin.figshare.com/articles/dataset/Data_Sheet_1_Big_Five_personality_and_mind_wandering_in_athletes_mediating_role_of_trait_anxiety_CSV/25210199
# DOI: 10.3389/fpsyg.2024.1232312.s001 (supplementary data of 10.3389/fpsyg.2024.1232312)
#   Li, Y., Ma, J., Xi, Y., & Li, J. (2024). Big Five personality and mind wandering in athletes:
#   mediating role of trait anxiety. Frontiers in Psychology, 15, 1232312.
# Data: Data_Sheet_1 (CSV), 681 Chinese athletes: MW1-MW31 (MW19 absent, 30 items, 1-5) the
#       Mind Wandering Questionnaire block, JL1-JL17 (JL10 absent, 16 items, 1-6) the trait
#       anxiety block (焦虑), RG1-RG20 (20 items, 1-6) the Big Five block (人格). Codes are the
#       deposit's own column names.
# License: CC BY 4.0 (figshare record; Frontiers article CC BY 4.0).
#
# Item text: not shipped -- the CSV has positional codes only; the paper names the instruments
#   but the administered Chinese wording is not in the deposit.
#
# Tables: li_2024_mind_wandering (30, 1-5), li_2024_trait_anxiety (16, 1-6), li_2024_big_five
#   (20, 1-6).
# Covariates: cov_gender (1/2 as deposited), cov_age (years), cov_sports_group (1/2),
#   cov_level (1-4), cov_sports_years.
# id: row index (no respondent identifier in the file).
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

RAW_DIR = RAW_ROOT / "figshare_25210199"
FNAME = "Data_Sheet_1_Big Five personality and mind wandering in athletes: mediating role of trait anxiety.CSV"
COVS = {"gender": "cov_gender", "years": "cov_age", "sports group": "cov_sports_group", "level": "cov_level",
        "sports years": "cov_sports_years"}
BLOCKS = {"li_2024_mind_wandering": ([f"MW{i}" for i in range(1, 32) if i != 19], range(1, 6)),
          "li_2024_trait_anxiety": ([f"JL{i}" for i in range(1, 18) if i != 10], range(1, 7)),
          "li_2024_big_five": ([f"RG{i}" for i in range(1, 21)], range(1, 7))}


def main() -> None:
    d = pd.read_csv(figshare_fetch(25210199, FNAME, RAW_DIR))
    assert len(d) == 681
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs[:-1]:
        d[c] = pd.to_numeric(d[c]).astype("Int64")
    d["cov_sports_years"] = pd.to_numeric(d["cov_sports_years"])  # fractional years occur
    emit({t: (long(d, items, covs, valid=valid), pv_for(items, valid)) for t, (items, valid) in BLOCKS.items()})


if __name__ == "__main__":
    main()
