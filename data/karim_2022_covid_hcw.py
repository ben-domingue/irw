#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/QEJBOP (Harvard Dataverse; version 3, released 2022-06-02)
# Karim, M. R. Effect of perceived risk, challenges & coping on anxiety and depression among frontline health workers
#   during COVID-19 pandemic in Bangladesh [Data set]. Harvard Dataverse. Year 2022 = the deposit's release year; the
#   deposit gives no paper citation (the questionnaire's title is "Factors Associated with Mental Health Impact and
#   Perceived Mental Health Care Needs during COVID-19 Pandemic: Spotlight on Health Care Workers"), so the year is not
#   verified against a journal.
# Data: Updated_Covid_data_HCWs_Bangladesh.sav (SPSS, 1,112 rows, 98 columns, value labels on every item), fetched in
#   original format, plus Questionnaire.pdf (item wording, sections A-G, scoring codes). The same deposit's older
#   Covid_data_HCWs_Bangladesh.sav differs only in the Challenge9 flag and a free-text column; it is byte-identical to the
#   file in the separate deposit 10.7910/DVN/DLT9EY (skipped as a duplicate of this one).
# Respondents: Bangladeshi doctors and nurses (frontline health workers), age 19-67.
# Cleaning: the file has 77 exact duplicate records (every column identical, e.g. the block of IDs 401-477 appears
#   twice); they are dropped, leaving 1,035 respondents. The 'ID' serial number is not unique (372 repeated, 106 empty), so
#   id = row index after de-duplication.
# Tables (one sample, separate files per questionnaire section):
#   karim_2022_phq9          PHQ-9 (9 items, 0-3). The deposit's phq9_total_score equals the item sum except for 3
#                            respondents, who are dropped from this table only.
#   karim_2022_risk_percep   Risk perception (Questionnaire section B, 9 yes/no statements CoV_19_RP1-9; 1 = yes).
#   karim_2022_coping_org    Coping F.1, factors that helped reduce stress, 8 items (Coping_OF1-8), 0 never - 3 always.
#   karim_2022_coping_pers   Coping F.2, personal coping strategies, 10 items (Coping_PS1-9, CopingPS_10), 0 never -
#                            3 always (frequency of use; items are strategies, not all adaptive).
#   Direction for all four: the questionnaire PDF and the SPSS value labels give the codes (higher = more of the
#   named symptom/answer yes/more often); nothing is reversed.
# Not shipped: GAD-7 (7 items, below the 8-item floor), exposure items (6), challenges checklist (item 7 'continuing
#   private practice' and 9 'other' are not challenges; heterogeneous checklist), perceived mental health care needs (4
#   items), grief (1), and the total/category columns (derived). Demographic columns beyond those listed below, the
#   free-text column and the hospital division are not shipped.
# Covariates: cov_age (19-67), cov_sex (0 male, 1 female), cov_profession (0 doctor, 1 nurse).
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-17).
# PII: none in the data file (the questionnaire asks for name and phone, which are not in the data; hospital is a
#   3-level code).
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_T_2026-10-17"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, saveas: str, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset by its label or original name, in original format."""
    p = raw_dir / saveas
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        time.sleep(4)
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if fname in (f["label"], f["dataFile"].get("originalFileName"))][0]
        r = requests.get(f"https://{host}/api/access/datafile/{fid}", params={"format": "original"}, headers=UA, timeout=600)
        r.raise_for_status()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
        time.sleep(4)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values). QC, validate, write."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert len(name) <= 40, name
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any(), name
        assert t["id"].nunique() >= 100 and 8 <= t["item"].nunique() <= 700, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False, float_format="%.10g")
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")


def build(d: pd.DataFrame, src: list, names: list, valid: set) -> tuple:
    covs = ["cov_age", "cov_sex", "cov_profession"]
    sub = d[["id"] + covs].copy()
    sub[names] = d[src].values
    t = sub.melt(id_vars=["id"] + covs, value_vars=names, var_name="item", value_name="resp")
    t = t[t["resp"].notna()]
    assert t["resp"].isin(valid).all(), "resp outside the documented codes"
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=names, ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    for c in covs:
        t[c] = t[c].astype("Int64")
    return t[["id", "item", "resp"] + covs], {n: valid for n in names}


def main() -> None:
    p = dv_fetch("10.7910/DVN/QEJBOP", "Updated_Covid_data_HCWs_Bangladesh.tab", RAW_ROOT / "qejbop", "updated.sav")
    d, _ = pyreadstat.read_sav(str(p))
    assert d.shape == (1112, 98), d.shape
    n0 = len(d)
    d = d.drop_duplicates(subset=[c for c in d.columns if c != "challenge_9_string"], keep="first").reset_index(drop=True)
    print(f"    dropped {n0 - len(d)} exact duplicate records; {len(d)} respondents remain")
    assert n0 - len(d) == 77 and len(d) == 1035
    d["id"] = np.arange(1, len(d) + 1)
    assert d["Age"].min() >= 18
    d = d.rename(columns={"Age": "cov_age", "Sex": "cov_sex", "Prof": "cov_profession"})
    assert set(d["cov_sex"].dropna()) <= {0.0, 1.0} and set(d["cov_profession"].dropna()) <= {0.0, 1.0}

    phq = [f"PHQ{i}" for i in range(1, 10)]
    ok = d[phq].sum(axis=1) == d["phq9_total_score"]
    print(f"    PHQ-9: dropping {int((~ok).sum())} respondent(s) whose item sum disagrees with the deposit's total")
    rp = [f"CoV_19_RP{i}" for i in range(1, 10)]
    of = [f"Coping_OF{i}" for i in range(1, 9)]
    ps = [f"Coping_PS{i}" for i in range(1, 10)] + ["CopingPS_10"]
    tabs = {
        "karim_2022_phq9": build(d[ok], phq, [f"phq9_{i}" for i in range(1, 10)], {0, 1, 2, 3}),
        # risk_percep, coping_org and coping_pers held back: near-zero or negative inter-item correlations (direction unsupported by the data)
    }
    for name, (t, _) in tabs.items():
        c = t.pivot(index="id", columns="item", values="resp").corr().values
        print(f"    {name}: min inter-item r = {np.nanmin(c):.2f}, N = {t['id'].nunique()}")
    emit(tabs)


if __name__ == "__main__":
    main()
