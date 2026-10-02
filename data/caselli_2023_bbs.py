#!/usr/bin/env python3
# Source: https://zenodo.org/records/8029702
# DOI: 10.3389/fneur.2023.1171163
#   Caselli, S., Sabattini, L., Cattaneo, D., Jonsdottir, J., Brichetto, G.,
#   Pozzi, S., Lugaresi, A. & La Porta, F. (2023). "When 'good' is not good
#   enough: a retrospective Rasch analysis study of the Berg Balance Scale for
#   persons with Multiple Sclerosis." Frontiers in Neurology 14:1171163.
#   (PMC10318536)
# Data: Zenodo 8029702, "Dataset BBS_MS_upload.xlsx", sheet "Unico" (1,220
#       assessments x 45 columns; 814 persons with MS, 1-3 assessments each,
#       three Italian rehabilitation centres). Sheet "Codebook_unico" is the
#       deposit's codebook.
# License: CC BY 4.0 (Zenodo record metadata; the paper's Data Availability
#   statement says the same).
#
# Item text: not shipped. The xlsx has no label levels at all (no variable
#   or value labels; the codebook sheet describes only the covariates, its
#   BBS01-14/ABC01-16 rows are blank). Wording is in the published
#   instruments: Berg Balance Scale (Berg et al. 1989/1992) and the
#   Activities-specific Balance Confidence scale (Powell & Myers 1995).
#
# Tables (item codes are the source column names):
#   caselli_2023_bbs  BBS01-BBS14  Berg Balance Scale, rated by
#                     physiotherapists. Paper: each item scored 0 (cannot
#                     perform the task) to 4 (best performance); asserted.
#                     1,220 assessments of 814 persons.
#   caselli_2023_abc  ABC01-ABC16  Activities-specific Balance Confidence
#                     scale (self-report), collected at two of the three
#                     centres only (300 assessments of 264 persons). The paper
#                     does not print the item response format; the file holds
#                     0-100 in steps of 10, which is the published ABC
#                     convention, but with no document in hand no permitted
#                     set is asserted.
#   "BBS totale" equals the BBS item sum and "ABC totale" the ABC item mean
#   (both asserted) and are dropped.
#
# wave: EvalN (0 = only assessment, 1-3 = 1st-3rd of a series), mapped to
#   1-3, so a single assessment is wave 1. The paper analyses these repeated
#   observations under random one-per-person subsampling; that allocation is
#   Rand_1/Rand_2 (A/B/C, A1/A2/B1/B2/C), which is dropped.
# id: row index over persons, replacing the clinic patient code (ID, e.g.
#   "M626"). Two different people share the code B231 (both single
#   assessments, ages 35 and 43, different MS types), so a single-assessment
#   row is its own person: this gives the paper's 814. Recorded gender is not
#   constant within two multi-assessment persons (M590, M252) and is kept as
#   recorded per assessment.
# Dropped: N (row number), Sample (number of assessments per person, implied
#   by wave), Rand_1, Rand_2, the two totals.
# Covariates (per assessment): cov_center (Milano / AISM / Bologna),
#   cov_gender (f/m), cov_age (whole years, floored; the file stores
#   fractional years), cov_ms_type (RR, PP, SP; RP = relapsing progressive),
#   cov_years_since_onset (1 decimal), cov_edss (0-10 by 0.5), cov_falls
#   (falls in the 2 months before the assessment; two centres only).

import io
import math
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/8029702/files/"
       "Dataset%20BBS_MS_upload.xlsx/content")

BBS = [f"BBS{i:02d}" for i in range(1, 15)]
ABC = [f"ABC{i:02d}" for i in range(1, 17)]
TABLES = {"caselli_2023_bbs": (BBS, range(0, 5)),
          "caselli_2023_abc": (ABC, None)}
DROPPED = {"N", "ID", "EvalN", "Sample", "Rand_1", "Rand_2", "BBS totale",
           "ABC totale"}
COVS = {"DB": "cov_center", "Gender": "cov_gender", "Age": "cov_age",
        "Ms_type": "cov_ms_type", "Years_after_onset": "cov_years_since_onset",
        "EDSS": "cov_edss", "Falls": "cov_falls"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name="Unico")


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = load()
    assert d.shape == (1220, 45), d.shape

    # Balance the books.
    known = set(BBS) | set(ABC) | DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known

    full = d[BBS].notna().all(axis=1)
    assert (d.loc[full, BBS].sum(axis=1) == d.loc[full, "BBS totale"]).all()
    abc = d[ABC].notna().all(axis=1)
    assert ((d.loc[abc, ABC].mean(axis=1) - d.loc[abc, "ABC totale"]).abs()
            < 1e-6).all()

    # Persons: the patient code, except single-assessment rows, which are
    # each their own person (B231 is two different people).
    key = d["ID"].where(d["EvalN"] > 0, d["ID"] + "_" + d["N"].astype(str))
    assert key.nunique() == 814
    codes = {k: i + 1 for i, k in enumerate(pd.unique(key))}
    d.insert(0, "id", key.map(codes))
    d["wave"] = d["EvalN"].clip(lower=1).astype(int)
    assert not d.duplicated(["id", "wave"]).any()

    d["Age"] = d["Age"].map(lambda a: math.floor(a) if pd.notna(a) else a)
    d["Years_after_onset"] = d["Years_after_onset"].round(1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, allowed) in TABLES.items():
        long = d.melt(id_vars=["id", "wave"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        pv = None
        if allowed is not None:
            for it, g in long.groupby("item"):
                bad = set(g["resp"]) - set(allowed)
                assert not bad, (table, it, bad)
            pv = {i: set(allowed) for i in its}
        long = long[["id", "item", "resp", "wave"] + cov_cols]
        for c in ("cov_age", "cov_falls"):
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "wave", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long, permitted_values=pv) if pv else run_qc(long)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        ctx = {"permitted_values": pv} if pv else None
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context=ctx)
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
