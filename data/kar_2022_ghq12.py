#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/VJEEIE (Harvard Dataverse)
# DOI: 10.7910/DVN/VJEEIE (dataset, 2022; Kar, Sonali). "Mental health status of Women in Reproductive age group and
#   its determinants in Rural Odisha, India using GHQ 12 questionnaire" -- N = 1260 women, 7 districts of Odisha.
# Data: GHQ.xlsx, sheet GHQ. One row per respondent, columns 1-12 = the GHQ-12 items scored 0-3 (symptom direction;
#   the positively worded items are already reverse-scored, items 1-11 correlate +0.17 to +0.58 with one another).
#   District header rows ('01. Khurdha', ...) sit between blocks of respondents and are used for cov_district.
#   GHQ_Total (sum of items) and Interpretation (cut-off category) are derived and not shipped.
#   Item 12 NOT shipped: it correlates -0.01 to -0.19 with every other item, while the deposit's own GHQ_Total adds
#   it as stored, so it is the one item left unreversed (a keying slip); 11 items ship. One out-of-range code
#   (a 4 on item 8) is dropped as an observation; one blank (item 7) is dropped.
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none in GHQ.xlsx (serial number per facility only, not unique across districts). id = row index (1-based).
#   The deposit's separate Mastersheet.xlsx (not used) holds partly masked mobile numbers and village names.
# Age: not in GHQ.xlsx. Mastersheet ages run 1-232 (typos) with median 26; sample is women of reproductive age.
# Item text: the deposit has the questionnaire as a PDF (COMPLETE QUESTION WRA MH.pdf), not transcribed here.
#
# Table: kar_2022_ghq12 (11 items, 0-3). Covariate: cov_district.
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_C_2026-10-16"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset in its original format."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"] if f["label"] == fname][0]
        r = requests.get(f"https://{host}/api/access/datafile/{fid}", params={"format": "original"},
                         headers=UA, timeout=300)
        r.raise_for_status()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values). QC, validate, write."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert max(map(len, tables)) <= 40, name
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 8, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")


def main() -> None:
    p = dv_fetch("10.7910/DVN/VJEEIE", "GHQ.xlsx", RAW_ROOT / "vjeeie")
    raw = pd.read_excel(p, sheet_name="GHQ")
    first = raw.columns[0]
    district = None
    rows = []
    for _, r in raw.iterrows():
        if pd.isna(r[1]):
            if isinstance(r[first], str) and r[first][:2].isdigit():
                district = r[first].split(". ", 1)[1].strip()
            continue
        rows.append({"cov_district": district, **{i: r[i] for i in range(1, 13)}})
    d = pd.DataFrame(rows)
    assert len(d) == 1260 and d["cov_district"].nunique() == 7 and d["cov_district"].notna().all()
    d["id"] = range(1, len(d) + 1)
    cols = {i: f"ghq_{i}" for i in range(1, 12)}  # item 12 dropped, see header
    t = d.melt(id_vars=["id", "cov_district"], value_vars=list(cols), var_name="item", value_name="resp")
    t["item"] = t["item"].map(cols)
    t = t[t["resp"].between(0, 3)]  # drops blanks and the single out-of-range 4
    assert (t["resp"] % 1 == 0).all()
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=list(cols.values()), ordered=True)
    t = t[["id", "item", "resp", "cov_district"]].sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    emit({"kar_2022_ghq12": (t, {i: {0, 1, 2, 3} for i in cols.values()})})


if __name__ == "__main__":
    main()
