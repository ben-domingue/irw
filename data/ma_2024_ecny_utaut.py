#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/28138236
# DOI: 10.6084/m9.figshare.28138236
#   Ma, Y., Al Mamun, A., Masukujjaman, M., & Ja'afar, R. (2025). Additional
#   file 2 of "Modeling the significance of unified theory of acceptance and
#   use of technology in predicting the intention and usage of eCNY"
#   [Dataset]. figshare.
# Paper: 10.1186/s40854-024-00712-5 (Financial Innovation) -- open access.
# Data: "40854_2024_712_MOESM2_ESM.csv" -- 809 respondents from eCNY pilot
#   communities in the Yangtze River Delta, Pearl River Delta and
#   Beijing-Tianjin-Hebei, 45 items on a 1-7 agreement scale.
# License: CC BY (verified on the figshare record; the article is CC BY 4.0).
# Item text: NOT shipped. The .csv is one header row of bare construct codes
#   with no label level. The stems are in the paper's own measurement table
#   (Appendix/Table of items in 10.1186/s40854-024-00712-5), which is where a
#   later pass should start; most are adapted Venkatesh UTAUT items, so a
#   rights ruling is wanted before any of that wording ships.
#
# CONSTRUCT NAMES come from the paper, not from a guess at the prefixes: PS is
#   "perceived security risk", PP "perceived privacy risk", PG "perceived
#   government policy", IeCNY intention toward the eCNY, AeCNY its actual use
#   (section headings of 10.1186/s40854-024-00712-5).
#
# NINE tables, one per measured construct (the convention this #3077 run has
#   followed for PLS-SEM batteries), all 809 respondents x 1-7:
#   ma_2024_performance_expectancy     PE1-5
#   ma_2024_effort_expectancy          EE1-5
#   ma_2024_social_influence           SI1-5
#   ma_2024_facilitating_conditions    FC1-5
#   ma_2024_security_risk              PS1-5
#   ma_2024_privacy_risk               PP1-5
#   ma_2024_government_policy          PG1-5
#   ma_2024_ecny_intention             IeCNY1-5
#   ma_2024_ecny_use                   AeCNY1-5
# id: the file carries no respondent id; the 0-based row index is used.
# Covariates: the seven demographics are option-coded with no codebook in the
#   deposit or the paper, so only the two the paper interprets (sex, age band)
#   are shipped, as cov_gender / cov_age_band; the rest are dropped with a
#   printed reason rather than shipped as unlabelled integers.
# Dropped: "Random" (a sort key) and the nine PE..AeCNY subscale means.
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
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "figshare_batch" / "28138236" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE, FNAME = 28138236, "40854_2024_712_MOESM2_ESM.csv"
SCALE = set(range(1, 8))

BLOCKS = {
    "ma_2024_performance_expectancy": ("PE", 5),
    "ma_2024_effort_expectancy": ("EE", 5),
    "ma_2024_social_influence": ("SI", 5),
    "ma_2024_facilitating_conditions": ("FC", 5),
    "ma_2024_security_risk": ("PS", 5),
    "ma_2024_privacy_risk": ("PP", 5),
    "ma_2024_government_policy": ("PG", 5),
    "ma_2024_ecny_intention": ("IeCNY", 5),
    "ma_2024_ecny_use": ("AeCNY", 5),
}
COVS = {"Gender": "cov_gender", "Age": "cov_age_band"}
DROP_DEMOG = ["Marital_status", "Education", "Employment_Sector",
              "Average_monthly_income", "Location"]
DROP_DERIVED = ["Random", "PE", "EE", "SI", "FC", "PS", "PP", "PG",
                "IeCNY", "AeCNY"]


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                         headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_csv(fetch())
    df.insert(0, "id", range(len(df)))

    blocks = {name: [f"{pre}{i}" for i in range(1, n + 1)]
              for name, (pre, n) in BLOCKS.items()}
    items = {c for cols in blocks.values() for c in cols}
    for c in items | set(COVS) | set(DROP_DEMOG) | set(DROP_DERIVED):
        assert c in df.columns, f"expected source column {c} is absent"
    unaccounted = [c for c in df.columns
                   if c not in ({"id"} | items | set(COVS)
                                | set(DROP_DEMOG) | set(DROP_DERIVED))]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"dropped, option-coded with no codebook anywhere: {DROP_DEMOG}")
    print(f"dropped, derived or administrative: {DROP_DERIVED}")

    for src, cov in COVS.items():
        df[cov] = pd.to_numeric(df[src]).astype(int)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in blocks.items():
        t = (df[["id", *COVS.values(), *cols]]
             .melt(id_vars=["id", *COVS.values()], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the documented 1-7 scale: {bad}"
        t = t[["id", "item", "resp", *COVS.values()]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert name not in written
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:170]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
