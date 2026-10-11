#!/usr/bin/env python3
# Source: https://zenodo.org/records/21963745
# DOI: 10.5281/zenodo.21963745 (dataset; the record names no paper)
#   Fauziah, Hanna Maulani; Ekowati, Carolina Retno; Nurani, Asih; Setiawati, Rini (2026).
#   Fostering Innovative Work Behavior through Human-AI Collaboration Capability: The Roles
#   of Humble Leadership, Psychological Safety, and Intrinsic Motivation among Indonesian
#   Employees [Dataset]. Zenodo.
# Data: "Data responden kuesioner PS, IM, HL, HACC, IWB.xlsx" (Google Form export): 241
#       rows, of which 210 passed the screening questions (employee, has a supervisor,
#       uses AI at work) and answered the five scales, 1-5 agreement. Column headers are
#       the Indonesian item stems in brackets, prefixed "Part A".."Part E":
#       A humble leadership (6), B psychological safety (7), C intrinsic motivation (3),
#       D human-AI collaboration capability (6), E innovative work behavior (10).
#       The SmartPLS outputs in the record name the codes HL1-6, PS1-7, IM1-3, HACC1-6,
#       IWB1-10, in the same order as the columns.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped (column headers are the administered Indonesian stems; IRW English
#   translation). Built by automated_finding/itemtext_verification/make_itemtext_fauziah_2026.py.
#
# Tables (item = the SmartPLS code, assigned by column order within each Part):
#   fauziah_2026_humble_leadership HL1-HL6, fauziah_2026_psych_safety PS1-PS7,
#   fauziah_2026_intrinsic_motivation IM1-IM3, fauziah_2026_human_ai_collab HACC1-HACC6,
#   fauziah_2026_iwb IWB1-IWB10; all 1-5.
# Covariates: cov_age (years, as typed), cov_ai_use_frequency, cov_gender, cov_education,
#   cov_industry, cov_position (Indonesian strings as deposited).
# id: row index of the export (1..241; only screened-in rows ship).

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

RAW_DIR = RAW_ROOT / "10_5281_zenodo_21963745"
FNAME = "Data responden kuesioner PS, IM, HL, HACC, IWB.xlsx"
PARTS = {"Part A": ("HL", "fauziah_2026_humble_leadership"), "Part B": ("PS", "fauziah_2026_psych_safety"),
         "Part C": ("IM", "fauziah_2026_intrinsic_motivation"), "Part D": ("HACC", "fauziah_2026_human_ai_collab"),
         "Part E": ("IWB", "fauziah_2026_iwb")}


def item_map(cols) -> dict:
    """header -> code, by order within each Part (the SmartPLS code order)."""
    out, n = {}, {k: 0 for k in PARTS}
    for c in cols:
        for part, (pre, _) in PARTS.items():
            if str(c).startswith(part + " ["):
                n[part] += 1
                out[c] = f"{pre}{n[part]}"
    assert [n[p] for p in PARTS] == [6, 7, 3, 6, 10], n
    return out


def main() -> None:
    d = pd.read_excel(zenodo_fetch(21963745, FNAME, RAW_DIR))
    assert len(d) == 241
    d["id"] = range(1, len(d) + 1)
    im = item_map(d.columns)
    cov_src = {"Berapakah usia anda saat ini?": "cov_age", "Jenis Kelamin": "cov_gender",
               "Pendidikan Terakhir": "cov_education", "Industri": "cov_industry",
               "Posisi Saat Ini": "cov_position"}
    freq = [c for c in d.columns if str(c).startswith("Seberapa sering Anda menggunakan")][0]
    cov_src[freq] = "cov_ai_use_frequency"
    d = d.rename(columns=cov_src)
    d["cov_age"] = pd.to_numeric(d["cov_age"], errors="coerce").astype("Int64")
    covs = ["cov_age", "cov_gender", "cov_education", "cov_industry", "cov_position", "cov_ai_use_frequency"]
    items = list(im)
    answered = d[items].notna().any(axis=1)
    print(f"  {answered.sum()} of {len(d)} rows answered the scales (screened in)")
    assert answered.sum() == 210
    d = d[answered]
    out = {}
    for part, (pre, name) in PARTS.items():
        cols = [c for c in items if im[c].startswith(pre) and im[c][len(pre):].isdigit()]
        t = long(d, cols, covs, valid=range(1, 6), rename=im)
        out[name] = (t, pv_for([im[c] for c in cols], range(1, 6)))
    emit(out)


if __name__ == "__main__":
    main()
