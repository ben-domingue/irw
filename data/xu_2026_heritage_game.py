#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.32238702.v1
# DOI: 10.6084/m9.figshare.32238702.v1 (dataset; the record names no paper)
#   Xu, Mingjie (2026). Questionnaire on Cultural Heritage Simulation Game Experience and
#   Real-World Cultural Participation Intentions [Dataset]. figshare.
# Data: Cleaned_Dataset.xlsx: 414 Chinese respondents who played a cultural-heritage
#       simulation game; 37 items whose column headers are the administered Chinese stems,
#       in the record's construct order: perceived interactivity (3), aesthetic experience
#       (4), presence (3), emotional engagement (3), perceived value (3), perceived
#       authenticity (5), perceived substitutability (4), perceived complementarity (3),
#       offline visit intention (3), heritage protection willingness (3), cultural
#       dissemination willingness (3). Observed values run 1-7 (substitutability 1-5).
# License: CC BY 4.0 (figshare record).
#
# Item text: shipped (headers are the administered Chinese stems; IRW English
#   translation). Built by automated_finding/itemtext_verification/make_itemtext_xu_2026.py.
#
# Tables (item = construct code + position, assigned by column order; the code->header map
#   is printed and reused by the item text builder):
#   xu_2026_game_experience   INTER1-3 AE1-4 PRES1-3 EMO1-3 VAL1-3 AUTH1-5 (21 items, 1-7)
#   xu_2026_substitutability  SUB1-4 (1-7 scale, observed 1-5)
#   xu_2026_participation     COMP1-3 VISIT1-3 PROT1-3 DISS1-3 (12 items, 1-7)
# Covariates: cov_gender, cov_age_group, cov_education (Chinese strings as deposited).
# id: row index of the sheet.

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

RAW_DIR = RAW_ROOT / "10_6084_m9_figshare_32238702_v1"
BLOCKS = [("INTER", 3), ("AE", 4), ("PRES", 3), ("EMO", 3), ("VAL", 3), ("AUTH", 5), ("SUB", 4),
          ("COMP", 3), ("VISIT", 3), ("PROT", 3), ("DISS", 3)]
TABLES = {"xu_2026_game_experience": ["INTER", "AE", "PRES", "EMO", "VAL", "AUTH"],
          "xu_2026_substitutability": ["SUB"],
          "xu_2026_participation": ["COMP", "VISIT", "PROT", "DISS"]}


def code_map(headers) -> dict:
    """header -> code, in deposit order."""
    out, i = {}, 0
    for pre, n in BLOCKS:
        for k in range(1, n + 1):
            out[headers[i]] = f"{pre}{k}"
            i += 1
    assert i == len(headers) == 37
    return out


def main() -> None:
    d = pd.read_excel(figshare_fetch(32238702, "Cleaned_Dataset.xlsx", RAW_DIR))
    assert len(d) == 414
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns={"性别": "cov_gender", "年龄": "cov_age_group", "学位": "cov_education"})
    covs = ["cov_gender", "cov_age_group", "cov_education"]
    heads = [c for c in d.columns if c not in covs + ["id"]]
    cm = code_map(heads)
    for h, c in cm.items():
        print(f"  {c}: {h}")
    out = {}
    for name, pres in TABLES.items():
        cols = [h for h in heads if any(cm[h].startswith(p) and cm[h][len(p):].isdigit() for p in pres)]
        codes = [cm[h] for h in cols]
        out[name] = (long(d, cols, covs, valid=range(1, 8), rename=cm), pv_for(codes, range(1, 8)))
    emit(out)


if __name__ == "__main__":
    main()
