#!/usr/bin/env python3
# Source: https://plos.figshare.com/articles/dataset/Burnout_study_data_June_2024_/28336250
# DOI: 10.1371/journal.pone.0299173 (data: 10.1371/journal.pone.0299173.s002)
# Data: pone.0299173.s002.xlsx, sheet "Biggs et al 2024"
# License: CC BY 4.0 (verified on the figshare record: license "CC BY 4.0")
# Reference: Biggs, D., Blackburn, L., Black, C., & Shanmugam, S. (2024). PLOS ONE.
# Item text: not shipped. The Supporting Information workbook has one sheet of bare
#   column headers -- there are no SPSS/Stata variable or value labels to read (it is an
#   .xlsx), and the headers are positional codes (P1SelfO ... P15OO, MI1 ... M10, B1 ... B14)
#   that name a subscale but not a stem. Checked: the sheet's header row and the deposit's
#   file list (the article's only other SI file is the questionnaire-free protocol). The
#   wording lives in the three published instruments named in the article's Methods
#   (multidimensional perfectionism, moral injury, and the burnout measure), each a
#   third-party scale the deposit's CC BY does not reach.
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

URL = "https://ndownloader.figshare.com/files/52107023"

COVS = {
    "physioarea": "cov_physio_area",
    "employer": "cov_employer",
    "hoursperweek": "cov_hours_per_week",
    "hoursoutsideofcontract": "cov_works_outside_contract",
    "howmanyhoursoutside": "cov_hours_outside_contract",
    "howmanypatientsperday": "cov_patients_per_day",
    "currentqualificationlevel": "cov_qualification_level",
    "banding": "cov_banding",
    "howlonghaveyouworkedinyourcurrentposition": "cov_time_in_position",
    "gender": "cov_gender",
    "age": "cov_age",
    "ethnicity": "cov_ethnicity",
}
BLOCKS = {
    "biggs_2024_perfectionism": (
        ["P1SelfO", "P2SelfO", "P3SelfO", "P4SelfO", "P5SelfO",
         "P6SocO", "P7SocO", "P8SocO", "P9SocO", "P10SocO",
         "P11OO", "P12OO", "P13OO", "P14OO", "P15OO"], range(1, 8)),
    "biggs_2024_moral_injury": (
        [f"MI{i}" for i in range(1, 10)] + ["M10"], range(1, 8)),
    "biggs_2024_burnout": (
        [f"B{i}" for i in range(1, 15)], range(1, 6)),
}
SKIPPED = {
    "MIQ": "single 1-5 overall moral-injury question on its own scale; a 1-item scale "
           "is not shippable and it does not belong on the 1-7 MI block",
    "MIT": "moral-injury total (composite)",
    "SelfOP": "self-oriented perfectionism subscale score (composite)",
    "SocOP": "socially-prescribed perfectionism subscale score (composite)",
    "OtherOP": "other-oriented perfectionism subscale score (composite)",
    "physicalexhaustion": "burnout subscale score (composite)",
    "cognitiveweariness": "burnout subscale score (composite)",
    "emotionalexhaustion": "burnout subscale score (composite)",
    "totalburnout": "burnout total (composite)",
}


def convert() -> None:
    d = pd.read_excel(fetch(URL, "pone.0299173.s002.xlsx"), sheet_name="Biggs et al 2024")
    screen_pii(d)
    src = list(d.columns)

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    assert d["id"].nunique() == len(d)
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
        if c in COVS or c in used:
            continue
        assert c in SKIPPED, f"unaccounted source column: {c}"
        print(f"  [skip] {c}: {SKIPPED[c]}")
    assert set(src) == set(COVS) | used | set(SKIPPED)

    emit(tables)


if __name__ == "__main__":
    convert()
