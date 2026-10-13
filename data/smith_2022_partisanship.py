#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/8V9FDH
# DOI: 10.7910/DVN/8V9FDH (deposit; the record names no paper DOI)
#   Smith, K. (2022). Replication Data for: Multi-dimensional partisanship shapes climate
#   policy support and behaviors. Harvard Dataverse, V2. (Mayer & Smith.)
# Data: MayerSmithPartisanshipCC_DATA.tab (format=original -> .dta): 1,604 US online-panel
#       respondents x 41 labelled columns. Three item blocks on a single scale each:
#   smith_2022_trust               trust in 7 targets (president .. people met for the first
#                                  time), 1 no trust at all .. 7 completely trust; 99 (don't
#                                  know) -> missing
#   smith_2022_expressive_partisan eff_part1..8, 8 expressive-partisanship statements,
#                                  1 strongly disagree .. 5 strongly agree
#   smith_2022_negative_partisan   neg_part1..5, out-party trait ratings (immoral, lazy,
#                                  close-minded, less intelligent, dishonest), 1 a lot less ..
#                                  5 a lot more
# Skipped: sci_trust_* (4 items), clim_pol_* (3) and the 4 willingness-to-act items (mixed
#   formats, 3-4 items each), clim_con, party_id and the demographics not carried.
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: not shipped. Variable labels are short tags ("Say We", "Opinion polls",
#   "Immoral"), not the administered statements; value labels are complete. The wording is
#   in the paper's supplementary questionnaire.
# Covariates: cov_age (6 bands), cov_female, cov_race_ethnicity, cov_region, cov_educ,
#   cov_income, cov_party_id (7-point).

RAW_KEY = "10.7910_dvn_8v9fdh"
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

DOI = "10.7910/DVN/8V9FDH"
COVS = {"age": "cov_age", "female": "cov_female", "racethn": "cov_race_ethnicity",
        "region": "cov_region", "educ": "cov_educ", "income": "cov_income",
        "party_id": "cov_party_id"}


def main() -> None:
    d, meta = pyreadstat.read_dta(str(dv_fetch(DOI, "MayerSmithPartisanshipCC_DATA.dta")))
    assert len(d) == 1604
    d = d.rename(columns=COVS)
    d.insert(0, "id", range(1, len(d) + 1))
    cov = list(COVS.values())
    trust = [c for c in d.columns if c.startswith("trust_")]
    eff = [f"eff_part{k}" for k in range(1, 9)]
    neg = [f"neg_part{k}" for k in range(1, 6)]
    assert len(trust) == 7
    t = d[["id"] + cov + trust].copy()
    t[trust] = t[trust].astype("float").replace(99.0, float("nan"))
    emit({
        "smith_2022_trust": (to_long(t, trust, extra=cov), list(range(1, 8))),
        "smith_2022_expressive_partisan": (to_long(d, eff, extra=cov), [1, 2, 3, 4, 5]),
        "smith_2022_negative_partisan": (to_long(d, neg, extra=cov), [1, 2, 3, 4, 5]),
    })


if __name__ == "__main__":
    main()
