#!/usr/bin/env python3
# Source: https://zenodo.org/records/23267991
# DOI: 10.5281/zenodo.23267991 (data; no article found)
# Deposit: Pérez Vásquez ER, Cárdenas Vila RM, Estrada Alomía ER, Tirado
#   Chacaliaza KP, Díaz Gamarra PP (2026). Evidencias psicométricas escala
#   Paykel en adultos peruanos [dataset]. Zenodo.
# Data: "DATOS UCV FINAL COMPLETO.xlsx" (1,000 Peruvian university students
#   aged 18-31, Lima) and PAYKEL_FINAL.omv, the authors' jamovi file, whose
#   metadata carries the covariate value labels used below.
# License: CC BY 4.0 (verified on the Zenodo record).
#
# Found by the automated_finding repos sweep of 2026-11-02 (mode 3), worked
# from leads/repos_leads_2026-11-02.csv the same day (BATCH_LOG.md).
#
# ONE output table:
#   perez_vasquez_2026_paykel  Paykel Suicide Scale, P1..P5, 0 = no,
#     1 = yes (dichotomous; the items sum to the deposit's Paykel_total).
# NOT shipped, all from the same file:
#   - R1..R4 (Roberts) and H1..H9 (PHQ-9): every item's middle category 2 is
#     nearly empty (0-19 of 1,000 per item; six PHQ-9 items never use it at
#     all), against heavy use of 0, 1 and 3. That is not how PHQ-9 data looks
#     and suggests a recode somewhere upstream, so they are excluded rather
#     than shipped on a doubtful scale.
#   - B1..B13 (BIEPS-A, 1-3): the jamovi file labels the codes only "1",
#     "2", "3", and nothing in the deposit says which end is agreement, so
#     the response direction cannot be established.
#   - the composite totals.
# Covariates (jamovi labels): age, sex, study condition (only studies / works
#   too), study mode, study cycle, family type.
# Dropped: L_NAC and L_RESIDENCIA (region of birth / Lima zone; geographic
#   codes under the 2026-10-20 ruling), LGTBIQ+ and TIPO_LGTBIQ+ (codes 0 in
#   the data have no label, and sexual orientation is not needed here),
#   TERAPIA (codes 0, 1, 3 have no label), T_UNIVERSIDAD (code 4 has no label).
# `id` is the deposit's own ID column.
#
# Item text: not shipped. The deposit carries item codes only; the Spanish
#   Paykel wording is not in it.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("PAYKEL_RAW", "DATOS UCV FINAL COMPLETO.xlsx")
P = [f"P{i}" for i in range(1, 6)]
NOT_SHIPPED = ([f"R{i}" for i in range(1, 5)] + [f"H{i}" for i in range(1, 10)] + [f"B{i}" for i in range(1, 14)]
               + ["Paykel_total", "Roberts_total", "PHQ9_total", "BIEPS_total", "BIEPS_Aceptacion_Control",
                  "BIEPS_Autonomia", "BIEPS_Vinculos", "BIEPS_Proyectos"])
DROPPED = ["L_NAC", "L_RESIDENCIA", "LGTBIQ+", "TIPO_LGTBIQ+", "TERAPIA", "T_UNIVERSIDAD"]
LAB = {
    "Sexo": ("cov_sex", {1: "male", 2: "female"}),
    "CONDICION": ("cov_condition", {1: "studies only", 2: "studies and works (employed)",
                                    3: "studies and works (self-employed)", 4: "other"}),
    "MOD_ESTUDIO": ("cov_study_mode", {1: "in person", 2: "blended"}),
    "CICLO": ("cov_cycle", {1: "I-II", 2: "III-IV", 3: "V-VI", 4: "VII-VIII", 5: "IX+"}),
    "T_FAMILIA": ("cov_family_type", {1: "nuclear", 2: "single-parent", 3: "extended", 4: "blended"}),
}


def convert():
    df = pd.read_excel(RAW)
    assert df.shape == (1000, 52), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    assert (df[P].sum(axis=1) - df["Paykel_total"]).abs().max() == 0
    h = df[[f"H{i}" for i in range(1, 10)]]
    print("PHQ-9 category-2 counts per item:", (h == 2).sum().tolist())
    assert df["ID"].is_unique
    df["id"] = df["ID"]
    df["cov_age"] = df["Edad"]
    covs = ["cov_age"]
    for src, (dst, lab) in LAB.items():
        df[dst] = df[src].map(lab)
        assert df[dst].notna().all(), src
        covs.append(dst)
    long = df[["id"] + covs + P].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    assert set(long["resp"]) <= {0, 1}
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [0, 1] for c in P})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    used = set(P) | set(NOT_SHIPPED) | set(DROPPED) | set(LAB) | {"ID", "Edad"}
    left = set(df.columns) - used - {"id"} - set(covs)
    assert not left, left
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "perez_vasquez_2026_paykel.csv"), index=False)
    print(f"perez_vasquez_2026_paykel: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
