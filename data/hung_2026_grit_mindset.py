#!/usr/bin/env python3

# Source: https://zenodo.org/records/18113188
# DOI: 10.5281/zenodo.18113188 (dataset; the record names no published paper)
#   Hung (2026). The Role of Grit and Life Satisfaction in the Growth Mindset-Academic
#   Engagement Link [Dataset]. Zenodo.
# Data: "522English.sav": 522 students of Chinese Language, with four published
#       instruments deposited at the item level, all on a 1-7 scale.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped for all four tables (English, from the SPSS variable labels, which
#   carry the full stem for every one of the 40 items; the value labels carry the 1-7
#   anchors). Checked both label levels.
#
# Four tables, one per instrument:
#   hung_2026_swls             5 items, Satisfaction With Life Scale (LS1-LS5).
#   hung_2026_uwes_s          17 items, Utrecht Work Engagement Scale-Student: VE vigour
#                             (6), DE dedication (5), AE absorption (6).
#   hung_2026_grit            11 items, Grit scale: POE*F perseverance of effort (6),
#                             COI*R consistency of interest (5).
#   hung_2026_growth_mindset   6 items, GM1R-GM3R fixed-mindset wording, GM4F-GM6F growth.
# The R/F suffixes are the deposit's own and are kept: they mark the direction the item is
# worded in, not a recode -- every column holds the raw 1-7 response.
# Not shipped: the eleven (AV) columns, which are subscale and scale means.
# Covariates: cov_gender, cov_age, cov_nation, cov_grade, cov_location,
#   cov_study_hours_per_day (the deposit's "time", self-reported hours).
# id: the deposit's "Number" (522 distinct over 522 rows).
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

def books(all_cols, used: dict) -> None:
    """Every source column is either shipped or skipped for a printed reason."""
    seen = {}
    for reason, cols in used.items():
        for c in cols:
            assert c not in seen, (c, reason, seen[c])
            seen[c] = reason
    missing = [c for c in all_cols if c not in seen]
    assert not missing, f"unaccounted source columns: {missing}"
    extra = [c for c in seen if c not in all_cols]
    assert not extra, f"named columns not in the source: {extra}"
    for reason, cols in used.items():
        if reason != "shipped" and cols:
            print(f"    [skipped: {reason}] {len(cols)}: {', '.join(map(str, cols))[:300]}")


RAW_DIR = RAW_ROOT / "10_5281_zenodo_18113188"
SWLS = [f"LS{i}" for i in range(1, 6)]
UWES = ([f"VE{i}" for i in range(1, 7)] + [f"DE{i}" for i in range(7, 12)]
        + [f"AE{i}" for i in range(12, 18)])
GRIT = ["POE1F", "POE4F", "POE6F", "POE9F", "POE10F", "POE12F",
        "COI3R", "COI5R", "COI7R", "COI8R", "COI11R"]
MINDSET = ["GM1R", "GM2R", "GM3R", "GM4F", "GM5F", "GM6F"]
COVS = {"gender": "cov_gender", "age": "cov_age", "nation": "cov_nation",
        "grade": "cov_grade", "location": "cov_location",
        "time": "cov_study_hours_per_day"}


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(zenodo_fetch(18113188, "522English.sav", RAW_DIR),
                                  apply_value_formats=False)
    assert len(d) == 522, len(d)
    src = list(d.columns)
    means = [c for c in src if "AV" in c]
    assert len(means) == 11, means
    books(src, {
        "shipped": SWLS + UWES + GRIT + MINDSET,
        "covariate": list(COVS),
        "respondent id": ["Number"],
        "subscale or scale mean computed by the depositor": means,
    })
    d = d.rename(columns={"Number": "id", **COVS})
    covs = list(COVS.values())
    assert d["id"].nunique() == len(d)
    v = range(1, 8)
    emit({
        "hung_2026_swls": (long(d, SWLS, covs, valid=v), pv_for(SWLS, v)),
        "hung_2026_uwes_s": (long(d, UWES, covs, valid=v), pv_for(UWES, v)),
        "hung_2026_grit": (long(d, GRIT, covs, valid=v), pv_for(GRIT, v)),
        "hung_2026_growth_mindset": (long(d, MINDSET, covs, valid=v), pv_for(MINDSET, v)),
    })


if __name__ == "__main__":
    main()
