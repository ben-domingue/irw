#!/usr/bin/env python3

# Source: https://zenodo.org/records/11525033
# DOI: 10.5281/zenodo.11525033
#   Mairean, Cornelia (2024). Can time heal anything? Exposure to traumatic events,
#   time perspective and quality of life [Dataset]. Zenodo.
# Data: "Database.sav" -- 362 Romanian adults, several instruments in one sitting.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped. Both label levels checked: only 5 of 178 variables carry a
#   variable label and all five are Zscore(...) derived columns; 5 carry value labels,
#   all demographics. So the file holds neither stems nor anchors for any item. The
#   instruments are published ones named in the paper.
# Naming: this author already has mairean_2023_childhood_trauma,
#   mairean_2023_conspiracy_dogmatism and mairean_2024_health_death_anxiety, so this
#   2024 deposit takes mairean_2024b_*.
#
# FOUR tables ship; TWO instruments are WITHHELD on rights:
#   mairean_2024b_lec    34 items, 0/1. The Life Events Checklist asked twice per
#                        event -- D_LEC_1-17 direct exposure, I_LEC_1-17 indirect.
#                        Both halves ship as distinct item codes because the item IS
#                        "event k, directly experienced"; the register row for
#                        LEC-5 is ship_with_note, not block.
#   mairean_2024b_aadl   13 items, 1-3  (advanced activities of daily living)
#   mairean_2024b_das    15 items, 1-5
#   mairean_2024b_aarc   10 items, 1-5  (awareness of age-related change)
#   mairean_2024b_art    21 items, 1-7  (the deposit's ART block; its subscales are
#                        ART_intensitate/coerenta/retraire/..., all derived)
# WITHHELD:
#   QoL_1-26   WHOQOL-BREF. Register row "WHOQOL family (WHOQOL-BREF, WHOQOL-100) and
#              its translations", verdict BLOCK, and its own matcher
#              `whoqol|^qol[_ ]?[0-9` matches these codes. 26 items is the BREF's
#              exact length. Ben ruled 2026-09-29 that a block row covers every
#              language, so the Romanian administration is covered.
#   ZTPI_1-18  Zimbardo Time Perspective Inventory. Register row verdict BLOCK.
#              Caught by reading the block, not by the matcher: the register's code
#              pattern is ^ZTPIQ[0-9]+R?$, which does NOT match ZTPI_1.
# Not shipped besides those: every derived column -- the LEC_/ZTPI_/AADL_/ART_/QoL_
#   named subscale scores, the Z* z-scores and the LECxAADL / ARTxAADL interaction
#   terms.
# id: the file carries no respondent id, so the 0-based row index is used; each row
#   is one respondent.
# Covariates: cov_age, cov_sex, cov_locality, cov_education, cov_marital_status,
#   cov_diagnosis.
import os
import re
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
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "11525033"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 11525033, "Database.sav"

COVS = {"Varsta": "cov_age", "Sex": "cov_sex", "Mediul": "cov_locality",
        "Studii": "cov_education", "Stare_civilă": "cov_marital_status",
        "Diagnostic": "cov_diagnosis"}
BLOCKS = {
    "mairean_2024b_lec": ([f"D_LEC_{i}" for i in range(1, 18)]
                          + [f"I_LEC_{i}" for i in range(1, 18)], {0, 1}),
    "mairean_2024b_art": ([f"ART_{i}" for i in range(1, 22)], set(range(1, 8))),
    "mairean_2024b_aadl": ([f"AADL_{i}" for i in range(1, 14)], {1, 2, 3}),
    "mairean_2024b_das": ([f"DAS_{i}" for i in range(1, 16)], set(range(1, 6))),
    "mairean_2024b_aarc": ([f"AARC_{i}" for i in range(1, 11)], set(range(1, 6))),
}
WITHHELD = ([f"QoL_{i}" for i in range(1, 27)]
            + [f"ZTPI_{i}" for i in range(1, 19)])


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                         headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    df.insert(0, "id", range(len(df)))

    items = {c for cols, _ in BLOCKS.values() for c in cols}
    for c in items | set(WITHHELD):
        assert c in df.columns, f"expected column {c} is absent"
    print(f"  withheld {len(WITHHELD)} columns on rights "
          f"(WHOQOL-BREF 26, ZTPI 18)")
    accounted = {"id"} | set(COVS) | items | set(WITHHELD)
    for c in df.columns:
        if c not in accounted:
            print(f"  skipped {c}: derived subscale score, z-score or "
                  f"interaction term, not an item")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, (cols, scale) in BLOCKS.items():
        t = (df[["id", *COVS, *cols]]
             .melt(id_vars=["id", *COVS], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"])
             .rename(columns=COVS))
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{name}: resp outside the block's observed scale: {bad}"
        for c in COVS.values():
            t[c] = t[c].astype("Int64")
        t = t[["id", "item", "resp", *COVS.values()]]

        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert name not in written
        checks = run_qc(t)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:170]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload")
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
