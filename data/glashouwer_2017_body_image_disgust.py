#!/usr/bin/env python3

# Source: https://ssh.datastations.nl/dataset.xhtml?persistentId=doi:10.17026/DANS-Z7Q-7ATH
# DOI: 10.17026/dans-z7q-7ath
#   Glashouwer, K., Bennik, E. C., & von Spreckelsen, P. (2017). Negative Body
#   Image - Relationships with Heightened Disgust Propensity, Disgust
#   Sensitivity, and Self-Directed Disgust [Dataset]. DANS Data Station
#   Social Sciences and Humanities.
# Data: the deposit's two study files, read as .sav -- Study 1 (577
#   undergraduates) and Study 2 (346). Each study is deposited three times, as
#   .sav, .dta and .por; they are the same data in three formats, and only the
#   .sav is read.
# License: CC0 1.0 (verified on the DANS record, 2026-10-19).
# Item text: NOT shipped. The deposit ships a codebook-and-documentation PDF,
#   so a later text pass has somewhere to start, but all four instruments here
#   are published scales with no rights-register verdict.
#
# SEVEN tables, complete in both studies:
#   glashouwer_2017_dpss_study1   16 items, 1-5  (Disgust Propensity and
#   glashouwer_2017_dpss_study2   16 items, 1-5   Sensitivity Scale)
#   glashouwer_2017_sds_study1    18 items, 1-7  (self-directed disgust)
#   glashouwer_2017_sds_study2    18 items, 1-7
#   glashouwer_2017_sdes_study2   16 items, 1-7  (self-disgust experiences;
#                                                 Study 2 only)
#   glashouwer_2017_tdss_study2   25 items, 0-6  (trait disgust, three
#                                                 domains; Study 2 only)
#
# THE EDE-Q BLOCK IS DEFERRED IN BOTH STUDIES, and the reason is a mixed
#   response metric the deposit does not document. Its 28 columns hold 0-6
#   ratings for most items but 247-288 cells (of ~10k and ~16k) carry values
#   outside that range -- 7, 8, ... up to 15 and above -- which is what the
#   EDE-Q's first twelve questions look like when they are recorded as RAW
#   DAYS OUT OF 28 rather than as the questionnaire's 0-6 bands, plus a few
#   fractional values (3.5, 0.01, 4e-05) that fit neither. Shipping the block
#   as one scale would mix two metrics on one item set; splitting it needs the
#   codebook read against each item. Recorded in the batch's leads file.
#
# NOT SHIPPED besides that: the deposit's own reverse-scored copies (r_SDES*,
#   r_SDS*), its composites (totalSDS, totalSDES, DPSS_S, DPSS_P, DPSS_total,
#   TDSSmor/TDSSpath/TDSSsex, Negative_Body_Image, EDEQ_total) and the EDE-Q
#   letter-suffixed sub-grids in Study 1 (EDEQ1A-EDEQ1Z), which belong to the
#   deferred block.
#
# id: the row index, per study. Neither file carries a respondent id.
# Covariates: cov_age and cov_bmi in both studies, plus cov_gender in Study 2;
#   Study 1's file records no gender column at all.
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
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "tail_batch" / "z7q7ath" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BASE = "https://ssh.datastations.nl"
STUDIES = {"study1": (181091, 577), "study2": (181093, 346)}
BLOCKS = {
    "dpss": ([f"DPSS{i}" for i in range(1, 17)], set(range(1, 6))),
    "sds": ([f"SDS{i}" for i in range(1, 19)], set(range(1, 8))),
    "sdes": ([f"SDES{i}" for i in range(1, 17)], set(range(1, 8))),
    "tdss": ([f"TDSS_{i}" for i in range(1, 26)], set(range(0, 7))),
}
COVS = {"Age": "cov_age", "BMI": "cov_bmi", "bmi": "cov_bmi",
        "Gender": "cov_gender"}


def fetch(fid: int, study: str) -> Path:
    p = RAW_DIR / f"{study}.sav"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(f"{BASE}/api/access/datafile/{fid}",
                         params={"format": "original"}, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    made = 0
    for study, (fid, n_rows) in STUDIES.items():
        df, _ = pyreadstat.read_sav(str(fetch(fid, study)),
                                    apply_value_formats=False)
        assert len(df) == n_rows, (study, len(df))
        df = df.rename(columns={k: v for k, v in COVS.items() if k in df.columns})
        df["id"] = range(1, len(df) + 1)
        cov_cols = [c for c in ("cov_age", "cov_bmi", "cov_gender")
                    if c in df.columns]
        for cov in cov_cols:
            v = pd.to_numeric(df[cov], errors="coerce")
            df[cov] = v.astype("Int64") if (v.dropna() % 1 == 0).all() else v
        edeq = [c for c in df.columns if c.startswith("EDEQ")]
        print(f"{study}: {len(df)} respondents, covariates {cov_cols}; "
              f"{len(edeq)} EDE-Q columns deferred (see the header note)")

        for block, (cols, scale) in BLOCKS.items():
            present = [c for c in cols if c in df.columns]
            if not present:
                continue
            assert len(present) == len(cols), (study, block, len(present))
            name = f"glashouwer_2017_{block}_{study}"
            t = (df[["id", *cov_cols, *present]]
                 .melt(id_vars=["id", *cov_cols], value_vars=present,
                       var_name="item", value_name="resp")
                 .dropna(subset=["resp"]))
            t["resp"] = pd.to_numeric(t["resp"])
            assert (t["resp"] % 1 == 0).all(), name
            t["resp"] = t["resp"].astype(int)
            bad = sorted(set(t["resp"]) - scale)
            assert not bad, f"{name}: resp outside the scale: {bad}"
            t = t[["id", "item", "resp", *cov_cols]]
            assert not t.duplicated(["id", "item"]).any(), name
            assert t["item"].nunique() == len(cols), name
            assert t["id"].nunique() >= 100, (name, t["id"].nunique())
            checks = run_qc(t, permitted_values=scale)
            fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
            assert not fails, (name, fails)
            for c in checks:
                if c.status == "warn":
                    print(f"    [qc warn] {name} {c.name}: {c.detail[:130]}")
            report = irw_validate.validate_frame(
                t, label=name, profile="upload",
                context={"permitted_values": scale})
            assert report.conforms and not report.errors, \
                (name, [(f.check, f.message) for f in report.errors])
            t.to_csv(OUT_DIR / f"{name}.csv", index=False)
            made += 1
            print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
                  f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert made == 6, made


if __name__ == "__main__":
    main()
