#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.1355389 (PLOS ONE S1 Dataset)
# DOI: 10.1371/journal.pone.0119052
#   Schroeter, C., Ehrenthal, J. C., Giulini, M., Neubauer, E., Gantz, S.,
#   Amelung, D., Balke, D., & Schiltenwolf, M. (2015). "Attachment, Symptom
#   Severity, and Depression in Medically Unexplained Musculoskeletal Pain
#   and Osteoarthritis: A Cross-Sectional Study." PLOS ONE, 10(3), e0119052.
#   (PMC4373893)
# Data: figshare file 6744927, S1 Dataset.SAV (174 rows x 110 columns;
#       German outpatients with medically unexplained musculoskeletal pain or
#       severe osteoarthritis pain).
# License: CC BY 4.0 (figshare API; the article is CC BY).
#
# Item text: not shipped. Both label levels checked: no variable labels on
#   any FFbH-R, HADS, ECR-R item (RQ2-RQ4 carry only "RQ item k <style>");
#   no value labels on any item (value labels only on the covariates). The
#   wording is in the published German FFbH-R, HADS-D and ECR-RD and in
#   Bartholomew's RQ (the paper quotes one prototype). HADS and ECR-R are
#   rights-register blocks.
#
# Tables (item codes are the source column names):
#   schroeter_2015_ffbhr   FFbH_R_1_t1 .. FFbH_R_12_t1  Hannover Functional
#       Ability Questionnaire for back pain (FFbH-R), 12 items, "each with
#       three possible answers: Yes, Yes with difficulty, and No" (paper
#       Methods). Stored as the raw answer code 1-3; the deposit's
#       FFbH_R_k_t1r scoring column equals 3 - raw in every complete row
#       (asserted), so 1 = Yes (full function) .. 3 = No. Permitted {1,2,3}.
#   schroeter_2015_hads    HADS_1_t1 .. HADS_14_t1  Hospital Anxiety and
#       Depression Scale, German version, all 14 items; "responses on a
#       4-point scale" (paper Methods), 0-3. Permitted {0,1,2,3}. The paper
#       analyses only the depression subscale; the deposit has all 14.
#   schroeter_2015_ecrr    ecrrd01 .. ecrrd36  Experiences in Close
#       Relationships-Revised, German version (ECR-RD), 36 items. The paper
#       does not print the response format; the ECR-R is a 7-point scale
#       (Fraley, Waller & Brennan 2000; German ECR-RD, Ehrenthal et al. 2009),
#       so permitted {1..7}. One cell (ecrrd32 = 77) is a keying error
#       outside that set and is set to NA.
#   schroeter_2015_rq      RQ1_t1 .. RQ4_t1  Relationship Questionnaire
#       (RQ-2), agreement with each of the four attachment prototypes
#       (1 secure, 2 dismissing, 3 preoccupied, 4 fearful). The paper says
#       "a 7-point Likert-type scale ranging from 1 (completely true) to 7
#       (completely false)"; the deposit stores 0-6. Which end of the stored
#       0-6 is "completely true" is undocumented, so NO permitted-value set
#       is asserted and resp is the stored code.
#
# Sentinels: 99 is the deposit's missing code (FFbH-R raw, HADS, Employment);
#   set to NA.
# Dropped:
#   - FFbH_R_1_t1r .. FFbH_R_12_t1r: the 0-2 scored copies of the raw items
#     (asserted = 3 - raw); where raw is 99 they hold a fractional
#     mean-imputed value, which is not shipped.
#   - Composites: RQ_t1_modelself, RQ_t1_modelothers, RQ_4Bindungsstile,
#     RQ_Bindungsstil_dichotom, Anzahl_Diagnosen, Anzahl_Schmerzpunkte,
#     Schmerz_Ausbreitung.
#   - HADS_suz_t1: an undocumented 1/2/99 code, not one of the 14 items.
#   - Diagnosis fields (Psychiatr_Hauptdiagnose, a SCID main-diagnosis
#     category, and the three disorder-group flags): categorical, not free
#     text; not carried.
#   - Raw/duplicate demographics superseded by the English-labelled
#     covariates: Erwerbstaetigkeit_kat, Erwerbslos_kat, Erwerbstätigkeit,
#     Erwerbstätigkeit_jn, EM_Rente_jn, Rentenverfahren, Schulabschluss,
#     Schulbildung_kat, Ausbildungsabschluss, Ausbildung_kat,
#     Einverständniserklärung (consent flag, constant 1).
# id: row index. "Code" (K001..) is a study code, not shipped.
# Covariates: cov_pain_condition (1 osteoarthritis, 2 medically unexplained
#   musculoskeletal pain), cov_sex (1 female, 2 male), cov_age (years),
#   cov_partnership (0 no, 1 yes), cov_education (1 lower/middle secondary,
#   2 college entrance), cov_employment (1 full-time .. 5 sick leave; 99 ->
#   NA), cov_pain_vas_week (average pain last 7 days, VAS 0-100),
#   cov_pain_vas_now (pain while filling in, VAS 0-100).

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
URL = "https://ndownloader.figshare.com/files/6744927"

FFBH = [f"FFbH_R_{i}_t1" for i in range(1, 13)]
FFBH_R = [f"{c}r" for c in FFBH]
HADS = [f"HADS_{i}_t1" for i in range(1, 15)]
ECRR = [f"ecrrd{i:02d}" for i in range(1, 37)]
RQ = [f"RQ{i}_t1" for i in range(1, 5)]
TABLES = {
    "schroeter_2015_ffbhr": FFBH,
    "schroeter_2015_hads": HADS,
    "schroeter_2015_ecrr": ECRR,
    "schroeter_2015_rq": RQ,
}
DOCUMENTED = {
    "schroeter_2015_ffbhr": set(range(1, 4)),
    "schroeter_2015_hads": set(range(0, 4)),
    "schroeter_2015_ecrr": set(range(1, 8)),
}
SENTINEL = 99
COMPOSITES = {"RQ_t1_modelself", "RQ_t1_modelothers", "RQ_4Bindungsstile",
              "RQ_Bindungsstil_dichotom", "Anzahl_Diagnosen",
              "Anzahl_Schmerzpunkte", "Schmerz_Ausbreitung"}
OTHER_DROPPED = {"HADS_suz_t1", "Psychiatr_Hauptdiagnose",
                 "Affektive_Störungen", "Angst_Zwangs_Störungen",
                 "Essstörungen", "Erwerbstaetigkeit_kat", "Erwerbslos_kat",
                 "Erwerbstätigkeit", "Erwerbstätigkeit_jn", "EM_Rente_jn",
                 "Rentenverfahren", "Schulabschluss", "Schulbildung_kat",
                 "Ausbildungsabschluss", "Ausbildung_kat",
                 "Einverständniserklärung", "Code"}
COVS = {"pain_condition": "cov_pain_condition", "Sex": "cov_sex",
        "Age": "cov_age", "Partnerschaft_kat": "cov_partnership",
        "Education": "cov_education", "Employment": "cov_employment",
        "Schmerz_1_t1": "cov_pain_vas_week",
        "Schmerz_2_t1": "cov_pain_vas_now"}


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
    assert d.shape == (174, 110), d.shape

    # Balance the books.
    items = {c for its in TABLES.values() for c in its}
    known = items | set(FFBH_R) | COMPOSITES | OTHER_DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert d["Code"].is_unique
    assert not d.drop(columns="Code").duplicated().any()

    # FFbH-R scored copies = 3 - raw wherever raw is a real answer.
    for raw, sc in zip(FFBH, FFBH_R):
        ok = d[raw].isin([1, 2, 3])
        assert (d.loc[ok, sc] == 3 - d.loc[ok, raw]).all(), sc
    # Diagnosis column is a category list, not free text.
    assert d["Psychiatr_Hauptdiagnose"].nunique() <= 12

    # Sentinels and the single ECR-R keying error.
    for c in FFBH + HADS + ["Employment"]:
        d[c] = d[c].replace(SENTINEL, np.nan)
    bad_ecr = (d[ECRR] == 77)
    assert bad_ecr.values.sum() == 1 and bad_ecr["ecrrd32"].sum() == 1
    d[ECRR] = d[ECRR].mask(bad_ecr)

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, its in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        pv = None
        if table in DOCUMENTED:
            allowed = DOCUMENTED[table]
            for it, g in long.groupby("item"):
                bad = set(g["resp"]) - allowed
                assert not bad, (table, it, bad)
            pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
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
