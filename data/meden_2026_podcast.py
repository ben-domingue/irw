#!/usr/bin/env python3
# Source: https://zenodo.org/records/22999275
# DOI: 10.5281/zenodo.22999275 (dataset; the record names no paper)
#   Meden, Ema (2026). Podcast Listening, Trust, and Media Literacy among Slovenian Adults
#   [Dataset]. Zenodo.
# Data: Podkasti.sav: 640 rows (604 complete) from an online survey of adult podcast
#       listeners in Slovenia. Three frequency blocks on a 1-5 scale (Nikoli/Redko/Vcasih/
#       Pogosto/Zelo pogosto = never .. very often), variable labels in Slovenian:
#       VAR00032-37 "Ucne aktivnosti" (learning activities while listening, 6 items),
#       VAR00038-41 "Globina" (depth of processing, 4), VAR00042-47 "Kriticno" (critical
#       engagement, 6). The NUA/NGU/NKR columns are the same items collapsed to 3 levels.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. Variable labels are abbreviated prompts ("Ucne aktivnosti:
#   zapiski" = learning activities: notes), not the administered stems; value labels
#   carry the 1-5 anchors. No questionnaire is deposited. Checked both label levels.
#
# Tables (item = the deposit's variable name): meden_2026_podcast_learning (VAR00032-37),
#   meden_2026_podcast_depth (VAR00038-41), meden_2026_podcast_critical (VAR00042-47); 1-5.
# Covariates: cov_age_group (1 <18 .. 5), cov_gender (1 male, 2 female), cov_education
#   (1-4), cov_listening_frequency (VAR00001, 1-4), as coded in the .sav.
# id: row index of the .sav.

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

import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "10_5281_zenodo_22999275"
BLOCKS = {"meden_2026_podcast_learning": [f"VAR000{i}" for i in range(32, 38)],
          "meden_2026_podcast_depth": [f"VAR000{i}" for i in range(38, 42)],
          "meden_2026_podcast_critical": [f"VAR000{i}" for i in range(42, 48)]}


def main() -> None:
    d, meta = pyreadstat.read_sav(str(zenodo_fetch(22999275, "Podkasti.sav", RAW_DIR)))
    assert len(d) == 640
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns={"VAR00048": "cov_age_group", "VAR00049": "cov_gender",
                          "VAR00050": "cov_education", "VAR00001": "cov_listening_frequency"})
    covs = ["cov_age_group", "cov_gender", "cov_education", "cov_listening_frequency"]
    for c in covs:
        d[c] = d[c].astype("Int64")
    out = {}
    for name, items in BLOCKS.items():
        for c in items:
            assert set(meta.variable_value_labels[c]) == {1.0, 2.0, 3.0, 4.0, 5.0}, c
        out[name] = (long(d, items, covs, valid=range(1, 6)), pv_for(items, range(1, 6)))
    emit(out)


if __name__ == "__main__":
    main()
