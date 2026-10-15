#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/JOJAGD
# DOI: 10.7910/DVN/JOJAGD (data, 2026; Li, Lingxin). Record: "Who benefits from digitalised vocational
#   education? Interactive learning, digital competence and thinking style in China's vocational
#   colleges"; no paper DOI given.
# Data: A_Data_Final.sav, 417 final-year students at four Chinese vocational colleges (CodeCombat
#       users): PI1-13, DC1-8, JTS1-8, CT1-29, all 1-5, no variable labels and no value labels on the
#       items; the record's description does not expand the block codes (PI, DC = digital competence,
#       JTS, CT). PI/DC/JTS/CT means are the authors' scores.
# License: CC0 1.0 (Harvard Dataverse).
#
# Item text: not shipped -- both label levels empty for every item, no codebook in the deposit.
#
# Tables: li_2026_vocational_pi (417 x 13), li_2026_vocational_dc (417 x 8), li_2026_vocational_jts
#   (417 x 8), li_2026_vocational_ct (417 x 29); all 1-5. Block meaning undocumented (data note).
# Covariates: cov_gender (1 male, 2 female), cov_age (18-23), cov_major (1-4, labels in the .sav).
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

import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "dv_JOJAGD"
FNAME = "A_Data_Final.sav"
BLOCKS = {"pi": [f"PI{i}" for i in range(1, 14)], "dc": [f"DC{i}" for i in range(1, 9)],
          "jts": [f"JTS{i}" for i in range(1, 9)], "ct": [f"CT{i}" for i in range(1, 30)]}


def main() -> None:
    d, meta = pyreadstat.read_sav(str(dv_fetch("10.7910/DVN/JOJAGD", FNAME, RAW_DIR)))
    assert len(d) == 417
    assert all(not meta.column_names_to_labels.get(c) and c not in meta.variable_value_labels
               for b in BLOCKS.values() for c in b)
    d["id"] = d.index + 1
    d["cov_gender"] = d["Gender"].astype("Int64")
    d["cov_age"] = d["Age"].astype("Int64")
    d["cov_major"] = d["DM"].astype("Int64")
    covs = ["cov_gender", "cov_age", "cov_major"]
    emit({f"li_2026_vocational_{k}": (long(d, v, covs, valid=range(1, 6)), pv_for(v, range(1, 6)))
          for k, v in BLOCKS.items()})


if __name__ == "__main__":
    main()
