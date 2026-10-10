#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/2HFVF7
# DOI: 10.7910/DVN/2HFVF7 (dataset; the record names no paper)
#   Ghasemy, Majid (2020). "Replication Data for: servant leadership behaviors of
#   academics with science backgrounds and their organizational outcomes (commitment,
#   satisfaction, and motivation)". Harvard Dataverse.
# Data: "499 - academics with science related backgrounds.csv" (format=original): 449
#       academics x 24 columns -- C_Tenure and 23 five-point items: CS2-CS4 and BE2-BE4
#       (the record's "two dimensions of servant leadership": conceptual skills and
#       behaving ethically, as perceived of the academics' leaders), OC1-OC6
#       (organizational commitment), JS2, JS3, JS4, JS8, JS10 (job satisfaction), WM1,
#       WM4, WM5, WM6, WM10, WM11 (work motivation). Numbering gaps are the deposit's
#       (items retained after the measurement model). No codebook.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Plain CSV: no variable labels and no value labels; headers
#   are positional codes; no questionnaire in the deposit.
#
# Tables (1-5 as stored; anchors undocumented):
#   ghasemy_2020_servant_leadership  CS2-CS4, BE2-BE4 (two dimensions of one
#                                    construct, so the multi_scale prefix warning is
#                                    expected)
#   ghasemy_2020_commitment          OC1-OC6
#   ghasemy_2020_job_satisfaction    JS2, JS3, JS4, JS8, JS10
#   ghasemy_2020_motivation          WM1, WM4, WM5, WM6, WM10, WM11
# Covariate: cov_tenure (C_Tenure, bands 1-4, labels undocumented).
# id: row index (no id column).

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
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any()
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


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=()) -> pd.DataFrame:
    """Melt, drop missing, check integer codes inside `valid`, order columns."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", "item"]).reset_index(drop=True)


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


def dryad_file(path: Path) -> Path:
    """Dryad file downloads need a browser session (an Anubis challenge, then a 403 to
    plain HTTP clients), so the file is placed by hand: open the dataset page in a
    browser, download the file, and put it at `path`."""
    if not path.exists():
        raise SystemExit(f"missing {path}: download it from the Dryad dataset page "
                         "(plain HTTP downloads are refused) and rerun")
    return path

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_2hfvf7"
FNAME = "499 - academics with science related backgrounds.csv"
P = "ghasemy_2020_"
TABLES = {"servant_leadership": ["CS2", "CS3", "CS4", "BE2", "BE3", "BE4"],
          "commitment": [f"OC{i}" for i in range(1, 7)],
          "job_satisfaction": ["JS2", "JS3", "JS4", "JS8", "JS10"],
          "motivation": ["WM1", "WM4", "WM5", "WM6", "WM10", "WM11"]}


def main() -> None:
    d = pd.read_csv(dv_fetch("10.7910/DVN/2HFVF7", FNAME, RAW_DIR), encoding="utf-8-sig")
    assert d.shape == (449, 24)
    items = [c for its in TABLES.values() for c in its]
    assert set(items) | {"C_Tenure"} == set(d.columns)
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns={"C_Tenure": "cov_tenure"})
    out = {}
    for suf, its in TABLES.items():
        out[P + suf] = (long(d, its, ["cov_tenure"], valid=range(1, 6)),
                        {i: set(range(1, 6)) for i in its})
    emit(out)


if __name__ == "__main__":
    main()
