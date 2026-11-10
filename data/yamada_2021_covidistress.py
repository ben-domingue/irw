#!/usr/bin/env python3
# Source: https://osf.io/z39us/ (COVIDiSTRESS global survey)
# DOI: 10.1038/s41598-024-52304-z (the Scientific Reports article whose Data
#   Availability statement led here) and the dataset's own descriptor:
#   Yamada, Cepulic, Coll-Martin, Debove, Gautreau, Han, Rasmussen, Tran et al.
#   (2021). "COVIDiSTRESS Global Survey dataset on psychological and behavioural
#   consequences of the COVID-19 outbreak." Scientific Data 8:3,
#   doi:10.1038/s41597-020-00784-9.
# Data: OSF z39us, "COVIDiSTRESS cleaned data and cleaning code (data from 27
#   April)/COVIDiSTRESS_May_30_cleaned_final.csv" (osf.io/cjxua, version 2 of
#   2020-12-02): 125,306 respondents x 154 columns, the exact N of the Scientific
#   Data descriptor. Version 2 is used deliberately: the OSF note "Note about the
#   cleaned dataset file and cleaning code files (December 2nd, 2020)" says every
#   earlier cleaned file, including "COVIDiSTRESS June 17.csv", has
#   Scale_PSS10_UCLA_6 and _7 swapped for Bengali-language rows.
#   Codebook: the cleaning notebook May30.Rmd and "COVIDiSTRESS Global Survey Data
#   cleaning information.pdf" (osf.io/e2y7w) document the numeric recodes.
# License: CC0 1.0 (OSF project z39us licence).
#
# Sample: adults (>= 18, consent given) in 47 languages, 30 March - 30 May 2020.
#   id = the deposit's ID column (unique per row).
#
# Tables (items keep the source column names, except that the PSS-10 and SLON-3
#   drop the "Scale_" prefix and "_UCLA" infix: Scale_PSS10_UCLA_k -> PSS10_k,
#   Scale_SLON_k -> SLON_k, because irw_lint_covariates reads a "Scale_" item as
#   a scale-group covariate; responses as stored, no reversal):
#   _pss10       Scale_PSS10_UCLA_1..10  1-5  Perceived Stress Scale (1 Never ..
#                5 Very often). PSS10_avg reproduces from these items with 4, 5,
#                7, 8 reversed (checked), so the items are unreversed.
#   _slon3       Scale_SLON_1..3         1-5  SLON-3 short loneliness scale (same
#                Never..Very often recode; first stored as PSS10_UCLA_11..13)
#   _trust_inst  OECD_insititutions_1..6 0-10 OECD trust in institutions
#   _concerns    Corona_concerns_1..5    1-6  (1 Strongly disagree .. 6 Strongly agree)
#   _compliance  Compliance_1..6         1-6
#   _bffneu/_bffext/_bffope/_bffagr/_bffcon  BFF_15_1..15, 1-6: the BFI-S (15
#                items, Lang et al. 2011), split per trait as the cleaning
#                notebook scores it: neu 1-3, ext 4-6, ope 7-9, agr 10-12,
#                con 13-15 (keyed items 3, 6, 10, 14 reversed in its scoring).
#   _distress    Expl_Distress_1..24     1-6; 99 "Does not apply to my current
#                situation" is a non-response and is dropped
#   _sps10       SPS_1..10               1-6  Social Provisions Scale (SPS-10)
#   _coping      Expl_Coping_1..16       1-6
#   _media       Expl_media_1..6         1-6
#
# Not shipped: OECD_people_1/2 (two items, below the 3-item floor), the single
#   Trust_countrymeasure item, the Asian-disease vignette (AD_*), the composite
#   scores, and the Bosnia war-trauma sub-study (Scale_UCLA_TRI_*, PS_PTSD_*:
#   about 50 respondents, below the floor). Free-text columns
#   (Expl_Distress_txt, Expl_coping_txt, Final_open, *_TXT) and Dem_state (a
#   free-text state/region) are dropped in no form; RecordedDate and the
#   duration are not carried.
#
# Covariates: age, gender, education, mother's education, employment, country,
#   expat, marital status, number of dependents, risk group, isolation status,
#   survey language.
#
# Item text: not shipped. Levels checked: the cleaned CSV has bare column names
#   only. The English master wording is in row 2 of the raw Qualtrics exports
#   ("choice text" files in the same OSF folder), but the survey was administered
#   in 47 languages (row 2 of the numeric export osf.io/ck8w9 also carries it), and the PSS-10 / BFI-S / SPS-10 wording belongs to third
#   parties (PSS-10 is a register `block`).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "yamada_2021_covidistress"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://osf.io/download/cjxua/?version=2"
FILE = "COVIDiSTRESS_May_30_cleaned_final.csv"
P = "yamada_2021_covidistress_"

L6 = set(range(1, 7))
TABLES = {
    "pss10": ([f"Scale_PSS10_UCLA_{i}" for i in range(1, 11)], set(range(1, 6))),
    "slon3": ([f"Scale_SLON_{i}" for i in range(1, 4)], set(range(1, 6))),
    "trust_inst": ([f"OECD_insititutions_{i}" for i in range(1, 7)], set(range(0, 11))),
    "concerns": ([f"Corona_concerns_{i}" for i in range(1, 6)], L6),
    "compliance": ([f"Compliance_{i}" for i in range(1, 7)], L6),
    "bffneu": ([f"BFF_15_{i}" for i in (1, 2, 3)], L6),
    "bffext": ([f"BFF_15_{i}" for i in (4, 5, 6)], L6),
    "bffope": ([f"BFF_15_{i}" for i in (7, 8, 9)], L6),
    "bffagr": ([f"BFF_15_{i}" for i in (10, 11, 12)], L6),
    "bffcon": ([f"BFF_15_{i}" for i in (13, 14, 15)], L6),
    "distress": ([f"Expl_Distress_{i}" for i in range(1, 25)], L6),
    "sps10": ([f"SPS_{i}" for i in range(1, 11)], L6),
    "coping": ([f"Expl_Coping_{i}" for i in range(1, 17)], L6),
    "media": ([f"Expl_media_{i}" for i in range(1, 7)], L6),
}
COVS = {
    "Dem_age": "cov_age", "Dem_gender": "cov_gender", "Dem_edu": "cov_education",
    "Dem_edu_mom": "cov_education_mother", "Dem_employment": "cov_employment",
    "Country": "cov_country", "Dem_Expat": "cov_expat",
    "Dem_maritalstatus": "cov_marital", "Dem_dependents": "cov_dependents",
    "Dem_riskgroup": "cov_riskgroup", "Dem_isolation": "cov_isolation",
    "UserLanguage": "cov_language",
}
SKIPPED = (["answered_all", "Duration..in.seconds.", "RecordedDate", "Dem_state",
            "Dem_isolation_adults", "Dem_isolation_kids", "AD_gain", "AD_loss",
            "AD_check", "OECD_people_1", "OECD_people_2", "Trust_countrymeasure",
            "born_92", "experience_war", "experience_war_TXT", "war_injury",
            "loss_during_war", "time_spent_in_war", "time_spent_in_war_TXT",
            "Expl_Distress_txt", "Expl_coping_txt", "Final_open", "PSS10_avg",
            "SLON3_avg", "neu", "ext", "ope", "agr", "con", "SPS_avg",
            "Scale_UCLA_TRI_avg"]
           + [f"Scale_UCLA_TRI_{i}" for i in range(1, 5)]
           + [f"PS_PTSD_{i}" for i in range(1, 6)])


def fetch() -> Path:
    p = RAW_DIR / FILE
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=900)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_csv(fetch(), low_memory=False, encoding_errors="replace")
    assert d.shape == (125306, 154), d.shape
    items = [c for its, _ in TABLES.values() for c in its]
    accounted = {"ID"} | set(items) | set(COVS) | set(SKIPPED)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    assert d["ID"].is_unique
    assert (d["Dem_age"] >= 18).all()
    # the items are stored unreversed: the deposit's own PSS10_avg reproduces
    pss = d[TABLES["pss10"][0]].copy()
    for i in (4, 5, 7, 8):
        pss[f"Scale_PSS10_UCLA_{i}"] = 6 - pss[f"Scale_PSS10_UCLA_{i}"]
    assert (pss.mean(axis=1) - d["PSS10_avg"]).abs().max() < 1e-5

    d = d.rename(columns={"ID": "id", **COVS})
    covs = list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    names = [P + k for k in TABLES]
    assert len(set(names)) == len(names) and all(len(n) <= 40 for n in names)
    for key, (its, pv_set) in TABLES.items():
        name = P + key
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        if key == "distress":
            na = t["resp"] == 99
            print(f"  {name}: dropped {na.sum()} 'does not apply' (99) responses")
            t = t[~na]
        t["item"] = (t["item"].str.replace(r"^Scale_PSS10_UCLA_", "PSS10_", regex=True)
                     .str.replace(r"^Scale_SLON_", "SLON_", regex=True))
        its = [i.replace("Scale_PSS10_UCLA_", "PSS10_").replace("Scale_SLON_", "SLON_") for i in its]
        assert set(t["item"]) == set(its)
        assert (t["resp"] % 1 == 0).all()
        t["resp"] = t["resp"].astype(int)
        assert set(t["resp"]) <= pv_set, (name, sorted(set(t["resp"])))
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any()
        pv = {i: pv_set for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message[:150]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
