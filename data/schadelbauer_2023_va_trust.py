#!/usr/bin/env python3
# Source: https://zenodo.org/records/7764249
# DOI: 10.5281/zenodo.7764249
# Data: DATA.csv (semicolon-separated, latin-1), with DATA_CODING.txt as the codebook
# License: CC BY 4.0 (verified on the Zenodo record page / API: license id cc-by-4.0)
# Reference: Schadelbauer, L., Schlogl, S., & Groth, A. (2023). DATA: Linking Personality
#   and Trust in Intelligent Virtual Assistants. Zenodo.
# Item text: not shipped, although it IS cheap here -- DATA_CODING.txt in the same deposit
#   gives the verbatim English stem for every item in all five blocks (e.g. TRUST_1-3
#   "Legal structures (e.g. GDPR ...) help me feel safe working with Virtual Assistants.",
#   PERS_1-1 "... is reserved.", ATI-1 "I like to occupy myself in greater detail with
#   technical systems."). Label levels checked: the .csv has no variable or value labels
#   (not an SPSS file); DATA_CODING.txt is the only label source and it is complete. It is
#   held on rights grounds, not availability: the stems are verbatim third-party
#   instruments -- McKnight et al.'s trust-in-technology scales, the BFI short form
#   (Rammstedt & John) for PERS_*, and the Affinity for Technology Interaction scale
#   (Franke et al. 2019) for ATI-* -- and none has a row in
#   itemtext/instrument_rights_register.csv. Silence does not ship; see the batch handoff
#   for the register rows these need.
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
             + [c for c in ("cluster_id", "block_id") if c in t.columns]
             + covs)
    return t[order].reset_index(drop=True)


def pvals(items, valid, rename: dict | None = None) -> dict:
    """permitted_values keyed by the shipped item code."""
    vs = sorted(float(v) for v in valid)
    return {(rename or {}).get(c, c): list(vs) for c in items}

URL = "https://zenodo.org/api/records/7764249/files/DATA.csv/content"

COVS = {
    "LANGUAGE": "cov_language", "SEX": "cov_sex", "AGE": "cov_age",
    "NATIONALITY": "cov_nationality", "GREW_UP": "cov_grew_up",
    "LIVE_IN": "cov_live_in", "HIGHEST_EDU": "cov_education",
    "OCCUPATION": "cov_occupation", "HOW_OFTEN": "cov_va_use_frequency",
    "DO_YOU_USE": "cov_uses_va",
}
# Every rating block in the codebook uses 0 for "no answer"; it is dropped, not kept as a
# scale point. TRUST/VA-* are 1-5, PERS/TRUST-TECH are 1-5, ATI is 1-6 (the codebook's
# "[1-5]" annotation is wrong for ATI -- 6 is observed throughout).
BLOCKS = {
    "schadelbauer_2023_va_trust": (("TRUST_",), range(1, 6)),
    "schadelbauer_2023_va_system_trust": (("VA-FUNC", "VA_FUNC", "VA-REL", "VA-HELP"),
                                          range(1, 6)),
    "schadelbauer_2023_bfi": (("PERS_",), range(1, 6)),
    "schadelbauer_2023_tech_trust": (("TRUST-TECH",), range(1, 6)),
    "schadelbauer_2023_ati": (("ATI-",), range(1, 7)),
}
SKIPPED = {
    "CODE": "participant code assigned by the survey tool; pure identifier, never an item "
            "or a covariate (the source's own numeric ID ships as `id`)",
    "START": "survey start timestamp",
    "END": "survey end timestamp",
    "OTHER_ASSISTANTS": "free-text 'other assistant' write-in",
    "OTHER_USE": "free-text 'other use' write-in",
    "ASK_OTHER": "free-text 'other request' write-in",
}
# Multi-select checkboxes: coded NA/1 with no explicit 0, so a blank cell cannot be told
# apart from an unanswered one. Not an ordered response scale -> not shipped.
CHECKBOX = ("ALEXA", "SIRI", "CORTANA", "GOOGLE_ASSISTANT", "BIXBY",
            "WORK_SCHOOL", "ENTERTAINMENT", "INFO", "CONTROL")


def convert() -> None:
    d = pd.read_csv(fetch(URL, "zenodo_7764249_DATA.csv"), sep=";", encoding="latin-1")
    screen_pii(d)
    src = list(d.columns)

    d = d.rename(columns={"ID": "id"})
    assert d["id"].nunique() == len(d), "ID is not one row per respondent"
    print(f"  respondents={d['id'].nunique()}")

    d = d.rename(columns=COVS)
    covs = sorted(COVS.values())

    used = set()
    tables = {}
    for name, (prefixes, valid) in BLOCKS.items():
        items = [c for c in src if c.startswith(prefixes)]
        assert len(items) >= 3, (name, items)
        used.update(items)
        tables[name] = (long(d, items, covs, valid=set(float(v) for v in valid)),
                        pvals(items, valid))

    for c in src:
        if c == "ID" or c in COVS or c in used:
            continue
        if c in CHECKBOX or c.startswith("ASK_") and c != "ASK_OTHER":
            print(f"  [skip] {c}: multi-select checkbox coded NA/1, no explicit 0 and no "
                  f"ordered scale")
            continue
        assert c in SKIPPED, f"unaccounted source column: {c}"
        print(f"  [skip] {c}: {SKIPPED[c]}")

    emit(tables)


if __name__ == "__main__":
    convert()
