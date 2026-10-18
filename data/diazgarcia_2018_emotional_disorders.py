#!/usr/bin/env python3

# Source: https://zenodo.org/records/1477084
# DOI: 10.5281/zenodo.1477084 (dataset; the record names no published paper)
#   Diaz-Garcia, A., Gonzalez-Robles, A., Mor, S., Mira, A., Quero, S.,
#   Garcia-Palacios, A., et al. (2018). Positive and Negative Affect Schedule
#   (PANAS): psychometric properties for the online version in a clinical sample
#   with emotional disorders [Dataset]. Zenodo.
# Data: "Database_PANAS.sav": 595 patients with emotional disorders, pooled over five
#       studies, with SIX instruments deposited at the item level. The PANAS was
#       administered twice (pre and post), everything else once.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: NOT shipped for any of the six tables. Both label levels checked, and the
#   absence is specific rather than assumed: NO item carries a variable label (the only
#   labelled column in the file is filter_$, an SPSS artefact reading "DIAG_CAT = 1
#   (FILTER)"), and value labels are present but ONLY on the eight covariates --
#   GENDER, CIVIL_STATUS, EDUCATION_LEVEL, DIAG_CAT, PRINCIPAL_DIAGNOSTIC, STUDY,
#   EXP_COND and filter_$. So the deposit documents neither stems nor item anchors, and
#   it holds no codebook. Separately, five of the six are named third-party instruments whose
#   wording would not ship anyway: the PANAS, BDI-II, BAI and NEO-FFI are rights-
#   blocked (the PANAS row in itemtext/instrument_rights_register.csv is an explicit
#   block under the 2026-10-15 silence ruling), and only the PHQ-9 carries an express
#   grant. So the absence of labels costs this batch nothing it could have shipped.
#
# Six tables, one per instrument, because each has its own response scale:
#   diazgarcia_2018_panas   20 items, 1-5, LONGITUDINAL -- wave pre/post, 2 x 20.
#   diazgarcia_2018_bdi2    21 items, 0-3 (Beck Depression Inventory-II).
#   diazgarcia_2018_oasis    5 items, 0-4 (Overall Anxiety Severity and Impairment).
#   diazgarcia_2018_bai     21 items, 0-3 (Beck Anxiety Inventory).
#   diazgarcia_2018_neoffi  24 items, 0-4 (NEO-FFI-B, neuroticism + extraversion).
#   diazgarcia_2018_phq9     9 items, 0-3.
#
# One data-entry error is dropped, found by checking values PER ITEM rather than on the
# merged block: BAI21pre holds a single 13 among 359 responses, every other BAI item is
# 0-3, and 13 is not on the BAI's scale. That one cell is dropped; nothing else is.
#
# Not shipped: the depositor's totals and subscale scores -- PANAS.R_PA_PRE,
#   PANAS.R_NA_PRE, PANAS.R_PA_POST, PANAS.R_NA_POST, BDI_TOTAL_PRE,
#   OASIS_TOTAL_PRE, BAI_TOTAL_PRE, Neuroticismo_total_pre, Extraversion_total_pre,
#   PHQ9Sumatorio_pre -- and filter_$, an SPSS filter artefact.
# Covariates: cov_gender, cov_age, cov_civil_status, cov_education_level,
#   cov_diagnosis_category, cov_principal_diagnosis, cov_comorbid_diagnosis,
#   cov_n_comorbid_diagnoses, cov_study (the deposit's five pooled samples),
#   cov_exp_condition.
# id: the row index. The deposit's "USER" is a platform-style participant code
#   ("Usuario12120") and is not unique -- the value "x_LE" appears twice -- so it is
#   replaced by the row index rather than hashed or trusted.
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
              f"items={t['item'].nunique()} resp={t['resp'].min():g}-{t['resp'].max():g}"
              + (f" waves={t['wave'].nunique()}" if "wave" in t else ""))


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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_1477084"
PANAS_PRE = [f"PANAS.R{i}pre" for i in range(1, 21)]
PANAS_POST = [f"PANAS.R{i}post" for i in range(1, 21)]
BDI = [f"BDI{i}pre" for i in range(1, 22)]
OASIS = [f"OASIS{i}pre" for i in range(1, 6)]
BAI = [f"BAI{i}pre" for i in range(1, 22)]
NEO = [f"NEOFFIB{i}pre" for i in range(1, 25)]
PHQ9 = [f"PHQ9{i}_pre" for i in range(1, 10)]
TOTALS = ["PANAS.R_PA_PRE", "PANAS.R_NA_PRE", "PANAS.R_PA_POST", "PANAS.R_NA_POST",
          "BDI_TOTAL_PRE", "OASIS_TOTAL_PRE", "BAI_TOTAL_PRE",
          "Neuroticismo_total_pre", "Extraversion_total_pre", "PHQ9Sumatorio_pre"]
COVS = {"GENDER": "cov_gender", "AGE": "cov_age",
        "CIVIL_STATUS": "cov_civil_status",
        "EDUCATION_LEVEL": "cov_education_level",
        "DIAG_CAT": "cov_diagnosis_category",
        "PRINCIPAL_DIAGNOSTIC": "cov_principal_diagnosis",
        "COMORBID_DIAGNOSTIC": "cov_comorbid_diagnosis",
        "NUMBER_COMORBID_DIAGNOSES": "cov_n_comorbid_diagnoses",
        "STUDY": "cov_study", "EXP_COND": "cov_exp_condition"}
# Item codes shipped for the PANAS drop the wave suffix, which becomes the `wave`
# column; the two waves must share one item code or they cannot be compared.
PANAS_CODE = {c: f"PANAS{i}" for i, c in enumerate(PANAS_PRE, 1)}
PANAS_CODE.update({c: f"PANAS{i}" for i, c in enumerate(PANAS_POST, 1)})


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(zenodo_fetch(1477084, "Database_PANAS.sav", RAW_DIR),
                                  apply_value_formats=False)
    assert len(d) == 595, len(d)
    # The item-text verdict in the header is an asserted absence, not an assumption:
    # no ITEM carries a stem at either label level. Only filter_$ has a variable
    # label, and value labels sit on the covariates alone.
    items_all = PANAS_PRE + PANAS_POST + BDI + OASIS + BAI + NEO + PHQ9
    labelled = [c for c, v in (meta.column_names_to_labels or {}).items() if v]
    assert labelled == ["filter_$"], labelled
    with_vl = set(meta.variable_value_labels or {})
    assert not (with_vl & set(items_all)), sorted(with_vl & set(items_all))
    books(list(d.columns), {
        "shipped": PANAS_PRE + PANAS_POST + BDI + OASIS + BAI + NEO + PHQ9,
        "covariate": list(COVS),
        "participant code, not unique -- id is the row index": ["USER"],
        "total or subscale score computed by the depositor": TOTALS,
        "SPSS filter artefact": ["filter_$"],
    })
    d = d.rename(columns=COVS)
    d["id"] = range(1, len(d) + 1)
    covs = list(COVS.values())

    # One isolated data-entry error: BAI21pre holds a single 13 on a 0-3 scale.
    bad = d["BAI21pre"] > 3
    assert bad.sum() == 1, bad.sum()
    print(f"    [dropped] 1 cell: BAI21pre = {d.loc[bad, 'BAI21pre'].iloc[0]:g}, "
          f"off a 0-3 scale (every other BAI item is 0-3)")
    d.loc[bad, "BAI21pre"] = pd.NA

    # The PANAS is the one instrument with two administrations, so it ships long in
    # wave as well as item.
    pre = long(d, PANAS_PRE, covs, valid=range(1, 6), rename=PANAS_CODE)
    post = long(d, PANAS_POST, covs, valid=range(1, 6), rename=PANAS_CODE)
    pre["wave"], post["wave"] = "pre", "post"
    panas = pd.concat([pre, post], ignore_index=True)
    panas = panas[["id", "item", "resp", "wave"] + covs]
    panas = panas.sort_values(["id", "wave", "item"]).reset_index(drop=True)

    emit({
        "diazgarcia_2018_panas": (panas, pv_for(PANAS_CODE.values(), range(1, 6))),
        "diazgarcia_2018_bdi2": (long(d, BDI, covs, valid=range(0, 4)), pv_for(BDI, range(0, 4))),
        "diazgarcia_2018_oasis": (long(d, OASIS, covs, valid=range(0, 5)), pv_for(OASIS, range(0, 5))),
        "diazgarcia_2018_bai": (long(d, BAI, covs, valid=range(0, 4)), pv_for(BAI, range(0, 4))),
        "diazgarcia_2018_neoffi": (long(d, NEO, covs, valid=range(0, 5)), pv_for(NEO, range(0, 5))),
        "diazgarcia_2018_phq9": (long(d, PHQ9, covs, valid=range(0, 4)), pv_for(PHQ9, range(0, 4))),
    })


if __name__ == "__main__":
    main()
