#!/usr/bin/env python3
# Source: https://zenodo.org/records/18938607
# DOI: 10.5281/zenodo.18938607
# Data: DATASET.xlsx, sheet "Full dataset" (the EFA/CFA sheets are analysis subsets of the
#   same SAT items and are not re-shipped)
# License: CC BY 4.0 (verified on the Zenodo record page / API: license id cc-by-4.0)
# Reference: Duplaga, M. (2026). The relationship between health literacy and satisfaction
#   with medical care in parents of children with chronic gastrointestinal diseases. Zenodo.
# Item text: not shipped. The deposit DOES carry a codebook -- the "Variables" sheet of the
#   same workbook -- and it was read in full: it gives each variable's response categories
#   (used here to find the HL "not applicable" code) but names the items only positionally
#   ("Perceived stress scale - Item1", "Health literacy questionnaire - Item4"). The .xlsx
#   has no variable or value labels (not an SPSS file), so the only label level available is
#   that sheet, and it carries no stems. The wording lives in the published PSS-10,
#   HLS-EU-Q16 and eHEALS instruments, which the deposit's CC BY does not cover.
import os
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = Path(os.environ.get(
    "IRW_OUT_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s2"))
CACHE = Path(os.environ.get("IRW_CACHE", "/tmp/irw_cache_s2"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch(url: str, name: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / name
    if not p.exists():
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=600) as r, open(p, "wb") as f:
            f.write(r.read())
    return p


def screen_pii(d: pd.DataFrame) -> None:
    """Print every string column and its sample values; assert the denominator is non-zero."""
    txt = [c for c in d.columns if pd.api.types.is_string_dtype(d[c])]
    print(f"  [pii] string columns examined: {len(txt)} of {d.shape[1]}")
    assert len(txt) > 0 or d.select_dtypes("object").empty, "PII screen selected no columns"
    for c in txt:
        vals = d[c].dropna().astype(str).unique()[:8]
        print(f"  [pii] {c!r}: {list(vals)}")


def emit(tables: dict) -> None:
    """name -> (long frame, permitted_values or None). QC, upload-profile validate, write."""
    names = list(tables)
    assert len(set(names)) == len(names), f"duplicate output names: {names}"
    assert max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        keys = ["id", "item"] + [c for c in ("wave", "rater") if c in t]
        assert not t.duplicated(keys).any(), name
        assert t["id"].nunique() >= 100, (name, t["id"].nunique())
        assert t["item"].nunique() >= 3, (name, t["item"].nunique())
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(
            t, label=name, profile="upload",
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
    """Melt `items` to long, drop missing, keep only codes in `valid`, order columns."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items,
               var_name="item", value_name="resp")
    if rename:
        t["item"] = t["item"].map(lambda c: rename.get(c, c))
    t["resp"] = pd.to_numeric(t["resp"], errors="coerce")
    t = t.dropna(subset=["resp"])
    if valid is not None:
        keep = t["resp"].isin(valid)
        if not keep.all():
            print(f"    dropped {int((~keep).sum())} resp outside {sorted(valid)[:1]}.."
                  f"{sorted(valid)[-1:]}")
        t = t[keep]
    order = (["id", "item", "resp"]
             + [c for c in ("wave", "treat", "rt", "date") if c in t.columns]
             + covs)
    return t[order].reset_index(drop=True)


def pvals(items, valid, rename: dict | None = None) -> dict:
    """permitted_values keyed by the shipped item code."""
    vs = sorted(float(v) for v in valid)
    return {(rename or {}).get(c, c): list(vs) for c in items}

URL = "https://zenodo.org/api/records/18938607/files/DATASET.xlsx/content"

COVS = {
    "AGE": "cov_age", "SEX": "cov_sex", "MARITAL": "cov_marital",
    "RESID": "cov_residence", "EDUC": "cov_education", "INCOME": "cov_income",
    "VOCAT": "cov_vocational_status", "EMERG": "cov_emergency_visits",
    "HOSP": "cov_hospital_admissions", "CHILDAGE": "cov_child_age",
    "CHILDDIS": "cov_child_disease_years", "CHILD_IBD": "cov_child_ibd",
    "SOCMED": "cov_social_media_use", "INTERNET": "cov_internet_use",
}
# Response categories are taken from the workbook's own "Variables" sheet.
BLOCKS = {
    # 0 decidedly unsatisfied ... 5 very satisfied
    "duplaga_2026_care_satisfaction": ([f"SAT{i}" for i in range(1, 11)], range(0, 6)),
    # 0 never ... 4 very often
    "duplaga_2026_pss10": ([f"PSS_{i}" for i in range(1, 11)], range(0, 5)),
    # 1 impossible ... 4 very easy; 5 = "not applicable or difficult to say" is a
    # non-response, not a fifth step on the scale, so those item-responses are dropped.
    "duplaga_2026_hls_eu_q16": ([f"HL{i}" for i in range(1, 17)], range(1, 5)),
    # 1 decidedly disagree ... 5 decidedly agree
    "duplaga_2026_eheals_parents": ([f"EH{i}" for i in range(3, 11)], range(1, 6)),
}
SKIPPED = {
    "SATISF_SCORE": "satisfaction scale mean (composite)",
    "PSS_SCORE": "perceived stress scale mean (composite)",
    "HLCATEG": "health literacy collapsed into 4 categories (derived)",
    "EHLSCORE": "e-health literacy mean (composite)",
    "EH1": "'EHEALS1 - initial question 1' -- a usefulness-of-the-internet question on its "
           "own 1-5 usefulness scale, not an eHEALS item",
    "EH2": "'EHEALS1 - initial question 2' -- an importance question on its own 1-5 "
           "importance scale; with EH1 it would be a 2-item file, below the 3-item floor",
}


def convert() -> None:
    p = fetch(URL, "zenodo_18938607_DATASET.xlsx")
    d = pd.read_excel(p, sheet_name="Full dataset")
    screen_pii(d)
    src = list(d.columns)

    d = d.rename(columns={"ID": "id"})
    assert d["id"].nunique() == len(d), "ID is not one row per respondent"
    print(f"  respondents={d['id'].nunique()}")

    d = d.rename(columns=COVS)
    covs = sorted(COVS.values())

    used = set()
    tables = {}
    for name, (items, valid) in BLOCKS.items():
        assert all(c in d.columns for c in items), name
        used.update(items)
        tables[name] = (long(d, items, covs, valid=set(float(v) for v in valid)),
                        pvals(items, valid))

    for c in src:
        if c == "ID" or c in COVS or c in used:
            continue
        assert c in SKIPPED, f"unaccounted source column: {c}"
        print(f"  [skip] {c}: {SKIPPED[c]}")
    assert set(src) == {"ID"} | set(COVS) | used | set(SKIPPED)

    emit(tables)


if __name__ == "__main__":
    convert()
