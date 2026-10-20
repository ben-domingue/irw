#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Data_for_validation_of_the_Malay_version_of_the_Body_Image_Scale_among_cancer_patients_in_Malaysia/29163374
# DOI: 10.6084/m9.figshare.29163374.v2
# Data: 10itemsBI.xlsx (sheet "10itemsBI")
# License: CC BY 4.0 (verified on the figshare record: license "CC BY 4.0")
# Reference: Leong Bin Abdullah, M. F. I. (2025). Data for validation of the Malay version
#   of the Body Image Scale among cancer patients in Malaysia. figshare.
# Item text: not shipped. Both label levels were checked and neither carries a stem: the
#   .xlsx has no variable or value labels at all (not an SPSS file), and its headers are
#   positional codes (BI1..BI10, AAQ1..AAQ7). The deposit's one other file, "Coding for
#   categorical variables (BIS-M).pdf", was read in full -- it codes the demographic
#   covariates only (gender, age band, race, religion, income, marriage, education, time
#   since diagnosis, cancer stage, diagnosis) and carries no item wording. The stems live in
#   the published EORTC Body Image Scale (Hopwood et al. 2001) and the Acceptance and Action
#   Questionnaire, third-party instruments the deposit's CC BY does not reach.
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

URL = "https://ndownloader.figshare.com/files/54876392"

# Covariate codes are documented in the deposit's coding PDF.
COVS = {
    "gender": "cov_gender", "age": "cov_age_band", "race": "cov_race",
    "religion": "cov_religion", "income": "cov_income", "marrige": "cov_marital",
    "education": "cov_education", "time": "cov_time_since_diagnosis",
    "stage": "cov_cancer_stage", "diagnosed": "cov_cancer_diagnosis",
}
BLOCKS = {
    "leongabdullah_2025_bis_malay": ([f"BI{i}" for i in range(1, 11)], range(1, 5)),
    "leongabdullah_2025_aaq": ([f"AAQ{i}" for i in range(1, 8)], range(1, 8)),
}
SKIPPED = {
    "TOTAL": "Body Image Scale total (composite)",
    "AAQTOTAL": "AAQ total (composite)",
    "Negative_affect": "BSIQ-SF subscale score (composite)",
    "Attractiveness_evaluation": "BSIQ-SF subscale score (composite)",
    "Physical_functionality": "BSIQ-SF subscale score (composite)",
    "Height_dissatisfaction": "BSIQ-SF subscale score (composite)",
    "Reverse_Neg_affect": "reverse-scored BSIQ-SF subscale score (composite)",
    "Reverse_height_dissatisfaction": "reverse-scored BSIQ-SF subscale score (composite)",
    "Total_BSIQ_SF": "BSIQ-SF total (composite)",
}


def convert() -> None:
    d = pd.read_excel(fetch(URL, "figshare_29163374_10itemsBI.xlsx"), sheet_name="10itemsBI")
    screen_pii(d)
    src = list(d.columns)

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
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
