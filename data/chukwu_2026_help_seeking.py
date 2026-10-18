#!/usr/bin/env python3

# Source: https://zenodo.org/records/22070938
# DOI: 10.5281/zenodo.22070938 (dataset; the record names no published paper)
#   Chukwu, D. U., Omeh, C. B., & Mashile, O. E. (2026). Help-Seeking Orientation and
#   Academic Self-Efficacy among University Lecturers: The Mediating Roles of AI
#   Literacy and AI Competency [Dataset]. Zenodo.
# Data: "Chris & Uche - HelpSeeking.sav": 974 university lecturers, five instruments
#       at the item level, every item on a 1-5 agreement scale.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: NOT shipped. Both label levels checked: the SPSS VALUE labels are present
#   on every item and give the 1-5 anchors, but the VARIABLE labels are empty for all
#   42 columns, so the deposit carries no item stems at all. Shipping anchors without
#   stems is the option-only shape ruled out in irw#1770. The stems are in the paper,
#   which this record does not name -- a later pass needs the published article for
#   the HSA/AiL/AiC/ASEB/TAS wording.
#
# Five tables, one per instrument (the deposit's own code prefixes):
#   chukwu_2026_help_seeking_attitude  8 items, HSA.
#   chukwu_2026_ai_literacy            6 items, AiL.
#   chukwu_2026_ai_competency          4 items, AiC.
#   chukwu_2026_academic_self_efficacy 8 items, ASEB.
#   chukwu_2026_trust_in_ai            8 items, TAS.
# Not shipped: H_Seek, Aca_Self, Trust_AI, Ai_Comp, Ai_Lit -- subscale means computed
#   by the depositor (all fractional, e.g. 1.875).
# Covariates: cov_faculty, cov_years_of_experience, cov_trained_in_ai.
# id: the deposit carries no respondent identifier, so id is the row index (1-974).
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
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def zenodo_fetch(record: int, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://zenodo.org/api/records/{record}", headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == fname][0]
        download(url, p)
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


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=(),
         rename: dict | None = None) -> pd.DataFrame:
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    if rename:
        t["item"] = t["item"].map(lambda c: rename.get(c, c))
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", *extra, "item"]).reset_index(drop=True)


def pv_for(items, valid) -> dict:
    return {i: set(valid) for i in items}


def books(all_cols, used: dict) -> None:
    """Every source column is either shipped or skipped for a printed reason."""
    seen = {}
    for reason, cols in used.items():
        for c in cols:
            assert c not in seen, (c, reason, seen[c])
            seen[c] = reason
    missing = [c for c in all_cols if c not in seen]
    assert not missing, f"unaccounted source columns: {missing}"
    extra = [c for c in seen if c not in all_cols]
    assert not extra, f"named columns not in the source: {extra}"
    for reason, cols in used.items():
        if reason != "shipped" and cols:
            print(f"    [skipped: {reason}] {len(cols)}: {', '.join(map(str, cols))[:300]}")


RAW_DIR = RAW_ROOT / "10_5281_zenodo_22070938"
HSA = [f"HSA{i}" for i in range(1, 9)]
AIL = [f"AiL{i}" for i in range(1, 7)]
AIC = [f"AiC{i}" for i in range(1, 5)]
ASEB = [f"ASEB{i}" for i in range(1, 9)]
TAS = [f"TAS{i}" for i in range(1, 9)]
COVS = {"FACULTY": "cov_faculty", "YOE": "cov_years_of_experience",
        "T_AI": "cov_trained_in_ai"}
MEANS = ["H_Seek", "Aca_Self", "Trust_AI", "Ai_Comp", "Ai_Lit"]


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(
        zenodo_fetch(22070938, "Chris & Uche - HelpSeeking.sav", RAW_DIR),
        apply_value_formats=False)
    assert len(d) == 974, len(d)
    src = list(d.columns)
    assert not any((meta.column_names_to_labels or {}).get(c) for c in src), \
        "variable labels appeared; the item-text verdict in the header needs redoing"
    books(src, {
        "shipped": HSA + AIL + AIC + ASEB + TAS,
        "covariate": list(COVS),
        "subscale mean computed by the depositor": MEANS,
    })
    d = d.rename(columns=COVS)
    d["id"] = range(1, len(d) + 1)
    covs = list(COVS.values())
    v = range(1, 6)
    emit({
        "chukwu_2026_help_seeking_attitude": (long(d, HSA, covs, valid=v), pv_for(HSA, v)),
        "chukwu_2026_ai_literacy": (long(d, AIL, covs, valid=v), pv_for(AIL, v)),
        "chukwu_2026_ai_competency": (long(d, AIC, covs, valid=v), pv_for(AIC, v)),
        "chukwu_2026_academic_self_efficacy": (long(d, ASEB, covs, valid=v), pv_for(ASEB, v)),
        "chukwu_2026_trust_in_ai": (long(d, TAS, covs, valid=v), pv_for(TAS, v)),
    })


if __name__ == "__main__":
    main()
