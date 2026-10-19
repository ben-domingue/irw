#!/usr/bin/env python3

# Source: https://zenodo.org/records/1295642
# DOI: 10.5281/zenodo.1295642
#   Gonzalez-Robles, A., Mira, A., Miguel, C., et al. (2018). A brief online
#   transdiagnostic measure: psychometric properties of the Overall Anxiety Severity
#   and Impairment Scale (OASIS) among Spanish patients with emotional disorders
#   [Dataset]. Zenodo.
# Data: "Database OASIS.sav" -- 583 records pooled from nine Spanish clinical
#       studies of patients with emotional disorders.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped. Both label levels checked: 3 of 105 variables carry a
#   variable label (all three are derived/subsample columns, not items), and 7 carry
#   value labels (Study, diagnosis and demographics). No item stems or anchors are
#   in the file. OASIS and ODSIS are published instruments with freely available
#   wording, one hop away in the paper.
#
# THREE tables ship; THREE instruments are WITHHELD on rights:
#   gonzalezrobles_2018_oasis   5 items, 0-4, WITH A WAVE. The deposit gives
#                               OASIS1-5pre for all 583 records and OASIS1-5post for
#                               92 of them, so the two administrations ship as
#                               wave=pre / wave=post on the same item codes rather
#                               than as ten separate items.
#   gonzalezrobles_2018_odsis   5 items, 0-4 (pre only; the deposit has no post).
#   gonzalezrobles_2018_qli    10 items, 0-10 (pre only).
# WITHHELD, all three `block` in itemtext/instrument_rights_register.csv:
#   BAI1-21pre      Beck Anxiety Inventory. Register verdict block; Ben ruled
#                   2026-09-29 (irw#2401) that a block row covers every language,
#                   so this Spanish administration is covered.
#   BDI1-21pre      Beck Depression Inventory-II. Register verdict block.
#   PANASR1-20pre   PANAS. Register verdict block, and its matcher
#                   `^pan[_ ]?[0-9]|panas` matches these codes.
# Not shipped besides those: the six derived totals (OASISpreTOTAL, OASISSumapost,
#   BAITotalpre, ODSISpreTOTAL, BDITOTALpre, QLImediapre) and the two PANAS subscale
#   scores.
#
# id: NEITHER `User` NOR (`Study`, `User`) identifies a record -- User has 428
#   distinct values over 583 rows, and (Study, User) still leaves 153 duplicated
#   pairs. The deposit documents no key, so the 0-based ROW INDEX is used: each row
#   is one patient's battery, and pre/post stay linked within the row. This is the
#   conservative reading -- it can split one person who appears in two studies into
#   two ids, but it never merges two different people (feedback_id_collision_prefix).
#   The original `User` and `Study` ride along as covariates so the ambiguity stays
#   visible rather than being erased.
# Covariates: cov_study, cov_user_code, cov_principal_diagnostic,
#   cov_n_comorbid_diagnoses, cov_gender, cov_age, cov_civil_status, cov_education.
import os
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
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "1295642"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 1295642, "Database OASIS.sav"

COVS = {"Study": "cov_study", "User": "cov_user_code",
        "Principal_diagnostic": "cov_principal_diagnostic",
        "Number_comorbid_diagnoses": "cov_n_comorbid_diagnoses",
        "Gender": "cov_gender", "Age": "cov_age",
        "Civil_status": "cov_civil_status", "Education": "cov_education"}
WITHHELD = ([f"BAI{i}pre" for i in range(1, 22)]
            + [f"BDI{i}pre" for i in range(1, 22)]
            + [f"PANASR{i}pre" for i in range(1, 21)])
DERIVED = ["OASISpreTOTAL", "OASISSumapost", "BAITotalpre", "ODSISpreTOTAL",
           "BDITOTALpre", "QLImediapre", "PANAS_Positive_pre",
           "PANAS_Negative_pre", "Subsample1", "Subsample2"]


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                         headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def emit(t, name, scale=None):
    keys = ["id", "item"] + (["wave"] if "wave" in t else [])
    assert not t.duplicated(keys).any(), name
    assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
    pv = set(scale) if scale else None
    checks = run_qc(t, **({"permitted_values": pv} if pv else {}))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {name} {c.name}: {c.detail[:170]}")
    report = irw_validate.validate_frame(
        t, label=name, profile="upload",
        context={"permitted_values": pv} if pv else None)
    assert report.conforms and not report.errors, \
        (name, [(f.check, f.message) for f in report.errors])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    w = f" waves={sorted(t['wave'].unique())}" if "wave" in t else ""
    print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}{w}")


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    df.insert(0, "id", range(len(df)))
    assert df["User"].nunique() < len(df), (
        "User is unique after all -- re-read the id note in this header")

    oasis = [f"OASIS{i}" for i in range(1, 6)]
    odsis = [f"ODSIS{i}pre" for i in range(1, 6)]
    qli = [f"QLI{i}pre" for i in range(1, 11)]
    used = ({f"{c}pre" for c in oasis} | {f"{c}post" for c in oasis}
            | set(odsis) | set(qli) | set(WITHHELD) | set(DERIVED)
            | set(COVS) | {"id"})
    unaccounted = [c for c in df.columns if c not in used]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"  withheld {len(WITHHELD)} columns on rights (BAI 21, BDI 21, PANAS 20)")
    for c in DERIVED:
        print(f"  skipped {c}: derived total/subscale or subsample flag")

    covcols = list(COVS)
    base = df[["id", *covcols]].rename(columns=COVS)
    for c in COVS.values():
        base[c] = pd.to_numeric(base[c], errors="coerce").astype("Int64")

    # OASIS: pre and post are two administrations of the same five items.
    waves = []
    for tag in ("pre", "post"):
        cols = [f"{c}{tag}" for c in oasis]
        w = (df[["id", *cols]]
             .melt(id_vars="id", value_vars=cols, var_name="item",
                   value_name="resp")
             .dropna(subset=["resp"]))
        w["item"] = w["item"].str.replace(f"{tag}$", "", regex=True)
        w["wave"] = tag
        waves.append(w)
    t = pd.concat(waves, ignore_index=True).merge(base, on="id")
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp", "wave", *COVS.values()]]
    emit(t, "gonzalezrobles_2018_oasis", range(0, 5))

    for name, cols, scale in (
            ("gonzalezrobles_2018_odsis", odsis, range(0, 5)),
            ("gonzalezrobles_2018_qli", qli, range(0, 11))):
        t = (df[["id", *cols]]
             .melt(id_vars="id", value_vars=cols, var_name="item",
                   value_name="resp")
             .dropna(subset=["resp"])
             .merge(base, on="id"))
        t["item"] = t["item"].str.replace("pre$", "", regex=True)
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp", *COVS.values()]]
        emit(t, name, scale)


if __name__ == "__main__":
    main()
