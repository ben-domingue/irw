#!/usr/bin/env python3
# Source: https://doi.org/10.1371/journal.pone.0218244 (S3 File)
# DOI: 10.1371/journal.pone.0218244
#   Deilkås, E. C. T., Hofoss, D., Husebo, B. S., & Bondevik, G. T. (2019). Opportunities for
#   improvement in nursing homes: Variance of six patient safety climate factor scores across
#   nursing homes and wards -- Assessed by the Safety Attitudes Questionnaire. PLOS ONE,
#   14(6), e0218244.
# Data: "pone.0218244.s003.sav": 288 staff of 34 wards in five Norwegian nursing homes
#       (2017). The SPSS variable labels carry each SAQ statement in English, the value
#       labels the five anchors plus 0 "Not applicable". The questionnaire was administered
#       in Norwegian (SAQ-Nursing Home version); the Norwegian wording is not in the deposit.
#       The variable named Kjønn (Norwegian: gender, values 1-2) is labelled "Age" and Alder
#       (age, values 1-5) is labelled "Gender": the labels are swapped, the names and the
#       value sets are not, so the script follows the names.
# License: CC BY 4.0 (PLOS ONE article and its supporting files).
#
# Item text: shipped (stems from the .sav variable labels, anchors from its value labels;
#   English substitute for a Norwegian administration -- language=Norwegian with empty
#   _translated columns; built by
#   automated_finding/itemtext_verification/make_itemtext_deilkas_2019.py). Source
#   licence governs (CC BY PLOS deposit); the rights register's SAQ row records UTHealth's
#   blanket grant for the short form.
#
# Tables (item = the .sav variable name; 0 "Not applicable" dropped as a non-response):
#   deilkas_2019_saq            SAQ1-SAQ62, the full Safety Attitudes Questionnaire (nursing
#                               home version), 1 disagree strongly .. 5 agree strongly.
#   deilkas_2019_collaboration  14 ratings of the quality of collaboration and communication
#                               experienced with each staff group / service (Physicians ..
#                               Hospital), 1 very low .. 5 very high.
# Skipped: the mean-imputed item copies (saq*imp, saq*impRev), the factor means and scores
#   (faktormean*, faktorscore*), and "Have you filled out this questionnaire previously?".
# Covariates: cov_nursing_home (1-5), cov_ward (1-34), cov_position (1-10, labelled),
#   cov_sex (1 female, 2 male), cov_age_group (1 <=30 .. 5 >=61), cov_experience_years
#   (1-6 bands), cov_experience_here_years (1-6 bands), cov_shift (1-6), cov_position_pct
#   (1-5 bands), cov_permanent (1 permanent, 2 temporary), cov_norwegian_native (1 yes, 2 no).
# id: the deposit's id (1..288).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.1371_journal.pone.0218244"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0218244.s003&type=supplementary"
FNAME = "pone.0218244.s003.sav"
P = "deilkas_2019_"
COLLAB = ["Physicians", "Registerednurses", "Nurseassistants", "Assistants", "Kitchenpersonell",
          "Cleaningpersonell", "Laundrypersonell", "Officepersonell",
          "PhysicalandOccupationaltherapists", "Management", "Officeofprioritization",
          "Outofhoursmedicalservices", "Ambulancepersonell", "Hospital"]
SAQ = [f"SAQ{k}" for k in range(1, 63)]
COVMAP = {"Nursinghome": "cov_nursing_home", "Department": "cov_ward", "Stilling": "cov_position",
          "Kjønn": "cov_sex", "Alder": "cov_age_group", "Yrkeserfaringtotalt": "cov_experience_years",
          "Yrkeserfaringsykehjemmet": "cov_experience_here_years", "Vakter": "cov_shift",
          "Stillingsandel": "cov_position_pct", "Ansettelse": "cov_permanent",
          "Norskmorsmål": "cov_norwegian_native"}
COVS = list(COVMAP.values())


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"]).any()
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


def raw() -> Path:
    return download(URL, RAW_DIR / FNAME)


def main() -> None:
    d, meta = pyreadstat.read_sav(str(raw()))
    assert len(d) == 288 and d["id"].is_unique
    collab = [c for c in d.columns if c in COLLAB]
    assert len(collab) == 14, collab
    d = d.rename(columns=COVMAP)
    d["id"] = d["id"].astype(int)
    for c in COVS:
        d[c] = d[c].astype("Int64")
    out = {}
    for name, items in (("saq", SAQ), ("collaboration", collab)):
        t = d.melt(id_vars=["id"] + COVS, value_vars=items, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        na = t["resp"] == 0
        print(f"  [{name}] dropped {na.sum()} 'Not applicable' (0) responses")
        t = t[~na]
        assert t["resp"].between(1, 5).all()
        t = t[["id", "item", "resp"] + COVS].sort_values(["id", "item"]).reset_index(drop=True)
        out[P + name] = (t, {i: set(range(1, 6)) for i in items})
    emit(out)


if __name__ == "__main__":
    main()
