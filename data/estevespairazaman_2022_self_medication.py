#!/usr/bin/env python3

# Source: https://zenodo.org/records/7011528
# DOI: 10.5281/zenodo.7011528
#   ESTEVES PAIRAZAMAN, A., ÑAÑEZ DEL PINO, D., et al. (2022). Self-medication for
#   anxiety symptoms in the context of COVID-19 [Dataset]. Zenodo.
# Data: "SPSS DATA 1 ENGLISH VERSION.sav" -- 384 Peruvian adults. The deposit also
#       ships the same 384 rows as DATA 1.csv (Spanish column names) and a second
#       file; see below.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: shipped. BOTH label levels checked on the English .sav: 29 of 32
#   variable labels are the authors' own ENGLISH item stems ("Have you experienced
#   increased heart rate (palpitations) during the pandemic?"), and 26 of 32 carry
#   value labels giving all five frequency anchors. The authors supplied the English
#   themselves -- this is a published English version of a Spanish-administered
#   instrument, not an IRW translation -- so nothing is owed on the issues page.
#
# TWO tables, both 1-5 frequency:
#   estevespairazaman_2022_anxiety_symptoms   9 items (P1-P9), COVID-19 anxiety
#                                             symptoms.
#   estevespairazaman_2022_self_medication   13 items (S1-S13), self-medication
#                                             behaviour.
# Not shipped:
#   SUMAV1/SUMAV2/SUMAD1-3  derived sums, and RANGOEDAD, an age band already
#                           carried as cov_age_band.
#   DATA 1.csv              the same 384 rows with Spanish headers and no labels --
#                           the .sav is the richer copy of the same data, so
#                           shipping both would duplicate every respondent.
#   SPSS DATA 2 (ENGLISH)   384 rows x 18, but it is not a Likert battery: D1-D3 are
#                           three frequency items while D1I1-D3I7 are binary
#                           CHECKBOX indicators of reasons and of which drug was
#                           taken (Diazepam, Clonazepam, ...), and V1/V2 are the two
#                           variable totals. The drug list is a nominal pick-one-or-
#                           more, not an ordinal item, so it is left out rather than
#                           forced into resp. Noted in the leads file.
# id: neither file carries a respondent id; the 0-based row index is used.
# Covariates: cov_age, cov_gender, cov_education, cov_marital_status,
#   cov_age_band.
# Rights: neither instrument is in the register. These are the authors' own items,
#   written for this study; checked by reading the stems.
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
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "7011528"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 7011528, "SPSS DATA 1 ENGLISH VERSION.sav"

COVS = {"Age": "cov_age", "Gender": "cov_gender",
        "EducationLevel": "cov_education", "MaritalStatus": "cov_marital_status",
        "RANGOEDAD": "cov_age_band"}
BLOCKS = {
    "estevespairazaman_2022_anxiety_symptoms": [f"P{i}" for i in range(1, 10)],
    "estevespairazaman_2022_self_medication": [f"S{i}" for i in range(1, 14)],
}
DERIVED = ["SUMAV1", "SUMAV2", "SUMAD1", "SUMAD2", "SUMAD3"]
SCALE = set(range(1, 6))


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

    items = {c for cols in BLOCKS.values() for c in cols}
    accounted = {"id"} | set(COVS) | items | set(DERIVED)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    for c in DERIVED:
        print(f"  skipped {c}: derived sum, not an item")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in BLOCKS.items():
        t = (df[["id", *COVS, *cols]]
             .melt(id_vars=["id", *COVS], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"])
             .rename(columns=COVS))
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the value-labelled 1-5 scale: {bad}"
        for c in COVS.values():
            t[c] = t[c].astype("Int64")
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
