#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/XOPDQ5
# DOI: 10.7910/DVN/XOPDQ5 (dataset; the record names no published paper)
#   Duraj, A., & Trusz, S. (2026). Expectancies of Significant Others, Students' Mathematics
#   Anxiety, and Their Mathematics Achievement: A Longitudinal Study - Dataset. Harvard
#   Dataverse, V1.
# Data: Expectancies_Anxiety_LongitudinalSt_N524.sav (the .xlsx is the same table): 524 Polish
#       lower-secondary students (13-15 at wave 1) measured twice (M1, M2) on the 9-item
#       Abbreviated Math Anxiety Scale (AMAS, 1-5) and three 13-item expectancy scales -- PE
#       parents', TE teachers' and PEE peers' expectancies of the student's mathematics, 1-4 --
#       plus a wave-3 mathematics exam score (E8). Columns PE2_M2 and PEE2_M2 sit inside the M1
#       block and are the wave-1 items (the real wave-2 columns are PE2_M2_A / PEE2_M2_A, whose
#       SPSS label is "PE2_M2"); "@_M1" is PE10 at wave 1 (between PE9_M1 and PE11_M1). The
#       *_r / *r columns are the authors' reverse-scored copies (checked: PE1_r_M1 = 5 - PE1_M1)
#       and the *_Average columns are scale means; neither is shipped. A single 5 on a 1-4 item
#       (TE1_M2) is dropped as a data-entry error.
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: not shipped -- the .sav has no variable labels and no value labels for any
#   column (both levels checked; the .xlsx headers are the same codes). The AMAS is Hopko et
#   al. (2003); the PE/TE/PEE stems are the authors' own Polish items and are not in the
#   deposit.
#
# Tables (item = the scale code and item number, wave 1/2):
#   duraj_2026_amas  AMAS1..AMAS9, resp 1-5          duraj_2026_pe   PE1..PE13, resp 1-4
#   duraj_2026_te    TE1..TE13, resp 1-4              duraj_2026_pee  PEE1..PEE13, resp 1-4
# Covariates: cov_age (years at wave 1), cov_gender (1 male, 2 female), cov_school_location
#   (Village / Town to 50k / Town to 100k / Town over 100k citizens), cov_math_score (E8,
#   the wave-3 mathematics exam score).
# id: the deposit's Nb (1..524; the "Id" column is a student code and is not shipped).

import os
import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "raw"))
RAW_DIR = RAW_ROOT / "10_7910_DVN_XOPDQ5"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


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


SCALES = {  # table suffix -> (prefix, n items, valid range)
    "amas": ("AMAS", 9, (1, 5)),
    "pe": ("PE", 13, (1, 4)),
    "te": ("TE", 13, (1, 4)),
    "pee": ("PEE", 13, (1, 4)),
}
# source column holding item k of a scale at wave w, where the name is not <prefix><k>_M<w>
ODD = {("PE", 2, 1): "PE2_M2", ("PE", 2, 2): "PE2_M2_A", ("PE", 10, 1): "@_M1",
       ("PEE", 2, 1): "PEE2_M2", ("PEE", 2, 2): "PEE2_M2_A"}


def main() -> None:
    d, _ = pyreadstat.read_sav(str(dv_fetch("10.7910/DVN/XOPDQ5",
                                            "Expectancies_Anxiety_LongitudinalSt_N524.sav", RAW_DIR)))
    assert len(d) == 524 and d["Nb"].is_unique
    d["id"] = d["Nb"].astype(int)
    d["cov_age"] = d["Age_M1"].astype("Int64")
    d["cov_gender"] = d["Gender1M2F"].astype("Int64")
    d["cov_school_location"] = d["SchoolLocation"]
    d["cov_math_score"] = d["E8"].astype("Int64")
    covs = ["cov_age", "cov_gender", "cov_school_location", "cov_math_score"]
    used = set()
    out = {}
    for suffix, (prefix, n, (lo, hi)) in SCALES.items():
        parts = []
        for wave in (1, 2):
            cols = {}
            for k in range(1, n + 1):
                c = ODD.get((prefix, k, wave), f"{prefix}{k}_M{wave}")
                assert c in d.columns, c
                cols[c] = f"{prefix}{k}"
            used |= set(cols)
            t = d[["id"] + covs + list(cols)].melt(id_vars=["id"] + covs, var_name="item",
                                                 value_name="resp").dropna(subset=["resp"])
            t["item"] = t["item"].map(cols)
            t["wave"] = wave
            bad = ~t["resp"].between(lo, hi)
            if bad.any():
                print(f"    {suffix} wave {wave}: dropping {int(bad.sum())} value(s) outside {lo}-{hi}:",
                      t.loc[bad, "resp"].tolist())
                t = t[~bad]
            parts.append(t)
        t = pd.concat(parts, ignore_index=True)
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp", "wave"] + covs].sort_values(["id", "wave", "item"]).reset_index(drop=True)
        out[f"duraj_2026_{suffix}"] = (t, {f"{prefix}{k}": set(range(lo, hi + 1)) for k in range(1, n + 1)})
    # every source column is either shipped, a covariate/id, or a known derived column
    skipped = [c for c in d.columns if c not in used and c not in
               ("Nb", "SchoolLocation", "Id", "V4", "Age_M1", "Gender1M2F", "E8", "id", *covs)]
    for c in skipped:
        assert re.search(r"(_r|r)_?M\d$|Average|^Measurement|^PE1r_M2$|^TE\d+r_M2$|^PEE\d+r_?M2$", c) \
            or d[c].isna().all(), c
    print("    skipped derived columns:", len(skipped))
    emit(out)


if __name__ == "__main__":
    main()
