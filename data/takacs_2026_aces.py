#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/32104447
# DOI: 10.6084/m9.figshare.32104447.v1 (dataset; no paper DOI on the record)
#   Takacs, Henrietta & Marschalko, Eszter Eniko (2026). "The Role of Adverse Childhood
#   Experiences in Adult Anxiety and Depression: The Roles of Resilience and Mindful
#   Awareness" [data set]. figshare.
# Data: Dataset.xlsx: 244 Hungarian-speaking adults from Romania and Hungary x row
#       number, six coded demographics, and ACE1-10, PHQ1-9, GAD1-7, CD1-10, MAAS1-15
#       with a total per instrument. Codebook.docx: per variable the English item
#       wording, SPSS name and coding (e.g. ACE "Yes = 1, No = 2"; PHQ/GAD "0 = Not at
#       all ... 3 = Nearly every day"; CD "0 = Not true at all ... 4 = True nearly all
#       the time"; MAAS "1 = Almost always ... 6 = Almost never").
# License: CC BY 4.0 (figshare record).
#
# Item text: shipped for aces, phq9, gad7, maas (codebook wording; built by
#   automated_finding/itemtext_verification/make_itemtext_takacs_2026.py). The codebook
#   gives the English wording only; the administration was Hungarian and the Hungarian
#   wording is not in the deposit, so these ship as the documented fallback
#   (English base fields, language = Hungarian, no _translated). Not shipped for
#   cdrisc10: CD-RISC is blocked in itemtext/instrument_rights_register.csv.
#
# Tables (codes as stored; one header has a stray leading space, " PHQ5", stripped):
#   takacs_2026_aces      ACE1-10  1 = Yes, 2 = No (ACE questionnaire; kept as coded)
#   takacs_2026_phq9      PHQ1-9   0-3
#   takacs_2026_gad7      GAD1-7   0-3
#   takacs_2026_cdrisc10  CD1-10   0-4 (CD-RISC-10)
#   takacs_2026_maas      MAAS1-15 1-6 (higher = more mindful)
# Not shipped: totalACE, totalPHQ, totalGAD, totalCD, totalMAAS (sums); the unnamed first
#   column (row number, used as id).
# Covariates (codebook): cov_gender (1 male, 2 female), cov_age, cov_residence
#   (1 Romania, 2 Hungary), cov_education (1 primary ... 6), cov_status (1 student,
#   2 student and employed, 3 employed, 4 unemployed, 5 retired), cov_marital
#   (1 single, 2 married, 3 cohabiting, 4 divorced, 5 widowed).

import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "takacs_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILES = {"Dataset.xlsx": "https://ndownloader.figshare.com/files/64031020",
         "Codebook.docx": "https://ndownloader.figshare.com/files/64031017"}
TABLES = {"ACE": ("takacs_2026_aces", 10, range(1, 3)),
          "PHQ": ("takacs_2026_phq9", 9, range(0, 4)),
          "GAD": ("takacs_2026_gad7", 7, range(0, 4)),
          "CD": ("takacs_2026_cdrisc10", 10, range(0, 5)),
          "MAAS": ("takacs_2026_maas", 15, range(1, 7))}
COVS = {"Gender": "cov_gender", "Age": "cov_age", "Residence": "cov_residence",
        "Education": "cov_education", "Current_status": "cov_status",
        "Marital_status": "cov_marital"}


def fetch() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for f, u in FILES.items():
        p = RAW_DIR / f
        if not p.exists():
            r = requests.get(u, headers=UA, timeout=300)
            r.raise_for_status()
            p.write_bytes(r.content)
    return RAW_DIR / "Dataset.xlsx"


def main() -> None:
    d = pd.read_excel(fetch())
    d.columns = [c.strip() for c in d.columns]
    assert d.shape == (244, 63) and d["Unnamed: 0"].is_unique
    items = {p: [f"{p}{i}" for i in range(1, n + 1)] for p, (_, n, _) in TABLES.items()}
    allit = {c for v in items.values() for c in v}
    skipped = [c for c in d.columns if c not in allit | set(COVS) | {"Unnamed: 0"}]
    assert all(c.startswith("total") for c in skipped), skipped
    print(f"  [skip] totals: {skipped}")
    d = d.rename(columns={"Unnamed: 0": "id", **COVS})
    covs = list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for pre, (name, n, rng) in TABLES.items():
        its = items[pre]
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item", value_name="resp")
        assert t["resp"].notna().all() and t["resp"].isin(list(rng)).all(), name
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any()
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:160]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
