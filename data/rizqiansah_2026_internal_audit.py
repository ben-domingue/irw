#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/gyfdrvfs7c
# DOI: 10.17632/gyfdrvfs7c (dataset, 2026-10-09; Rizqiansah, Hafizt; Hidayatullah). "E-Audit, Artificial
#   Intelligence, and Data Analytics in Internal Audit Quality: The Moderating Role of Auditor Competence".
# Data: the single .xlsx (Google-Forms export), 135 Indonesian internal auditors (ministries, SOEs, local
#       government, public accounting firms): X1.1-X1.5 e-audit, X2.1-X2.5 artificial intelligence,
#       X3.1-X3.5 data analytics, Z.1-Z.5 auditor competence, Y.1-Y.5 internal audit quality; 1-5
#       agreement. Demographics in Indonesian text.
# License: CC BY 4.0 (Mendeley Data).
#
# Item text: not shipped -- codes only (X1.1 ...), no instrument in the deposit.
#
# Tables: rizqiansah_2026_e_audit (5), rizqiansah_2026_ai (5), rizqiansah_2026_data_analytics (5),
#   rizqiansah_2026_auditor_competence (5), rizqiansah_2026_audit_quality (5); item codes x1.1 ... y.5;
#   135 ids = the file's "No Resp". Covariates: cov_education (1 Diploma, 2 S1, 3 S2, 4 S3),
#   cov_position (1 anggota tim, 2 ketua tim, 3 pengendali teknis, 4 pengendali mutu), cov_experience
#   (1 <1 year, 2 1-5, 3 6-11, 4 >11 years).
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


def dans_fetch(doi: str, fname: str, raw_dir: Path) -> Path:
    """Download one original-format file of a DANS Data Station (Dataverse) dataset."""
    return dv_fetch(doi, fname, raw_dir, host="ssh.datastations.nl")
RAW_DIR = RAW_ROOT / "C_74_gyfdrvfs7c"
FNAME = ("Data-E-Audit, Artificial Intelligence, and Data Analytics in Internal Audit Quality-The "
         "Moderating Role of Auditor Competence.xlsx")
BLOCKS = {"e_audit": "X1.", "ai": "X2.", "data_analytics": "X3.", "auditor_competence": "Z.",
          "audit_quality": "Y."}


def main() -> None:
    d = pd.read_excel(mendeley_fetch("gyfdrvfs7c", FNAME, RAW_DIR))
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == 135 and d["No Resp"].is_unique
    d["id"] = d["No Resp"].astype(int)
    d["cov_education"] = d["Pendidikan"].str.strip().map({"Diploma": 1, "S1": 2, "S2": 3, "S3": 4}).astype("Int64")
    d["cov_position"] = d["Posisi / Jabatan"].str.strip().map(
        {"Anggota Tim": 1, "Ketua Tim": 2, "Pengendali Teknis": 3, "Pengendali Mutu": 4}).astype("Int64")
    d["cov_experience"] = d["Pengalaman"].str.replace(r"\s+", "", regex=True).map(
        {"<1tahun": 1, "1-5tahun": 2, "6-11tahun": 3, ">11tahun": 4}).astype("Int64")
    covs = ["cov_education", "cov_position", "cov_experience"]
    assert d[covs].notna().all().all(), d[["Pendidikan", "Posisi / Jabatan", "Pengalaman"]].drop_duplicates()
    out = {}
    for k, pre in BLOCKS.items():
        cols = [f"{pre}{i}" for i in range(1, 6)]
        assert all(c in d.columns for c in cols), (cols, list(d.columns))
        ren = {c: c.lower() for c in cols}
        out[f"rizqiansah_2026_{k}"] = (long(d, cols, covs, valid=range(1, 6), rename=ren), pv_for(ren.values(), range(1, 6)))
    emit(out)


if __name__ == "__main__":
    main()
