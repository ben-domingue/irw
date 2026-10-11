#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/NWYX4N
# DOI: 10.7910/DVN/NWYX4N (Eugene-Springfield Community Sample collection, dataset (21))
#   Goldberg, L. R. (2018). (21) Personality, Emotions, and Attitudes (PEA). Eugene-
#   Springfield Community Sample. Harvard Dataverse, V1.
# Data: PEA.tab (format=original -> PEA.sav): 749 ESCS participants x 350 columns, every
#       column carrying a variable label and (nearly) all a value-label set. The questionnaire
#       is a set of blocks on different response formats; data/goldberg_2018_escs.py excluded
#       it as mixed, and this script splits it by column family and scale:
#   goldberg_2018_pea              b001..b178, 178 statements, 1 very inaccurate .. 5 very
#                                  accurate (the "b" block mixes emotional-expressivity,
#                                  dissociation, absorption and schizotypy-type statements)
#   goldberg_2018_pea_health       hlth01..hlth23, 23 health-behaviour statements, 1-5 accuracy
#   goldberg_2018_pea_belief       belief01..belief30, 30 magical/paranormal-belief statements,
#                                  1 strongly disagree .. 5 strongly agree
#   goldberg_2018_pea_gambling     gambl01..gambl14, 14 gambling activities, 1 never .. 5
#                                  frequently in the past year
#   goldberg_2018_pea_reading      read01..read08, 8 reading materials, 1 never .. 5 every day
#   goldberg_2018_pea_childexp     chldexp1..chldexp8, 8 childhood-experience statements,
#                                  1 never .. 5 almost always
#   goldberg_2018_pea_experiences  perexp01..perexp24, 24 adverse life events, 1 never /
#                                  2 once or twice / 3 more than once or twice
# Skipped: comp*, vit*, drive*, persq* (computer use, vitamins, driving, sexual orientation:
#   single questions on their own formats), supp*/alth* (check-all boxes coded 1 only, no 0),
#   relstyl1..4 (4 items, 7-point).
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: not shipped. Variable labels are present for every item but are SPSS-truncated
#   upper-case paraphrases, many cut off with ".." ("RARELY GET BORED BECAUSE I START
#   DAYDREAMING WHEN..BORING"); value labels are complete. The full wording is in the
#   collection's TechnicalReport_ESCS.doc / the original questionnaire, not in this file.
#
# Covariates joined from the collection's demographics file (DVN/VGMXJX), as in
# goldberg_2018_escs.py: cov_sex, cov_age, cov_educ, cov_ethnic, cov_employ, cov_marital.

RAW_KEY = "10.7910_dvn_nwyx4n"
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

DOI = "10.7910/DVN/NWYX4N"
DEMOGRAPHICS = ("10.7910/DVN/VGMXJX", "demographics-1.sav")  # the unsuffixed copy is a .por
COVS = {"SEX": "cov_sex", "AGE": "cov_age", "EDUC": "cov_educ", "ETHNIC": "cov_ethnic",
        "EMPLOY": "cov_employ", "MARITAL": "cov_marital"}
BLOCKS = {  # table suffix -> (column prefix, permitted values)
    "": ("b", [1, 2, 3, 4, 5]),
    "_health": ("hlth", [1, 2, 3, 4, 5]),
    "_belief": ("belief", [1, 2, 3, 4, 5]),
    "_gambling": ("gambl", [1, 2, 3, 4, 5]),
    "_reading": ("read", [1, 2, 3, 4, 5]),
    "_childexp": ("chldexp", [1, 2, 3, 4, 5]),
    "_experiences": ("perexp", [1, 2, 3]),
}


def demographics() -> pd.DataFrame:
    p = dv_fetch(*DEMOGRAPHICS, raw_dir=RAW_DIR.parent / "10.7910_dvn_vgmxjx")
    dem, _ = pyreadstat.read_sav(str(p))
    dem.columns = [c.upper() for c in dem.columns]
    dem = dem.rename(columns={"ID": "id"})
    return dem[["id"] + [c for c in COVS if c in dem]].rename(columns=COVS)


def main() -> None:
    d, meta = pyreadstat.read_sav(str(dv_fetch(DOI, "PEA.sav")))
    assert d["id"].is_unique and len(d) == 749
    d = d.merge(demographics(), on="id", how="left")
    cov = [c for c in d.columns if c.startswith("cov_")]
    used, tables = set(), {}
    for suffix, (prefix, pv) in BLOCKS.items():
        cols = [c for c in d.columns if c.startswith(prefix) and c[len(prefix):].isdigit()]
        for c in cols:
            assert d[c].dropna().isin(pv).all(), (c, sorted(d[c].dropna().unique()))
        used |= set(cols)
        tables["goldberg_2018_pea" + suffix] = (to_long(d, cols, extra=cov), pv)
    skipped = [c for c in d.columns if c not in used and c != "id" and not c.startswith("cov_")]
    print(f"skipping {len(skipped)} columns: {skipped}")
    assert len(used) == 178 + 23 + 30 + 14 + 8 + 8 + 24
    emit(tables)


if __name__ == "__main__":
    main()
