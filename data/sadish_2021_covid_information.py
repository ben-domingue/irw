#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/WKDC9I
# DOI: 10.7910/DVN/WKDC9I
# Data: is_4_4_6_publicData.dta (Harvard Dataverse, format=original)
# License: CC0 1.0 (verified on the Dataverse record: license name "CC0 1.0",
#   rightsIdentifier CC0-1.0)
# Reference: Sadish, D., Adhvaryu, A., & Nyshadham, A. (2021). (Mis)information and
#   Anxiety: Evidence from a Randomized Covid-19 Information Campaign. Journal of
#   Development Economics. Harvard Dataverse.
# Item text: not shipped. Both label levels were checked. Stata variable labels exist but
#   are mostly plumbing ("_bl symptoms_1", "_el vector"); the ONE place real stems appear is
#   the derived `*_des_*` family ("Non-symptomatic can spread Covid-19.", "Eating turmeric
#   protects from Covid-19 infection."), and those are recoded binaries, not the raw items
#   shipped here, so using their wording would mean asserting a mapping the file does not
#   state. Value labels are populated for the raw belief items (Yes / No / Don't know) and
#   are what identified the "Don't know" code dropped below, but they carry no stem. The
#   symptom-recall items (symptoms_1..9) have no label of any kind -- their wording is in
#   the study's survey instrument, which is not in the deposit (the deposit's
#   info_study_baseline_*.html is the baseline tracking sheet, not the questionnaire).
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

FID = 4771542  # is_4_4_6_publicData.tab -> format=original gives the .dta
URL = f"https://dataverse.harvard.edu/api/access/datafile/{FID}?format=original"

COVS = {
    "female": "cov_female", "edu_hi": "cov_education_above_grade10", "age": "cov_age",
    "religion": "cov_religion", "location": "cov_location", "smartphone": "cov_smartphone",
    "hostel": "cov_lives_in_hostel", "treatment": "cov_treatment_arm",
    "round": "cov_survey_round", "strata": "cov_strata", "quit": "cov_left_job",
    "cheat": "cov_suspected_cheating", "att": "cov_attrited", "retained": "cov_retained",
}
# Raw per-item responses, measured at baseline (_bl, wave 1) and endline (_el, wave 2).
SYMPTOMS = [f"symptoms_{i}" for i in range(1, 10)]          # 0/1 recall of a symptom
BELIEFS = ["vector", "remedy", "antibiotics", "urine", "turmeric", "heart",
           "religion_spread"]                                # 0/1, plus 2 = "Don't know"
# Numeracy quiz, asked once.
NUMERACY = ["canAdd", "canSub", "canMul"]


def convert() -> None:
    d = pd.read_stata(fetch(URL, "dvn_wkdc9i_publicData.dta"), convert_categoricals=False)
    screen_pii(d)
    src = list(d.columns)

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    print(f"  respondents={d['id'].nunique()}")
    d = d.rename(columns={"factory": "cluster_id"})
    d = d.rename(columns=COVS)
    covs = sorted(COVS.values())

    used = set()
    tables = {}
    for name, stems, valid in (
            ("sadish_2021_covid_symptoms", SYMPTOMS, {0.0, 1.0}),
            ("sadish_2021_covid_beliefs", BELIEFS, {0.0, 1.0})):
        parts = []
        for wave, suf in ((1, "_bl"), (2, "_el")):
            cols = [f"{s}{suf}" for s in stems]
            assert all(c in d.columns for c in cols), (name, suf)
            used.update(cols)
            t = long(d, cols, covs, valid=valid, extra=("cluster_id",),
                     rename={f"{s}{suf}": s for s in stems})
            t.insert(3, "wave", wave)
            parts.append(t)
        t = pd.concat(parts, ignore_index=True)
        tables[name] = (t, pvals(stems, sorted(valid)))

    used.update(NUMERACY)
    tables["sadish_2021_numeracy"] = (
        long(d, NUMERACY, covs, valid={0.0, 1.0}, extra=("cluster_id",)),
        pvals(NUMERACY, [0, 1]))

    # Balance the books.
    reasons = [
        (lambda c: c.startswith("surveyor_") or c.startswith("submitDate_"),
         "survey administration field (enumerator id / submission date)"),
        (lambda c: c.startswith("numSymptoms"), "count of symptoms recalled (composite)"),
        (lambda c: c.startswith("knowledge"), "standardised knowledge index (composite)"),
        (lambda c: "_tri_" in c, "recoded -1/0/1 copy of the raw belief item"),
        (lambda c: "_bi_" in c, "recoded 0/1 copy of the raw belief item"),
        (lambda c: "_des_" in c, "recoded 0/1 'descriptive' copy of the raw belief item"),
        (lambda c: c.startswith(("distress", "depression", "anxiety")),
         "PHQ-4 / PHQ-2 / GAD-2 scale score; the item-level responses are not in the file"),
        (lambda c: c in ("numeracy", "memory", "numeracy_hi", "memory_hi", "age_hi"),
         "score or high/low split (composite)"),
        (lambda c: c in ("who_answered", "disconnected", "info_related", "info_work",
                         "info_unrelated", "phoneCall", "callDate", "callTime", "attempts",
                         "voiceRecording", "callerCalled", "intDuration"),
         "intervention-delivery field recorded by the caller, not a respondent response"),
        (lambda c: c in ("VR", "PC", "TM", "audio", "attemptsUnknown", "smsDelivered", "contact", "infoContent",
                         "infoAll", "infoRepeat"),
         "intervention-delivery field recorded by the caller, not a respondent response"),
        (lambda c: c == "ipw", "inverse probability weight (analysis field)"),
        (lambda c: c == "empcode", "sequential employee code used to link the two waves; "
                                   "pure identifier, superseded by `id`"),
    ]
    for c in src:
        if c in ("factory",) or c in COVS or c in used:
            continue
        for test, why in reasons:
            if test(c):
                print(f"  [skip] {c}: {why}")
                break
        else:
            raise AssertionError(f"unaccounted source column: {c}")

    emit(tables)


if __name__ == "__main__":
    convert()
