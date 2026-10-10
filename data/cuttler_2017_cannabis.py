#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.5045962 (PLOS figshare; S1 File, S2 File)
# DOI: 10.1371/journal.pone.0178194
#   Cuttler, C., & Spradlin, A. (2017). Measuring cannabis consumption: Psychometric
#   properties of the Daily Sessions, Frequency, Age of Onset, and Quantity of Cannabis
#   Use Inventory (DFAQ-CU). PLOS ONE, 12(5), e0178194.
# Data: "S2 File.sav" (figshare file 8541154): 2,062 cannabis users x 282 columns.
#       All completed the DFAQ-CU and the CUDIT-R; a subsample of 645 (Subsample = 1)
#       also completed the MSHQ, TLFB, CAST, CUPIT, MSI and AUDIT. "S1 File.docx"
#       (8541142) is the DFAQ-CU inventory itself (instructions, items, options).
# License: CC BY 4.0 (figshare record; PLOS ONE article).
#
# Item text: shipped for cuttler_2017_dfaqcu_freq only -- SPSS variable labels carry
#   every stem and value labels every option, matching the S1 File inventory, which is
#   the authors' own CC BY material. Not shipped for the other five tables, although
#   both label levels carry the text there too (stems in the variable labels, options
#   in the value labels): CAST, CUDIT-R, CUPIT and MSI are not in
#   itemtext/instrument_rights_register.csv and were not cleared here, and AUDIT is
#   `ship_with_note`.
#
# Tables (id = row index; the file has no respondent id):
#   cuttler_2017_dfaqcu_freq  DFAQ-CU frequency-format items: DFAQCU2 (last use, 1 over
#                             a year ago .. 11 currently high), DFAQCU3 (current
#                             frequency, 0 do not use .. 12 more than once a day),
#                             DFAQCU5 (frequency before that, 0-12), DFAQCU6 (days used
#                             in the past week, 0-7), DFAQCU7 (days in the past month,
#                             a 0-31 count), DFAQCU8 (lifetime uses, 0 never .. 10 more
#                             than 10,000), DFAQCU10 (hours after waking, 0 do not use ..
#                             8 immediately upon waking). All higher = more use.
#   cuttler_2017_cudit_r      CUDIT2-CUDIT9, the eight CUDIT-R items, 0-4 (CUDIT9 is
#                             scored 0/2/4 as the CUDIT-R scores it). N=1,544.
#   cuttler_2017_cast         CAST1-CAST6, 0 never .. 4 very often. Subsample.
#   cuttler_2017_cupit        CUPIT1-CUPIT16, each item on its own published response
#                             scale (1-8, 0-8, 1-6, 0-6, 0-5, 0-4, 1-9, 0-3); the range
#                             differences are the instrument's. CUPIT7 runs 1 "6 months
#                             or longer" .. 9 "no days at all" and CUPIT9 0 never .. 4
#                             always "able to stop": shipped as stored. Subsample.
#   cuttler_2017_msi          MSI1-MSI31, Marijuana Screening Inventory, 0 no / 1 yes.
#                             Subsample.
#   cuttler_2017_audit        AUDIT1-AUDIT10, 0-4 (AUDIT9 and AUDIT10 scored 0/2/4).
#                             Subsample.
# Skipped: DFAQCU1 (constant, everyone has used cannabis), DFAQCU2b (asked only of
#   the 280 currently high), DFAQCU4 (duration of the current frequency), DFAQCU9
#   (weekend/weekday pattern, nominal), DFAQCU11/12/17-27 and aDFAQCU/bDFAQCU (free
#   counts and grams, the quantity sections, branched by form of cannabis),
#   DFAQCU13-16 (method/form, nominal), DFAQCU28-33 (ages, onset, medical use),
#   DFAQCU32 (its stored codes are out of order: 13 = "5-6 times a week" sits after
#   11 = "more than once a day"); every z* column and subscale score (derived);
#   CAST0 and CUDIT1 (screening gates); MSHQ1-21 (mixed formats, history questions);
#   TLFB_D* (30-day calendar cells); Consent (constant); free-text columns.
# Covariates: cov_age, cov_sex (1 male, 2 female, 3 other), cov_ethnicity (1 White,
#   2 Black, 3 Hispanic or Latino, 4 Asian, 5 Native American, 6 Pacific Islander,
#   7 other), cov_ppi_deviant (PPI_Sum, deviant-responding scale 0-3; the authors'
#   screening variable, kept rather than applied).

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
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "plos_0178194"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/8541154"
P = "cuttler_2017_"
TABLES = {
    "dfaqcu_freq": (["DFAQCU2", "DFAQCU3", "DFAQCU5", "DFAQCU6", "DFAQCU7", "DFAQCU8",
                     "DFAQCU10"], None),
    "cudit_r": ([f"CUDIT{i}" for i in range(2, 10)], None),
    "cast": ([f"CAST{i}" for i in range(1, 7)], None),
    "cupit": ([f"CUPIT{i}" for i in range(1, 17)], None),
    "msi": ([f"MSI{i}" for i in range(1, 32)], None),
    "audit": ([f"AUDIT{i}" for i in range(1, 11)], None),
}
COVS = {"Age": "cov_age", "Sex": "cov_sex", "Ethnicity": "cov_ethnicity",
        "PPI_Sum": "cov_ppi_deviant"}


def fetch() -> Path:
    p = RAW_DIR / "S2 File.sav"
    if not p.exists():
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
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


def main() -> None:
    d, meta = pyreadstat.read_sav(str(fetch()))
    vl = meta.variable_value_labels
    assert d.shape == (2062, 282)
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    items = [c for its, _ in TABLES.values() for c in its]
    # books: everything not shipped is skipped by a named rule
    skip_re = re.compile(r"^(z|DFAQCU(1|2b|4|9|1[1-9]|2[0-9]|3[0-3].*|14.*|16.*|ci)$|"
                         r"[ab]DFAQCU$|DFAQCU_|MSHQ|TLFB|CAST0$|CUDIT1$|CAST$|CUDIT$|CUPIT$|"
                         r"MSI$|AUDIT$|Consent|Ethnicity_Other|Subsample)")
    rest = [c for c in d.columns if c not in items and c not in covs and c != "id"
            and not skip_re.match(c)]
    assert not rest, rest
    # stored codes must be the labelled ones (DFAQCU7 is a free count, 0-31)
    for c in items:
        if c in vl:
            assert set(d[c].dropna().unique()) <= set(vl[c]), (c, sorted(d[c].dropna().unique()))
    assert d["DFAQCU7"].dropna().between(0, 31).all()
    out = {}
    for suf, (its, _) in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert (t["resp"] % 1 == 0).all(), suf
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its)
        pv = {c: set(int(k) for k in vl[c]) for c in its if c in vl}
        if suf == "dfaqcu_freq":
            pv["DFAQCU7"] = set(range(32))
        out[P + suf] = (t, pv)
    emit(out)


if __name__ == "__main__":
    main()
