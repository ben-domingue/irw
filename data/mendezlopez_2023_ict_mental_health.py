#!/usr/bin/env python3
# Source: https://zenodo.org/records/10645380
# DOI: 10.2147/PRBM.S412013
#   Mendez-Lopez, F., Olivan-Blazquez, B., Dominguez-Garcia, M., Lopez-del-
#   Hoyo, Y., Tamayo-Morales, O., & Magallon-Botaya, R. (2023). Depressive and
#   Anxious Symptoms Increase with Problematic Technologies Use Among Adults:
#   The Effects of Personal Factors Related to Health Behavior. Psychology
#   Research and Behavior Management, 16, 2499-2515. (PMC10329434; the
#   deposit description cites it.)
# Data: Zenodo 10645380, Dataset.sav (391 rows x 151 columns; Dataset.csv in
#       the same deposit is a flat export of the same table and is not used).
# License: CC BY 4.0 (Zenodo API).
#
# Sample (paper): 391 adults aged 35-74 attending primary health care centres
# in Aragon, Spain, July 2021 - July 2022.
#
# Item text: not shipped. Both label levels checked: every item carries its
#   full Spanish stem as the variable label (BFI stems are "... que es
#   reservada." continuations of a shared prompt) and value labels on every
#   block except SOC-13. Not built because the deposit and paper carry no
#   English, so the itemtext standard's `_translated` fields would need a
#   machine translation (an issues-page item), which fails the cheapness
#   test. PHQ-9, GAD-7 and RSES are rights-register `ship` and are the easy
#   ones for a later pass; CD-RISC is a `block`; GSES-12, SOC-13, BFI-10 and
#   MULTICAGE-ICT are not in the register.
#
# Tables (item codes are the source column names). Instruments and score
# ranges from the paper's Measures section; per-item ranges from the value
# labels where present.
#   mendezlopez_2023_phq9      PHQ_1-PHQ_9   PHQ-9 (Spanish), 0-3 (labels
#       Nunca .. Casi todos los dias; paper severity bands up to 27).
#   mendezlopez_2023_gad7      GAD_1-GAD_7   GAD-7 (Spanish), 0-3 (labels;
#       paper "graded on a scale ranging from 0 to 3").
#   mendezlopez_2023_multicage_ict  TIC_1-TIC_20  MULTICAGE-ICT (Internet,
#       mobile phone, video games, instant messaging, social networks; 4
#       items each), 0 = No, 1 = Si (labels).
#   mendezlopez_2023_gses12    GSES_1-GSES_12  General Self-Efficacy Scale-12
#       (Spanish), 1-5 (labels; paper total range 12-60). Each item's value
#       labels run in its scored direction (negatively worded items have
#       1 = "Siempre me ocurre"), so the stored codes are already scored.
#   mendezlopez_2023_cdrisc10  CDRISC_1-CDRISC_10  CD-RISC-10 (Spanish), 0-4
#       (labels; paper total 0-40).
#   mendezlopez_2023_bfi10     BFI_1-BFI_11  BFI-10 (Spanish) plus its
#       optional 11th agreeableness item, 1-5 (labels, 1 = Absolutamente de
#       acuerdo .. 5 = Absolutamente en desacuerdo; stored in that direction).
#       BFI_agreeableness sums three items, confirming BFI_11 was scored.
#   mendezlopez_2023_soc13     SOC_1-SOC_13  Sense of Coherence-13
#       (Spanish), 1-7. No value labels; the paper's total range 13-91 gives
#       the 1-7 per-item range. Stored unreversed.
#   mendezlopez_2023_rses      EAR_1-EAR_10  Rosenberg Self-Esteem Scale
#       (Escala de Autoestima de Rosenberg, Spanish), 1-4 (labels; items
#       6-10 have reversed labels, so codes are already scored).
#
# Dropped:
#   - *_inv reverse copies: BFI_1/3/4/5/7_inv (= 6 - x) and SOC_1/2/3/7/10_inv
#     (= 8 - x); asserted.
#   - Totals, factor scores, categories and interaction terms: *_total,
#     *_cat, BFI trait scores, TIC_internet .. TIC_redes, TIC_abuso, TICx*.
#     GSES, CD-RISC, GAD, PHQ, TIC and SOC totals equal the item sums
#     (asserted); EAR_total does too wherever it is not missing.
#   - PHQ_test_dificil: the PHQ's functional-difficulty question, not one of
#     the nine scored items (and asked only of those endorsing a problem).
#   - sexo_nacer: identical to genero_actual in every row (asserted).
# id: row index. The source `id` is a REDCap record code ("161-001"), a study
#   code, replaced with the row index.
# Covariates: cov_rural_urban (0 rural, 1 urban), cov_gender (0 man, 1 woman),
#   cov_age (years), cov_partner (0 without, 1 with), cov_education (0 none or
#   primary, 1 secondary or tertiary), cov_working (0 not working, 1 working).

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/10645380/files/Dataset.sav/content"


def block(prefix, n):
    return [f"{prefix}_{i}" for i in range(1, n + 1)]


TABLES = {
    "mendezlopez_2023_phq9": (block("PHQ", 9), range(0, 4)),
    "mendezlopez_2023_gad7": (block("GAD", 7), range(0, 4)),
    "mendezlopez_2023_multicage_ict": (block("TIC", 20), range(0, 2)),
    "mendezlopez_2023_gses12": (block("GSES", 12), range(1, 6)),
    "mendezlopez_2023_cdrisc10": (block("CDRISC", 10), range(0, 5)),
    "mendezlopez_2023_bfi10": (block("BFI", 11), range(1, 6)),
    "mendezlopez_2023_soc13": (block("SOC", 13), range(1, 8)),
    "mendezlopez_2023_rses": (block("EAR", 10), range(1, 5)),
}
# Tables whose permitted set comes from value labels (all but SOC-13).
LABELLED = set(TABLES) - {"mendezlopez_2023_soc13"}
REVERSED = {**{f"BFI_{i}_inv": (f"BFI_{i}", 6) for i in (1, 3, 4, 5, 7)},
            **{f"SOC_{i}_inv": (f"SOC_{i}", 8) for i in (1, 2, 3, 7, 10)}}
TOTALS = {"GSES_total": "GSES", "CDRISC_total": "CDRISC",
          "GAD_total": "GAD", "PHQ_total": "PHQ", "TIC_total": "TIC"}
COMPOSITES = {
    "GSES_total", "CDRISC_total", "BFI_extraversion", "BFI_agreeableness",
    "BFI_conscientiousness", "BFI_neuroticism", "BFI_openness", "GAD_total",
    "GAD_total_cat", "PHQ_total", "PHQ_total_cat", "SOC_total", "EAR_total",
    "TIC_total", "TIC_internet", "TIC_movil", "TIC_juegos", "TIC_whatsp",
    "TIC_redes", "TIC_internet_cat", "TIC_movil_cat", "TIC_juegos_cat",
    "TIC_whatsp_cat", "TIC_redes_cat", "TIC_abuso", "TICxmunicip",
    "TICxgender", "TICxage", "TICxestadocivil", "TICxestudios",
    "TICxocupat", "TICxGSES", "TICxCDRISC", "TICxBFIE", "TICxBFIA",
    "TICxBFIC", "TICxBFIN", "TICxBFIO", "TICxSOC", "TICxEAR"}
OTHER_DROPPED = {"PHQ_test_dificil", "sexo_nacer", "id"}
COVS = {"municip": "cov_rural_urban", "genero_actual": "cov_gender",
        "edad": "cov_age", "estado_civil_dicot": "cov_partner",
        "nivel_estudios_dicot": "cov_education",
        "laboral_actual_dicot": "cov_working"}


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
    assert d.shape == (391, 151), d.shape

    # Balance the books.
    items = {c for its, _ in TABLES.values() for c in its}
    known = items | set(REVERSED) | COMPOSITES | OTHER_DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known

    for alt, (src, k) in REVERSED.items():
        assert (d[alt] == k - d[src]).all(), alt
    for tot, prefix in TOTALS.items():
        its = TABLES[[t for t, (i, _) in TABLES.items()
                      if i[0].startswith(prefix + "_")][0]][0]
        assert (d[its].sum(axis=1) == d[tot]).all(), tot
    soc_scored = [f"SOC_{i}" for i in range(1, 14)
                  if i not in (1, 2, 3, 7, 10)] + \
        [f"SOC_{i}_inv" for i in (1, 2, 3, 7, 10)]
    assert (d[soc_scored].sum(axis=1) == d["SOC_total"]).all()
    ok = d["EAR_total"].notna()
    assert (d.loc[ok, block("EAR", 10)].sum(axis=1)
            == d.loc[ok, "EAR_total"]).all()
    assert (d["sexo_nacer"] == d["genero_actual"]).all()
    assert d["id"].is_unique
    assert not d.drop(columns=["id"]).duplicated().any()

    # Value-labelled blocks: the labels must cover exactly the permitted set.
    for table in LABELLED:
        its, rng = TABLES[table]
        for c in its:
            assert set(meta.variable_value_labels[c]) == set(rng), c

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, rng) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        allowed = set(rng)
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
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
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
