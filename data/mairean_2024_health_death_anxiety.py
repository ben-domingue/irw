#!/usr/bin/env python3
# Source: https://zenodo.org/records/13926078
# DOI: 10.1177/13591053251341191
#   Macovei, M., & Mairean, C. (2025). "Health anxiety and death anxiety: The
#   role of cyberchondria and social aspirations." Journal of Health
#   Psychology, 31(4), 1575-1589. (Not linked from the deposit; found by Crossref title
#   search. Paywalled (SAGE, closed per Unpaywall) -- only the abstract was
#   read: 405 participants, 67% women, aged 18-38, which this file matches.)
#   Deposit: Mairean, C., & Macovei, M. (2024). Health anxiety and death
#   anxiety. The role of cyberchondria and social aspirations. Zenodo.
#   https://doi.org/10.5281/zenodo.13926078
# Data: database.sav (405 rows x 143 columns; Romanian young adults).
#   Not the sample of data/mairean_2023_childhood_trauma.py (Zenodo 7668169,
#   N=261, ages 17-63; different instruments).
# License: CC BY 4.0 (Zenodo API).
#
# Item text: not shipped. Both label levels checked: variable labels are
#   absent or just repeat the column name ("PANAS1", "DAS8"); no value labels
#   on any item (value labels only on the covariates and the two HSCMS1
#   aspiration questions). The wording is in the published Romanian
#   adaptations of the instruments.
#
# Instrument identities rest on the block names and their item counts, and
# on the deposit's own totals (each asserted to equal the raw item sum):
#   mairean_2024_css12   CSS1-CSS12  Cyberchondria Severity Scale, 12-item
#       short form (CSS_scor_total). The CSS-12 is a 5-point frequency scale
#       (McElroy et al. 2019), stored 1-5. Permitted {1..5}.
#   mairean_2024_shai    SHAI1-SHAI18  Short Health Anxiety Inventory
#       (SHAI_scor_total). Each SHAI item has four response statements
#       (Salkovskis et al. 2002); the deposit codes them 1-4 (its total runs
#       18-62, i.e. 18 x 1 at the floor). Permitted {1..4}.
#   mairean_2024_panas   PANAS1-PANAS20 (wave 1) and PANAS1_A-PANAS20_A
#       (wave 2)  Positive and Negative Affect Schedule, 5-point (Watson,
#       Clark & Tellegen 1988), stored 1-5. Permitted {1..5}.
#   mairean_2024_das     DAS1-DAS15 (wave 1) and DAS1_A-DAS15_A (wave 2)
#       Death Anxiety Scale (Templer 1970), 15 true/false items, stored 1/2.
#       Permitted {1,2}. Which code is "true" is not labelled. (irw-validate's
#       rights_register flags these codes against the Dyadic Adjustment
#       Scale's "DAS" row: a name collision, not that instrument.)
#     PANAS and DAS were each recorded twice: the deposit carries both blocks
#     with separate totals (PANAS_scor_total1/2, DAS_scor_total1/2), the two
#     agree on 61% / 90% of cells and correlate .52-.94 per item, so they are
#     two administrations to the same people, not copies. What separates
#     them (e.g. before/after a task) is not documented in anything readable
#     here; `wave` is 1 for the unsuffixed block and 2 for the _A block.
#   mairean_2024_hscm   HSCMS21-HSCMS23  motivation for high social class
#       (the "social aspirations" of the title; HSCM = HSCMS2_scor_total =
#       their sum, asserted). Stored 1-7; the response format is NOT
#       documented in anything readable here, so no permitted-value set is
#       asserted.
#
# Dropped:
#   - Totals, subscales and derived terms: CSS_excesivitate, CSS_suferinta,
#     CSS_reasigurare, CSS_constrangere, CSS_scor_total, SHAI_scor_total,
#     PA1, NA1, PANAS_scor_total1, PA2, NA2, PANAS_scor_total2,
#     HSCMS2_scor_total, HSCM (an identical copy of HSCMS2_scor_total,
#     asserted), DAS_scor_total1, DAS_scor_total2, Ilness_likelihood,
#     Ilness_severity, body_vigilance, and all Z-scores and interaction terms
#     (ZSHAI_scor_total .. cyberXHSCM).
#   - Ocupatia: free-text job title (no names or narrative; checked), not
#     carried.
# id: row index (no respondent id in the file).
# Covariates: cov_gender (1 female, 2 male), cov_age (years),
#   cov_residence (1 rural, 2 urban), cov_education (1 high school ..
#   4 doctorate), cov_marital (1 married, 2 divorced, 3 in a relationship,
#   4 single), cov_income (1 < 2000 lei .. 5 > 8000 lei, 6 prefer not to
#   say), cov_bereavement (experienced a death: 1 yes, 2 no),
#   cov_aspired_income (HSCMS1-1: 1 < 2000 lei .. 6 > 10000 lei),
#   cov_aspired_education (HSCMS1-2: 1 high school .. 3 postgraduate).

import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/13926078/files/database.sav/content"

CSS = [f"CSS{i}" for i in range(1, 13)]
SHAI = [f"SHAI{i}" for i in range(1, 19)]
PANAS = [f"PANAS{i}" for i in range(1, 21)]
PANAS_A = [f"{c}_A" for c in PANAS]
DAS = [f"DAS{i}" for i in range(1, 16)]
DAS_A = [f"{c}_A" for c in DAS]
HSCM = ["HSCMS21", "HSCMS22", "HSCMS23"]
# table -> (wave-1 columns, wave-2 columns or None, permitted set or None)
TABLES = {
    "mairean_2024_css12": (CSS, None, set(range(1, 6))),
    "mairean_2024_shai": (SHAI, None, set(range(1, 5))),
    "mairean_2024_panas": (PANAS, PANAS_A, set(range(1, 6))),
    "mairean_2024_das": (DAS, DAS_A, {1, 2}),
    "mairean_2024_hscm": (HSCM, None, None),
}
TOTALS = [(CSS, "CSS_scor_total"), (SHAI, "SHAI_scor_total"),
          (PANAS, "PANAS_scor_total1"), (PANAS_A, "PANAS_scor_total2"),
          (DAS, "DAS_scor_total1"), (DAS_A, "DAS_scor_total2"),
          (HSCM, "HSCMS2_scor_total")]
COMPOSITES = {"CSS_excesivitate", "CSS_suferinta", "CSS_reasigurare",
              "CSS_constrangere", "CSS_scor_total", "SHAI_scor_total", "PA1",
              "NA1", "PANAS_scor_total1", "PA2", "NA2", "PANAS_scor_total2",
              "HSCMS2_scor_total", "HSCM", "DAS_scor_total1",
              "DAS_scor_total2", "Ilness_likelihood", "Ilness_severity",
              "body_vigilance", "ZSHAI_scor_total", "ZCSS_scor_total",
              "ZIlness_likelihoos", "ZIlness_severity", "Zbody_vigilance",
              "ZHSCM", "anxXHSCM", "illnesslikXHSCM", "illnesssevXHSCM",
              "bodyXHSCM", "cyberXHSCM"}
OTHER_DROPPED = {"Ocupatia"}
COVS = {"Gen": "cov_gender", "Varsta": "cov_age",
        "Mediu_provenienta": "cov_residence", "Nivel_studii": "cov_education",
        "Statut_marital": "cov_marital", "Venit_castigat": "cov_income",
        "Trecere_prin_deces": "cov_bereavement",
        "HSCMS11": "cov_aspired_income", "HSCMS12": "cov_aspired_education"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (405, 143), d.shape

    # Balance the books.
    items = set(CSS + SHAI + PANAS + PANAS_A + DAS + DAS_A + HSCM)
    known = items | COMPOSITES | OTHER_DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert not d.duplicated().any()

    for cols, total in TOTALS:
        assert np.allclose(d[cols].sum(axis=1), d[total]), total
    assert (d["HSCM"] == d["HSCMS2_scor_total"]).all()
    # The two PANAS / DAS blocks are distinct administrations, not copies.
    assert not (d[PANAS].values == d[PANAS_A].values).all(axis=1).mean() > .5
    assert not (d[DAS].values == d[DAS_A].values).all()
    # Ocupatia is a short job title, not narrative.
    assert d["Ocupatia"].astype(str).str.len().max() <= 20

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (w1, w2, allowed) in TABLES.items():
        parts = []
        for wave, cols in ((1, w1), (2, w2)):
            if cols is None:
                continue
            ren = {c: w1[k] for k, c in enumerate(cols)}
            part = d[["id"] + cov_cols + cols].rename(columns=ren).melt(
                id_vars=["id"] + cov_cols, value_vars=w1, var_name="item",
                value_name="resp")
            if w2 is not None:
                part["wave"] = wave
            parts.append(part)
        long = pd.concat(parts, ignore_index=True)
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        pv = None
        if allowed is not None:
            for it, g in long.groupby("item"):
                bad = set(g["resp"]) - allowed
                assert not bad, (table, it, bad)
            pv = {i: allowed for i in w1}
        keys = ["id", "item"] + (["wave"] if w2 is not None else [])
        long = long[["id", "item", "resp"]
                    + (["wave"] if w2 is not None else []) + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(keys).reset_index(drop=True)
        assert not long.duplicated(keys).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(w1) > 1
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
