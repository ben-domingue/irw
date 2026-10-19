#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/24588120
# DOI: 10.6084/m9.figshare.24588120
#   Gerou, S., & Adonis, M. (2023). Humility and Negative Affect: The Role of
#   Quiet Ego [Dataset]. figshare.
# Data: "Humility and Quiet Ego.sav" -- 188 respondents, three instruments
#   administered in Greek.
# License: CC BY 4.0 (verified on the figshare record).
# Item text: NOT shipped. Both label levels are populated and complete: every
#   item has its full Greek stem as a variable label and every block a full
#   set of English value labels, so extraction is solved. Held because all
#   three are published third-party instruments and none has a row in
#   itemtext/instrument_rights_register.csv -- the HEXACO Honesty-Humility
#   items (Lee & Ashton), DASS-21 (Lovibond & Lovibond 1995) and the Quiet Ego
#   Scale (Wayment, Bauer & Sylaska 2015). Under the 2026-10-15 silence rule
#   that is a hold, and the Greek wording would need a translation note too.
#   Identification is from the stems, not the labels: HH_2 is "if I knew I
#   would never be caught, I would be willing to steal a million euros",
#   HEXACO's Fairness item verbatim.
#
# DASS SENTINEL: DASS_8 carries the value 8 on a 0-3 scale. Nothing in the
#   file documents it, and 8 is the file's only out-of-range value anywhere,
#   so it is a user-missing code and those responses are dropped (not
#   recoded). The count is printed.
#
# ONE COLUMN NAME IS MISTYPED IN THE SOURCE: "ΗH_4" begins with a Greek
#   capital eta, not a Latin H. It is the fourth HEXACO item ("I am an
#   ordinary person who is no better than others", HEXACO's Modesty item), so
#   it ships as HH_4 -- the fix is recorded here because it changes an item
#   code.
#
# THREE tables, 188 respondents:
#   gerou_2023_hexaco_honesty_humility   HH_1-HH_16,   1-5  (16 items)
#   gerou_2023_dass21                    DASS_1-21,    0-3  (21 items)
#   gerou_2023_quiet_ego                 QES_1-QES_14, 1-5  (14 items)
# id: the deposit's own ID serial (1-188), kept so the three tables link.
# Covariates: cov_gender, cov_age, cov_education, cov_marital_status; the .sav
#   value labels are harvested into metadata/covariate_labels/.
# Dropped: the fifteen *R reverse-scored copies and every subscale or total
#   column (Sincerity, Fairness, Greed, Modesty, DASS_DEP/ANX/STR/DEPR,
#   HH_TOTAL, QE_TOTAL, DASS_TOTAL, QES_TOTAL).
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
    REPO_ROOT / "automated_finding" / "runs" / "figshare_batch" / "24588120" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE, FNAME = 24588120, "Humility and Quiet Ego.sav"

MISTYPED = {"ΗH_4": "HH_4"}          # Greek eta -> Latin H
HH = [f"HH_{i}" for i in range(1, 17)]
DASS = [f"DASS_{i}" for i in range(1, 22)]
QES = [f"QES_{i}" for i in range(1, 15)]
COVS = {"Gender": "cov_gender", "Age": "cov_age",
        "Education": "cov_education", "MaritalStatus": "cov_marital_status"}
DROPPED = ([f"HH_{i}R" for i in (1, 2, 6, 7, 9, 11, 12, 14, 15, 16)]
           + [f"QES_{i}R" for i in (2, 6, 10, 11, 14)]
           + ["Sincerity", "Fairness", "Greed", "Modesty", "DASS_DEP",
              "DASS_ANX", "DASS_STR", "DASS_DEPR", "HH_TOTAL", "QE_TOTAL",
              "DASS_TOTAL", "QES_TOTAL"])
DASS_MISSING = 8


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
    df, _meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    for src, dst in MISTYPED.items():
        assert src in df.columns and dst not in df.columns, (src, dst)
    df = df.rename(columns=MISTYPED)

    known = set(HH + DASS + QES + list(COVS) + DROPPED + ["ID"])
    for c in known:
        assert c in df.columns, f"expected source column {c} is absent"
    unaccounted = [c for c in df.columns if c not in known]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"dropped, reverse-scored copies and composites: {len(DROPPED)} columns")

    n_sent = int((df[DASS] == DASS_MISSING).sum().sum())
    print(f"DASS: dropping {n_sent} response(s) coded {DASS_MISSING} on a 0-3 "
          f"scale as user-missing")
    df[DASS] = df[DASS].mask(df[DASS] == DASS_MISSING)

    df = df.rename(columns={"ID": "id", **COVS})
    df["id"] = pd.to_numeric(df["id"]).astype(int)
    assert df["id"].is_unique
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov])
        df[cov] = v.astype("Int64") if (v.dropna() % 1 == 0).all() else v

    tables = {
        "gerou_2023_hexaco_honesty_humility": (HH, set(range(1, 6))),
        "gerou_2023_dass21": (DASS, set(range(0, 4))),
        "gerou_2023_quiet_ego": (QES, set(range(1, 6))),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, (cols, scale) in tables.items():
        t = (df[["id", *cov_cols, *cols]]
             .melt(id_vars=["id", *cov_cols], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{name}: resp outside the documented scale: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert name not in written
        checks = run_qc(t, permitted_values=scale)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:170]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": scale})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
