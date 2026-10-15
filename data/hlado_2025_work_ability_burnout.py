#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/8RGHK6
# DOI: 10.7910/DVN/8RGHK6 (data); paper: Hlaďo, Lintner & Juhaňák, "Bidirectional Relationship Between
#   Perceived Work Ability and Burnout: Evidence from a Two-Wave Study among Teachers" (JOOP, 2025)
# Data: APWH_Dataset.xlsx, 853 Czech primary and lower-secondary teachers, two waves one year apart
#       (T2 n = 481): T1/T2_Burnout_1-14 (14 burnout items, 1-7) and T1/T2_TWAS_01-21 (21 Teacher Work
#       Ability Scale items, 1-7). The T2 TWAS columns are named _25/_26 where T1 has _15/_16 -- a
#       naming slip; mapped by position (the deposit's R code uses V2_TWAS_15/16). The *_score columns
#       are the authors' means.
# License: CC0 1.0 (Harvard Dataverse).
#
# Item text: not shipped -- the workbook has codes only (no stems), no codebook in the deposit; the
#   burnout measure and TWAS wording are in the JOOP paper's supplement.
#
# Tables: hlado_2025b_burnout (853 x 14, 1-7, wave 1-2), hlado_2025b_twas (853 x 21, 1-7, wave 1-2).
#   ("2025b": the same authors' other deposit, DVN/WABYKR with 613 teachers, already ships as
#   hlado_2025_burnout / hlado_2025_ptwa; this is a different sample and study.)
# Covariates: cov_gender (female/male/other), cov_age (years), cov_years_practice,
#   cov_job_position (primary teacher / lower secondary teacher / undifferentiated).
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

RAW_DIR = RAW_ROOT / "dv_8RGHK6"
FNAME = "APWH_Dataset.xlsx"
POS = {"primary teacher": "primary", "lower secondary teacher": "lower_secondary", "učitel/ka nerozlišeno": "undifferentiated"}


def main() -> None:
    d = pd.read_excel(dv_fetch("10.7910/DVN/8RGHK6", FNAME, RAW_DIR))
    assert len(d) == 853
    d["id"] = d.index + 1
    d["cov_gender"] = d["Gender"]
    d["cov_age"] = d["Age"].astype("Int64")
    d["cov_years_practice"] = d["Years_of_practice"].astype("Int64")
    d["cov_job_position"] = d["Job_position"].map(POS)
    assert d["cov_job_position"].notna().all()
    covs = ["cov_gender", "cov_age", "cov_years_practice", "cov_job_position"]
    out = {}
    for name, prefix, n, fmt in [("burnout", "Burnout", 14, "{}_Burnout_{}"), ("twas", "TWAS", 21, "{}_TWAS_{:02d}")]:
        parts = []
        for w, tag in [(1, "T1"), (2, "T2")]:
            cols = [fmt.format(tag, i) for i in range(1, n + 1)]
            if tag == "T2" and prefix == "TWAS":
                cols = [c.replace("T2_TWAS_15", "T2_TWAS_25").replace("T2_TWAS_16", "T2_TWAS_26") for c in cols]
            ren = {c: f"{prefix.lower()}_{i:02d}" for i, c in enumerate(cols, 1)}
            dd = d[["id", *covs, *cols]].copy()
            dd["wave"] = w
            parts.append(long(dd, cols, covs, valid=range(1, 8), extra=["wave"], rename=ren))
        t = pd.concat(parts, ignore_index=True)
        out[f"hlado_2025b_{name}"] = (t, pv_for(sorted(t["item"].unique()), range(1, 8)))
    emit(out)


if __name__ == "__main__":
    main()
