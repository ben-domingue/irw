#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/SPSS_File_for_Teachers_Grit_Self-efficacy_Motivation_and_Burnout/28052750
# DOI: 10.6084/m9.figshare.28052750.v1 (dataset, 2024-12-18; Golzar, Jawad). "SPSS File for Teachers'
#   Grit, Self-efficacy, Motivation and Burnout".
# Data: "Main Data for Models.sav", 196 teachers: TG1-TG8 grit (1-5), SE1-SE12 self-efficacy (1-5),
#       TM1-TM19 work motivation (1-5; the authors' subscale means are Intrinsic/Identified/
#       Interjected/External/Amotivation), TB1-TB22 burnout (1-5; the authors' EE/DP/RPA means
#       mark it as a 22-item MBI-Educators form). PE/CI/IS/SE/CM/... are composites, not shipped.
#       No demographics in the file.
# License: CC BY 4.0 (figshare).
#
# Item text: not shipped -- both label levels empty for every item; no instrument in the deposit.
#   The grit (Grit-S) and burnout (MBI) items are rights-register blocks in any case.
#
# Tables: golzar_2024_teacher_grit (8), golzar_2024_teacher_self_efficacy (12),
#   golzar_2024_teacher_motivation (19), golzar_2024_teacher_burnout (22); 196 ids = the file's NO column.
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
import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "C_52_28052750"
FNAME = "Main Data for Models.sav"
BLOCKS = {"teacher_grit": [f"TG{i}" for i in range(1, 9)],
          "teacher_self_efficacy": [f"SE{i}" for i in range(1, 13)],
          "teacher_motivation": [f"TM{i}" for i in range(1, 20)],
          "teacher_burnout": [f"TB{i}" for i in range(1, 23)]}


def main() -> None:
    d, meta = pyreadstat.read_sav(str(figshare_fetch(28052750, FNAME, RAW_DIR)))
    assert len(d) == 196 and d["NO"].is_unique
    d["id"] = d["NO"].astype(int)
    out = {}
    for k, cols in BLOCKS.items():
        t = long(d, cols, [], valid=range(1, 6))
        out[f"golzar_2024_{k}"] = (t, pv_for(cols, range(1, 6)))
    emit(out)


if __name__ == "__main__":
    main()
