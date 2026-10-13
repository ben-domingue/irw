#!/usr/bin/env python3
# Source: https://zenodo.org/records/5003916 (Dryad mirror of doi:10.5061/dryad.wm37pvmhk)
# DOI: 10.5061/dryad.wm37pvmhk
#   Stanford, M., & Jong, J. (2019). Beyond Buddhism and animism: A psychometric test of
#   the structure of Burmese Theravada Buddhism [Data set]. Dryad. (PLOS ONE 2019,
#   10.1371/journal.pone.0226414.)
# Data: Study_1.sav (2,285 Burmese adults x 55) and Study_2.sav (3,377 x 31). Both carry the
#       Burmese Buddhist Religiosity Scale: RF_* 21 practice-frequency items (1 never .. 8),
#       RI_* 3 interest items and RB_* 4 belief items (1-5). Study 1 adds
#       BuddhismAttitudes_1..24 (1-5, no variable labels) and both carry survey weights.
#   stanford_2019_bbrs_frequency   21 RF items, 1-8, Study 1 + Study 2 (cov_study)
#   stanford_2019_bbrs_belief      RI (3) + RB (4) items, 1-5, Study 1 + Study 2 (cov_study)
#   stanford_2019_buddhism_attitud 24 attitude statements, 1-5, Study 1 only
# Skipped: NatImagesInHome, WeeksMonk (counts), Weights.
# License: CC0 1.0 (Dryad / Zenodo record).
#
# Item text: not shipped. Variable labels are paraphrases ("Frequency of thinking about
#   Buddha"), not the administered Burmese wording, and BuddhismAttitudes_* have no variable
#   labels; value labels are complete on RF/RI/RB. The items are in the paper's S1 appendix.
# id: row index within study, offset by 10,000 for Study 2; no demographics in the files.

RAW_KEY = "10.5061_dryad.wm37pvmhk"
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
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / RAW_KEY
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def dv_fetch(doi: str, fname: str, raw_dir: Path = None,
             host: str = "dataverse.harvard.edu") -> Path:
    """Fetch a Harvard Dataverse file by its ORIGINAL name, as format=original
    (never the lossy .tab conversion)."""
    raw_dir = raw_dir or RAW_DIR
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"].get("originalFileName", f["dataFile"]["filename"]) == fname][0]
        download(f"https://{host}/api/access/datafile/{fid}?format=original", p)
    return p


def to_long(d: pd.DataFrame, items, id_col="id", extra=(), rename=None) -> pd.DataFrame:
    """Melt `items` (wide columns) to id/item/resp, carrying `extra` columns."""
    keep = [id_col] + list(extra)
    t = d[keep + list(items)].melt(id_vars=keep, value_vars=list(items),
                                   var_name="item", value_name="resp")
    if rename:
        t["item"] = t["item"].map(lambda c: rename.get(c, c))
    t = t.dropna(subset=["resp"])
    if id_col != "id":
        t = t.rename(columns={id_col: "id"})
    lead = ["id", "item", "resp"] + [c for c in ("wave", "treat", "rt", "date") if c in t.columns]
    cov = [c for c in t.columns if c.startswith("cov_")]
    tail = [c for c in ("rater", "item_family") if c in t.columns]
    return t[lead + cov + tail].reset_index(drop=True)


def emit(tables: dict) -> None:
    """tables: name -> (long df, permitted_values or None). QC + validate + write."""
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in names:
        assert not (OUT_DIR / f"{name}.csv").exists() or os.environ.get("IRW_OVERWRITE"), \
            f"{name}.csv already staged; set IRW_OVERWRITE=1 to rebuild"
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"] + [c for c in ("wave", "rater") if c in t]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, (name, t["id"].nunique())
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


import pyreadstat  # noqa: E402

BASE = "https://zenodo.org/api/records/5003916/files/{}/content"


def load(study: str) -> pd.DataFrame:
    d, meta = pyreadstat.read_sav(str(download(BASE.format(f"Study_{study}.sav"),
                                               RAW_DIR / f"Study_{study}.sav")))
    d.insert(0, "id", range(1, len(d) + 1) if study == "1" else range(10001, 10001 + len(d)))
    d["cov_study"] = int(study)
    return d


def main() -> None:
    s1, s2 = load("1"), load("2")
    rf = [c for c in s1.columns if c.startswith("RF_")]
    rib = [c for c in s1.columns if c.startswith(("RI_", "RB_"))]
    att = [f"BuddhismAttitudes_{k}" for k in range(1, 25)]
    assert len(rf) == 21 and len(rib) == 7 and all(c in s2.columns for c in rf + rib)
    both = pd.concat([s1[["id", "cov_study"] + rf + rib], s2[["id", "cov_study"] + rf + rib]])
    assert both["id"].is_unique
    for c in rf:
        assert both[c].dropna().between(1, 8).all(), c
    for c in rib + att:
        assert (both if c in rib else s1)[c].dropna().between(1, 5).all(), c
    emit({
        "stanford_2019_bbrs_frequency": (to_long(both, rf, extra=["cov_study"]), list(range(1, 9))),
        "stanford_2019_bbrs_belief": (to_long(both, rib, extra=["cov_study"]), [1, 2, 3, 4, 5]),
        "stanford_2019_buddhism_attitud": (
            to_long(s1, att, rename={c: "attitude_" + c.split("_")[1] for c in att}), [1, 2, 3, 4, 5]),
    })


if __name__ == "__main__":
    main()
