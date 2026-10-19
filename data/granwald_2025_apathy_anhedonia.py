#!/usr/bin/env python3

# Source: https://zenodo.org/records/17514160
# DOI: 10.5281/zenodo.17514160 (dataset)
#   Granwald, Tobias; Triolo, Federico; Lengyel, Mate; Dayan, Peter; Guitart Masip, Marc
#   (2025). Exploring the Link Between a Prior for Active Avoidance and Apathy, Anhedonia,
#   and Depression: A Network Analysis [Dataset]. Zenodo.
#   Paper: 10.1016/j.bpsc.2025.09.013 (Biological Psychiatry: CNNI).
# Data: "extracted_data_networkPriors.csv": 528 online participants, six published
#       questionnaires deposited at the item level.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. The column codes are positional within each named instrument
#   (PHQ_1 .. SHPS_14) and the deposit holds no codebook or questionnaire, so the wording
#   would have to come from each instrument's published source and be matched by position
#   -- which is exactly the mapping this pipeline is told not to reconstruct. The text is
#   in the published instruments: PHQ-9 (Kroenke 2001), CES-D (Radloff 1977), Zung SDS
#   (Zung 1965), BIS/BAS (Carver & White 1994), AMI (Ang 2017), SHPS (Snaith 1995).
#
# Six tables, one per instrument, each with its own response width:
#   granwald_2025_phq9      9 items, 0-3
#   granwald_2025_cesd     20 items, 0-3
#   granwald_2025_zung_sds 20 items, 1-4
#   granwald_2025_bis_bas  24 items, 1-4
#   granwald_2025_ami      18 items, 0-4
#   granwald_2025_shps     14 items, 0-3
# Not shipped: muAll, the paper's fitted per-participant prior parameter -- a model
#   estimate, not a response.
# Covariates: cov_age, cov_sex, cov_nationality, cov_attention_check_fails (AC_fails).
# id: the deposit's subjID (528 distinct over 528 rows).
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_17514160"
BLOCKS = {
    "granwald_2025_phq9": ("PHQ", 9, range(0, 4)),
    "granwald_2025_cesd": ("CESD", 20, range(0, 4)),
    "granwald_2025_zung_sds": ("SDS", 20, range(1, 5)),
    "granwald_2025_bis_bas": ("BIS_BAS", 24, range(1, 5)),
    "granwald_2025_ami": ("AMI", 18, range(0, 5)),
    "granwald_2025_shps": ("SHPS", 14, range(0, 4)),
}
COVS = {"age": "cov_age", "sex": "cov_sex", "nationality": "cov_nationality",
        "AC_fails": "cov_attention_check_fails"}


def main() -> None:
    d = pd.read_csv(zenodo_fetch(17514160, "extracted_data_networkPriors.csv", RAW_DIR))
    assert len(d) == 528, len(d)
    src = list(d.columns)
    sets = {}
    for name, (pre, n, valid) in BLOCKS.items():
        cols = [f"{pre}_{i}" for i in range(1, n + 1)]
        assert all(c in src for c in cols), (name, cols)
        sets[name] = (cols, valid)
    books(src, {
        "shipped": [c for cols, _ in sets.values() for c in cols],
        "covariate": list(COVS),
        "respondent id": ["subjID"],
        "fitted model parameter, not a response": ["muAll"],
    })
    d = d.rename(columns={"subjID": "id", **COVS})
    covs = list(COVS.values())
    assert d["id"].nunique() == len(d)
    emit({name: (long(d, cols, covs, valid=valid), pv_for(cols, valid))
          for name, (cols, valid) in sets.items()})


if __name__ == "__main__":
    main()
