#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/FNYYQR
# DOI: 10.1007/s11136-018-1785-8
#   Fischer, F., Gibbons, C., Coste, J., Valderas, J. M., Rose, M., & Leplege, A. (2018).
#   Measurement invariance and general population reference values of the PROMIS
#   Profile 29 in the UK, France, and Germany. Quality of Life Research, 27(4), 999-1014.
# Data: Harvard Dataverse 10.7910/DVN/FNYYQR (Fischer, Felix; 2021-02-02),
#       "Representative PROMIS Profile 29 and EQ-5D Data from France, UK, and Germany".
#       p29_data.sav (file 4286318, format=original): 4,512 Ipsos internet-panel
#       respondents (UK 1,509, France 1,501, Germany 1,502) x 75 columns; no missing
#       data (forced response). p29_data_dictionary-1.xlsx (file 4361654) gives every
#       variable's question text, PROMIS item ID and response options.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped -- rights. The wording is right there (the data dictionary
#   xlsx carries every stem and option; the .sav carries value labels for every item,
#   variable labels are empty), but PROMIS is a `block` row in
#   itemtext/instrument_rights_register.csv (HealthMeasures terms, ruled 2026-09-05)
#   and EQ-5D is blocked likewise (EuroQol, ratified 2026-09-30).
#
# Tables (PROMIS-29 v2 domains, 1-5 as stored; item = the deposit's column name,
#   whose PROMIS item ID is in the dictionary: P1_1 PFA11, P1_2 PFA21, P1_3 PFA23,
#   P1_4 PFA53, P2_1 EDANX01 ... P8_4 PAININ34).
#   CODING: the stored codes are PROMIS item scores, NOT the questionnaire option
#   order that the .sav value labels and the dictionary list. Checked from the data:
#   physical function sits 77-83% at 5 in a general-population sample and correlates
#   -0.58 with pain interference and -0.71 with EQ-5D mobility, so 5 = "without any
#   difficulty" (labels say 1); P5 (sleep quality) and P6_1 (sleep refreshing)
#   correlate +0.69 and +0.55 with P6_2 ("I had a problem with my sleep"), so both are
#   stored reversed, higher = worse sleep, as PROMIS scores them. Every other domain's
#   labels agree with the data (e.g. anxiety 1 never sits at 43%).
#   fischer_2018_promis29_physfunc     P1_1-P1_4  1 unable to do .. 5 without any difficulty
#   fischer_2018_promis29_anxiety      P2_1-P2_4  1 never .. 5 always
#   fischer_2018_promis29_depression   P3_1-P3_4  1 never .. 5 always
#   fischer_2018_promis29_fatigue      P4_1-P4_4  1 not at all .. 5 very much
#   fischer_2018_promis29_sleep        P5, P6_1-P6_3  higher = more sleep disturbance
#                                      (P5, P6_1 reverse-scored in the deposit)
#   fischer_2018_promis29_social       P7_1-P7_4  1 never .. 5 always ("I have trouble ...")
#   fischer_2018_promis29_pain         P8_1-P8_4  pain interference, 1 not at all .. 5 very much
#   fischer_2018_eq5d5l                E1-E5      EQ-5D-5L descriptive system, 1 no problems ..
#                                      5 unable/extreme (E1 1 = 71%)
# Skipped: P9 (PROMIS pain intensity, a single 0-10 item), E6 (EQ VAS, a single 0-100
#   rating), Q12_1-Q12_18 (doctor-diagnosed condition checklist, not an instrument),
#   the country-specific region/market/education/income codes (FRREG5, GEREG16,
#   UKREG12, FRMKT5, GEMKT3, UKMKT3, FREDU, GEEDU, UKEDU, FRGEINC, UKINC; their
#   harmonised versions EDU3 and INC4 ship), AGER (age band; AGE ships).
# Covariates (codes as the .sav labels them): cov_country (France / Germany / UK),
#   cov_gender (1 male, 2 female), cov_age (years), cov_education (EDU3, 1-3),
#   cov_income (INC4, 1 lower .. 4 higher, 5 prefer not to say), cov_occupation (OCC),
#   cov_household (HHCMP5), cov_marital (MARITAL), cov_weight (the survey weight).
# id: the deposit's ID is the Ipsos panel identifier, a platform participant ID, so it
#   is replaced by the row index (2026-09-20 ruling) and never shipped.

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
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_fnyyqr"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/4286318?format=original"

P = "fischer_2018_"
TABLES = {
    "promis29_physfunc": [f"P1_{i}" for i in range(1, 5)],
    "promis29_anxiety": [f"P2_{i}" for i in range(1, 5)],
    "promis29_depression": [f"P3_{i}" for i in range(1, 5)],
    "promis29_fatigue": [f"P4_{i}" for i in range(1, 5)],
    "promis29_sleep": ["P5", "P6_1", "P6_2", "P6_3"],
    "promis29_social": [f"P7_{i}" for i in range(1, 5)],
    "promis29_pain": [f"P8_{i}" for i in range(1, 5)],
    "eq5d5l": [f"E{i}" for i in range(1, 6)],
}
COVS = {"GENDER": "cov_gender", "AGE": "cov_age", "EDU3": "cov_education",
        "INC4": "cov_income", "OCC": "cov_occupation", "HHCMP5": "cov_household",
        "MARITAL": "cov_marital", "WEIGHT": "cov_weight"}
COUNTRY = {1: "France", 2: "Germany", 3: "UK"}
SKIP = {"ID": "Ipsos panel ID (replaced by row index)",
        "P9": "single-item pain intensity", "E6": "single-item EQ VAS",
        "AGER": "age band (AGE ships)",
        **{f"Q12_{i}": "diagnosis checklist" for i in range(1, 19)},
        **{c: "country-specific code (harmonised version ships)" for c in
           ["FRREG5", "GEREG16", "UKREG12", "FRMKT5", "GEMKT3", "UKMKT3", "FREDU",
            "GEEDU", "UKEDU", "FRGEINC", "UKINC"]}}


def fetch() -> Path:
    p = RAW_DIR / "p29_data.sav"
    if not p.exists():
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
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


def main() -> None:
    d, _ = pyreadstat.read_sav(str(fetch()))
    assert d.shape == (4512, 75) and d["ID"].is_unique
    items = [c for its in TABLES.values() for c in its]
    accounted = set(items) | set(COVS) | {"COUNTRY"} | set(SKIP)
    assert accounted == set(d.columns), set(d.columns) ^ accounted
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d["cov_country"] = d["COUNTRY"].map(COUNTRY)
    d = d.rename(columns=COVS)
    covs = ["cov_country"] + list(COVS.values())
    for c in covs:
        if c not in ("cov_country", "cov_weight"):
            d[c] = d[c].astype("Int64")
    assert d[items].isin(range(1, 6)).all().all()
    # stored codes are PROMIS scores (see header): physical function 5 = no difficulty,
    # P5/P6_1 reversed so higher = worse sleep
    pf = d[TABLES["promis29_physfunc"]].mean(axis=1)
    assert pf.corr(d["P8_1"]) < -0.4 and (d["P1_4"] == 5).mean() > 0.7
    assert d["P5"].corr(d["P6_2"]) > 0.5 and d["P6_1"].corr(d["P6_2"]) > 0.4
    out = {}
    for suf, its in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and len(t) == 4512 * len(its)
        out[P + suf] = (t, {i: set(range(1, 6)) for i in its})
    emit(out)


if __name__ == "__main__":
    main()
