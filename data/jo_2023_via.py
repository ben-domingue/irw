#!/usr/bin/env python3
# Source: https://doi.org/10.5061/dryad.jdfn2z3g5 (Dryad; mirrored at https://zenodo.org/records/7982557)
# DOI: 10.5061/dryad.jdfn2z3g5 (dataset; the record names no paper)
#   Jo, Hyungjoo (2023). Data for: Evaluating motivation attributes and interaction
#   elements in user adoption of voice intelligent assistant [Dataset]. Dryad.
# Data: VIA_Dataset(262)_230529.xlsx, sheet "2201_AIPA Sample(262)": 262 voice-assistant
#       users, 10 constructs x 3 items on 1-7 agreement scales (README.md documents every
#       column: PUS perceived usefulness, INT interaction, UTM utilitarian motivation, VOA
#       voice attractiveness, HEM hedonic motivation, PSI parasocial interaction, LON
#       loneliness, COI continuance intention, CFS cabin fever syndrome, SAT satisfaction).
#       Dryad refuses plain-HTTP downloads, so the file is fetched from the Zenodo mirror.
# License: CC0 1.0 (Dryad and Zenodo records).
#
# Item text: not shipped. README.md paraphrases each item ("Degree of restlessness
#   experienced during social isolation/lockdown") rather than giving the administered
#   stem; no questionnaire is deposited. Checked: column headers (codes only) and README.
#
# One table: all 30 items of the one questionnaire, item = the deposit's column code
#   (construct prefix + position), resp 1-7. The ten 3-item blocks are constructs of a
#   single PLS-SEM questionnaire, kept together rather than split into 3-item files.
# Covariates: cov_gender (1 male, 2 female), cov_age (years), cov_ai_type (the deposit's
#   AI_Type code 1-7, undocumented beyond the code).
# id: the deposit's "No" (anonymous respondent id).

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

RAW_DIR = RAW_ROOT / "10_5061_dryad_jdfn2z3g5"
FNAME = "VIA_Dataset(262)_230529.xlsx"
BLOCKS = ["PUS", "INT", "UTM", "VOA", "HEM", "PSI", "LON", "COI", "CFS", "SAT"]


def main() -> None:
    d = pd.read_excel(zenodo_fetch(7982557, FNAME, RAW_DIR), sheet_name="2201_AIPA Sample(262)")
    assert len(d) == 262 and d["No"].is_unique
    items = [f"{b}{i}" for b in BLOCKS for i in (1, 2, 3)]
    assert set(items) <= set(d.columns)
    d = d.rename(columns={"No": "id", "GND": "cov_gender", "Age(N)": "cov_age", "AI_Type": "cov_ai_type"})
    covs = ["cov_gender", "cov_age", "cov_ai_type"]
    t = long(d, items, covs, valid=range(1, 8))
    emit({"jo_2023_via_adoption": (t, pv_for(items, range(1, 8)))})


if __name__ == "__main__":
    main()
