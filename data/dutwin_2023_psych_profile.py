#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/ZLFLRT (Harvard Dataverse)
# DOI: 10.7910/DVN/ZLFLRT (dataset, 2023; Dutwin, David). Replication data for Dutwin, Bilgen & Hendarwan, "The
#   Psychological and Personality-Based Underpinnings of Survey Nonresponse and the Impact of Nonresponse Mitigation
#   Efforts" -- NORC AmeriSpeak Psychological Profile 2022, N = 5818 US adults, 18 sample groups (SAMPLE_NAME).
# Data: "psychological survey public.tab" (one row per respondent, 447 columns). The raw item blocks are read here;
#   the deposit's SAS file ("psych scales sas.txt") defines the derived columns (*_REV, *_VAL, TOT_*, *_SCALE, Z*_SCALE,
#   which are recodes, validity flags and scale scores and are NOT shipped) and so documents which columns are raw.
# Tables (blocks of 8 or more raw items on one scale):
#   dutwin_2023_personality  PERSONALITY_A..X, 24 items, 1-7 (6 factors x 4 items: extraversion, agreeableness,
#                            conscientiousness, neuroticism, openness, honesty-humility; HEXACO-style short form)
#   dutwin_2023_narcissism   NARCISSISM_1..8, forced choice between two statements (1/2; exhibitionism 3, entitlement 5)
#   dutwin_2023_cominv       COMINV_A..H, 8 items, 1-6 (community involvement)
#   dutwin_2023_fear         FEAR_1..8, 8 items, 1-5
# Not shipped: blocks under 8 items (TRUSTNEW 6, COMMUNAL 6, COMPASSION 7, MORALFABRIC 6, BENEFITS 6, PRIVACY 4,
#   POLCTRL 4, CHQLTY 4, ...), and COMMUNAL because its values run to 10 with no codebook.
# Codes 77/98/99 (refused / don't know / skipped style sentinels, per the SAS file's treatment of them as non-valid)
#   are removed as missing. Raw responses are shipped as stored: reverse-keyed items (the SAS file's *_REV columns) are
#   NOT recoded (datastandard.md). Item wording is not in the deposit (item names only).
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none. ID is a 1..N respondent serial; replaced by the row index anyway. No names, dates or geography in the
#   shipped columns; only age, gender, education, race/ethnicity and sample group are kept as covariates.
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_E_2026-10-16"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, original: bool = False, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset (ingested tab by default)."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        time.sleep(4)
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"] if f["dataFile"]["filename"] == fname][0]
        r = requests.get(f"https://{host}/api/access/datafile/{fid}",
                         params={"format": "original"} if original else {}, headers=UA, timeout=600)
        r.raise_for_status()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
        time.sleep(4)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values). QC, validate, write."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert max(map(len, tables)) <= 40, name
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 8, name
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
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")


SENTINELS = (77, 98, 99)
LET = list("ABCDEFGH")
BLOCKS = {  # table -> (item columns, top code)
    "dutwin_2023_personality": ([f"PERSONALITY_{c}" for c in "ABCDEFGHIJKLMNOPQRSTUVWX"], 7),
    "dutwin_2023_narcissism": ([f"NARCISSISM_{i}" for i in range(1, 9)], 2),
    "dutwin_2023_cominv": ([f"COMINV_{c}" for c in LET], 6),
    "dutwin_2023_fear": ([f"FEAR_{i}" for i in range(1, 9)], 5),
}
COVS = {"AGE": "cov_age", "GENDER_i": "cov_gender", "EDUC_5": "cov_education",
        "RACETHNICITY": "cov_race_ethnicity", "SAMPLE_NAME": "cov_sample"}


def main() -> None:
    p = dv_fetch("10.7910/DVN/ZLFLRT", "psychological survey public.tab", RAW_ROOT / "zlflrt")
    d = pd.read_csv(p, sep="\t", low_memory=False)
    assert len(d) == 5818 and d["ID"].is_unique
    d = d.reset_index(drop=True)
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    out = {}
    for name, (cols, top) in BLOCKS.items():
        items = {c: c.lower() for c in cols}
        t = d.melt(id_vars=["id"] + covs, value_vars=cols, var_name="item", value_name="resp")
        t = t[t["resp"].notna() & ~t["resp"].isin(SENTINELS)]
        assert (t["resp"] % 1 == 0).all()
        assert t["resp"].between(1, top).all(), (name, sorted(t["resp"].unique()))
        t["resp"] = t["resp"].astype(int)
        t["item"] = pd.Categorical(t["item"].map(items), categories=list(items.values()), ordered=True)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        t["item"] = t["item"].astype(str)
        out[name] = (t, {i: set(range(1, top + 1)) for i in items.values()})
    emit(out)


if __name__ == "__main__":
    main()
