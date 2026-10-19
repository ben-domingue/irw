#!/usr/bin/env python3

# Source: https://zenodo.org/records/13905610
# DOI: 10.5281/zenodo.13905610
#   Nistoreanu-Neculau, B., Mairean, C., Gavrilovici, O. (2024). The relation between
#   deviation from the balanced time perspective and ... [Dataset]. Zenodo.
# Data: "Database.sav" -- 368 Romanian adults.
# License: CC BY 4.0 (verified on the Zenodo record).
#
# ONE DATASET, TWO DOIs. 10.5281/zenodo.13905612 (Mairean & Nistoreanu-Neculau,
#   "The relation between childhood experiences and manifestations of ...") deposits
#   a Database.sav that is BYTE-IDENTICAL to this one -- md5 6caeefb64b03b16cb4a827ec80e12e4d
#   for both. Two papers from one data collection. The tables ship once, from this
#   record; 13905612 is statused as the duplicate in the leads file.
#
# Item text: NOT shipped. Both label levels checked: 0 of 145 variables carry a
#   variable label, 15 carry value labels and all fifteen are demographics. Neither
#   stems nor anchors for any item are in the file.
# Naming: mairean_2024_* and mairean_2024b_* are taken, so this takes mairean_2024c_*.
#
# THREE tables ship; TWO instruments are WITHHELD on rights:
#   mairean_2024c_des     28 items, 0-10. Dissociative Experiences Scale.
#   mairean_2024c_ices    28 items, 1-5. The Invalidating Childhood Environment Scale
#                         asked about EACH PARENT: ICES1_M..ICES14_M (mother) and
#                         ICES1_T..ICES14_T (tata, father). The _M/_T suffix is a
#                         TARGET, not a wave -- the two halves were administered in
#                         the same sitting -- so they ship as 28 distinct item codes
#                         in the source's own spelling rather than being melted into
#                         a wave column.
#   mairean_2024c_bce     10 items, 1-2. Benevolent Childhood Experiences.
# WITHHELD, neither currently in the rights register and BOTH flagged for a row:
#   CTQ1-28      Childhood Trauma Questionnaire (Bernstein & Fink), published by
#                Pearson. Another #3077 fork flagged the CTQ as wanting a register
#                row on the same day; withheld here on that basis rather than
#                shipped because the register happens to be silent.
#   PAI_BOR1-24  Personality Assessment Inventory, Borderline Features scale
#                (Morey), published by PAR. The register blocks other PAR
#                instruments (NEO-FFI) but has no PAI row; withheld on the same
#                conservative basis and flagged.
#   Both are listed in the batch's TODO as register-row requests.
# Not shipped besides those: the 16 SCOR_* derived subscale and total scores, and
#   the four ICES_* named subscale scores.
# id: the file carries no respondent id; the 0-based row index is used.
# Covariates: cov_age, cov_gender, cov_locality, cov_education,
#   cov_relationship_status, cov_diagnosis.
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
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "13905610"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 13905610, "Database.sav"

COVS = {"Varsta": "cov_age", "Genul": "cov_gender", "Provenienta": "cov_locality",
        "Studii": "cov_education", "Statut_relational": "cov_relationship_status",
        "Diagnostic": "cov_diagnosis"}
BLOCKS = {
    "mairean_2024c_des": [f"DES{i}" for i in range(1, 29)],
    "mairean_2024c_ices": ([f"ICES{i}_M" for i in range(1, 15)]
                           + [f"ICES{i}_T" for i in range(1, 15)]),
    "mairean_2024c_bce": [f"BCE{i}" for i in range(1, 11)],
}
WITHHELD = ([f"CTQ{i}" for i in range(1, 29)]
            + [f"PAI_BOR{i}" for i in range(1, 25)])
DROP_EXTRA = ["Nume_diagnostic"]   # free-text diagnosis name, not an item


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
    for c in items | set(WITHHELD):
        assert c in df.columns, f"expected column {c} is absent"
    print(f"  withheld {len(WITHHELD)} columns on rights (CTQ 28, PAI-BOR 24)")
    accounted = {"id"} | set(COVS) | items | set(WITHHELD)
    for c in df.columns:
        if c not in accounted:
            why = ("free-text diagnosis name" if c in DROP_EXTRA
                   else "derived subscale or total score")
            print(f"  skipped {c}: {why}, not an item")

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
