#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/KJKXEB (Harvard Dataverse)
# Christensen, R., & Wright, B. E. Replication Data for "Additional intervention evidence on the relationship between
#   public service motivation and ethical behavior" [Data set]. Harvard Dataverse (deposit released 2021-01-01; the
#   deposit calls it "2017 Replication Data" and the file is PSM_2017_Replication_DataVerse.xlsx, so 2017 is used as
#   the table year; no paper citation or DOI in the deposit, year not verified against the journal).
# Data: PSM_2017_Replication_DataVerse.xlsx (Sheet1; row 1 = question text, row 2 = codes/value labels, rows 3-311 =
#   309 respondents, 52 columns), fetched in original format. US students who are or will be enrolled in college,
#   online experiment: control v. treatment (public-service-motivation writing prime, Control 1/Treatment 2).
# Tables (one sample, N = 309; separate files per instrument):
#   christensen_2017_bfi10   10 items Opinion_13..Opinion_22, the BFI-10 ("I see myself as someone who ..."), 7-point
#                            agree/disagree. The deposit's code row labels Strongly agree = 8 ... Strongly disagree =
#                            14, so resp = 15 - code to make higher = more agreement (1 strongly disagree - 7
#                            strongly agree). Direction is therefore documented by the deposit's own labels. Items
#                            are NOT reverse-scored (reserved, lazy, relaxed, few artistic interests, fault-finding
#                            are negatively keyed on their trait; keying is left to the analyst).
#   christensen_2017_unethical  9 scenarios Scenario_* (fast food, copies, exam, change, answers, software, insider,
#                            recycled, candidate): "What is the percentage chance that you will engage in the behavior
#                            described", 0-100 slider/typed percent, kept continuous. Higher = more likely to behave
#                            unethically. treat = Control v. Treatment (the experiment precedes these items).
# Not shipped: Opinion_1..12 (mixed unnamed individualism/collectivism and prosocial statements; no scale definition
#   in the deposit, and the code row for Opinion_1 wrongly reads '% chance'), Opinion_23-25 (single items),
#   free-text writing responses, Time/Enrolled/Nonmobile/Heads (design variables), State.
# id: row index (the file's ResponseID is a Qualtrics platform ID, dropped).
# Covariates: cov_age (18-60, adults only), cov_sex (1 female, 2 male as coded), cov_race (1 Black, 2 Asian, 3 White
#   non-Hispanic, 4 Hispanic, 5 and 6 as coded in the deposit, labels for 5/6 not given), cov_region (US census region
#   from the deposit's Region column).
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-17).
# PII: none in shipped columns; ResponseID dropped; free-text columns not read into the output and screened for e-mail
#   addresses and phone numbers (none found).
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
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


def main() -> None:
    p = dv_fetch("10.7910/DVN/KJKXEB", "PSM_2017_Replication_DataVerse.xlsx", RAW_ROOT / "kjkxeb", "psm.xlsx")
    d = pd.read_excel(p)
    codes = d.iloc[1]  # sheet row 1 = question text, row 2 = codes / value labels, then the responses
    d = d[d["ResponseID"].astype(str).str.startswith("R_")].reset_index(drop=True)
    assert len(d) == 309 and d["ResponseID"].is_unique
    assert "Strongly agree (8)" in codes["Opinion_13"] and "Strongly disagree (14)" in codes["Opinion_13"]
    d["id"] = np.arange(1, len(d) + 1)
    num = lambda s: pd.to_numeric(s, errors="coerce")
    d["cov_age"] = num(d["Age"])
    assert d["cov_age"].min() >= 18 and d["cov_age"].notna().all()
    d["cov_sex"] = num(d["Sex"])
    d["cov_race"] = num(d["Ethnicity/Race"])
    d["cov_region"] = d["Region"].astype(str)
    d["treat"] = (num(d["Control"]) == 2).astype(int)
    assert set(num(d["Control"]).unique()) == {1, 2}
    covs = ["cov_age", "cov_sex", "cov_race", "cov_region"]

    def long(cols, names, transform, valid):
        sub = d[["id", "treat"] + covs].copy()
        for c, n in zip(cols, names):
            sub[n] = transform(num(d[c]))
        t = sub.melt(id_vars=["id", "treat"] + covs, value_vars=names, var_name="item", value_name="resp")
        t = t[t["resp"].notna()]
        assert t["resp"].map(valid).all(), "resp outside valid range"
        t["item"] = pd.Categorical(t["item"], categories=names, ordered=True)
        t = t.sort_values(["id", "item"]).reset_index(drop=True)
        t["item"] = t["item"].astype(str)
        for c in ("cov_age", "cov_sex", "cov_race"):
            t[c] = t[c].astype("Int64")
        return t[["id", "item", "resp", "treat"] + covs]

    bfi_cols = [f"Opinion_{i}" for i in range(13, 23)]
    bfi_names = ["bfi_reserved", "bfi_trusting", "bfi_lazy", "bfi_relaxed", "bfi_few_artistic", "bfi_outgoing",
                 "bfi_fault_finding", "bfi_thorough", "bfi_nervous", "bfi_imagination"]
    t1 = long(bfi_cols, bfi_names, lambda s: 15 - s, lambda v: v in range(1, 8))
    t1["resp"] = t1["resp"].astype(int)
    sc_cols = [c for c in d.columns if c.startswith("Scenario_")]
    assert len(sc_cols) == 9
    t2 = long(sc_cols, [c.lower() for c in sc_cols], lambda s: s, lambda v: 0 <= v <= 100)
    w = t1.pivot(index="id", columns="item", values="resp")
    print("    BFI-10 min inter-item r = %.2f; outgoing-reserved r = %.2f" % (np.nanmin(w.corr().values), w["bfi_outgoing"].corr(w["bfi_reserved"])))
    emit({
        "christensen_2017_bfi10": (t1, {n: set(range(1, 8)) for n in bfi_names}),
        "christensen_2017_unethical": (t2, {}),
    })


if __name__ == "__main__":
    main()
