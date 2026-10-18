#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/EWHO0O (Harvard Dataverse)
# Amornsriwatanakul, A., Chia, M., Promjun, T., & Abdul Rahman, H. (2025). Dataset on Physical Activity, Health Risk
#   Factors, and Mental Wellbeing of University Students in ASEAN (Association of South East Asian Nations) University
#   Network - Health Promotion Network [Data set]. Harvard Dataverse. (AUN-HPN Physical Activity Study, 2021.)
# Data: ALL_aun_pacs210914.xlsx, sheet aun_mi (15,366 students, 164 columns; codebook sheet documents every column).
# Tables (Section 5 of the survey, "support from family and friends", 3-month recall; codebook response labels:
#   None (1), Rarely (2), A few times (3), Often (4), Very often (5), Does not apply (6)):
#   amornsriwatanakul_2025_family_support  12 items s_family1-12, 1-5
#   amornsriwatanakul_2025_friend_support  12 items s_friend1-12, 1-5 (same 12 statements about friends)
#   The 12 statements (codebook): 1 exercised with me; 2 encouraged me to stick with my exercise program; 3 changed their
#   schedule so we could exercise together; 4 offered to exercise with me; 5 gave helpful reminders; 6 planned exercise on
#   recreational outings; 7 discussed exercise with me; 8 talked about how much they like to exercise; 9 helped plan
#   activities around my exercise; 10 asked me for ideas on how they can get more exercise; 11 took over chores so I had
#   more time to exercise; 12 made positive comments about my physical appearance.
# "Does not apply" (6, about 3-6% per item) is not an ordinal response and is set to missing (cell dropped).
# Direction: all 24 statements are positively worded; all 132 + 132 inter-item correlations are positive
#   (0.38-0.73), so nothing is flipped (labels and data agree).
# Not shipped: WEMWBS (7 items) and physical-activity attitude (5 items) are under 8 items; the PANES environment block
#   (panes1-10), health-risk-behaviour block (hrb_*) and GPAQ items mix yes/no, unordered and count formats; sport/minute
#   columns are derived or conditional counts.
# Minors: the survey records age (15-36, missing for 1,769 students). The 145 respondents with a recorded age under 18
#   are dropped; the rest are university students and are treated as adults (missing age is not grounds to drop).
# Covariates: cov_gender (1 male, 2 female), cov_age, cov_country (country of birth), cov_year_of_study (1-5, 5 = year 5
#   or more).
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none. `pin` is the codebook's "anonymous participant identity number" and equals the row number (asserted);
#   id is the row index. University name and free-text opinions are not shipped.
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

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_K_2026-10-16"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        time.sleep(4)
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"] if f["label"] == fname][0]
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
    p = dv_fetch("10.7910/DVN/EWHO0O", "ALL_aun_pacs210914.xlsx", RAW_ROOT / "ewho0o")
    d = pd.read_excel(p, sheet_name="aun_mi")
    assert d.shape == (15366, 164)
    assert (d["pin"].to_numpy() == np.arange(1, len(d) + 1)).all()
    d = d.copy()
    d["id"] = d["pin"].astype(int)
    n_minor = int((d["age"] < 18).sum())
    assert n_minor == 145, n_minor
    d = d[~(d["age"] < 18)].copy()
    d["cov_gender"] = d["gender"].where(d["gender"].isin([1, 2])).astype("Int64")
    d["cov_age"] = d["age"].astype(float)  # 3 fractional ages (18.5, 21.4) kept as given
    d["cov_country"] = d["country"].astype(str).str.strip().str.title()
    d["cov_year_of_study"] = d["year"].astype("Int64")
    covs = ["cov_gender", "cov_age", "cov_country", "cov_year_of_study"]
    out = {}
    for key, pre in (("family", "s_family"), ("friend", "s_friend")):
        items = [f"{pre}{i}" for i in range(1, 13)]
        w = d[items]
        assert w.stack().isin([1, 2, 3, 4, 5, 6]).all()
        cc = w.replace(6, np.nan).corr().to_numpy()
        assert (cc[np.triu_indices(12, 1)] > 0).all()
        t = d.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
        t = t[t["resp"].notna() & (t["resp"] != 6)].copy()
        t["resp"] = t["resp"].astype(int)
        t["item"] = pd.Categorical(t["item"], categories=items, ordered=True)
        t = t.sort_values(["id", "item"]).reset_index(drop=True)
        t["item"] = t["item"].astype(str)
        t = t[["id", "item", "resp"] + covs]
        out[f"amornsriwatanakul_2025_{key}_support"] = (t, {c: {1, 2, 3, 4, 5} for c in items})
    emit(out)


if __name__ == "__main__":
    main()
