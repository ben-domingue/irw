#!/usr/bin/env python3
# Source: https://zenodo.org/records/15345328
# DOI: 10.5281/zenodo.15345328
# Data: final_db_substances.dta (Stata, variable + value labels present)
# License: CC BY 4.0 (verified on the Zenodo record)
# Reference: Osorio, Alfonso (2025). Dataset for the article "Exploring the
#   links between parenting styles, differentiation of self and substance use
#   in adolescents".
#
# 7,161 adolescents aged 12-17 across six countries. Three instruments share
# the file, each on its own scale, which is why the triage flagged it
# `resp_scale_mixed`:
#
#   vpa_dos01..22   Differentiation of Self Inventory, 0-5   -> _dsi
#   vpa_estilo01..06 + vpa_estilos07..16  parenting styles, 0-6 -> _parenting
#   vpa_fumar/porros/alcohol/binge/drogas substance use, 0-4  -> _substance_use
#
# WHY `dos01..21` IS NOT SHIPPED. The file carries a second copy of the DSI
# block under bare `dos01..dos21`, labelled "Item dosNN invertido 1 a 6". It is
# derived, and the script proves it rather than assuming: for every one of the
# 21, `dos{N} == 6 - vpa_dos{N}` on **100%** of the rows where both are
# present, and the match is searched over all 22 candidates rather than taken
# positionally. (`vpa_dos22` has no reverse-coded twin, which is why there are
# 21 and not 22.) Shipping both would put the same responses in the corpus
# twice under opposite polarity.
# `afecto`, `control`, `reac`, `dist`, `diferenciacion` are subscale
# means (fractional), `*_dic`/`*2`/`relig_3cat` are recodes, and `Z*` are
# z-scores -- all derived, all dropped with a printed reason.
#
# RIGHTS. The Differentiation of Self Inventory (Skowron & Friedlander) has NO
# row in itemtext/instrument_rights_register.csv, so nothing blocks it, but a
# miss is not an all-clear -- it is logged in
# itemtext/register_gaps_2026-10-18.csv as an uncovered published instrument.
# The parenting and substance-use blocks read as study-authored.
#
# Item text: NOT shipped. Both label levels were checked and both are
# populated -- variable labels carry the full Spanish stem for every item
# ("La gente suele decirme que soy excesivamente emocional") and value labels
# carry the anchors ("Nada cierto 0" .. "Totalmente cierto 5" for the DSI,
# "Nunca 0" .. "Muy a menudo 6" for parenting). The administration is Spanish
# and the deposit supplies no author English, so the English half of the
# schema would be an IRW translation owing a `translation_source` and a public
# issues-page callout. Queued with the other seven such deposits (TODO) rather
# than bolted onto a response batch; the text is in this .dta's own labels.

import os

import pandas as pd
import pyreadstat

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "automated_finding", "runs", "hr5", "raw",
                   "zenodo_15345328__final_db_substances.dta")

DSI = [f"vpa_dos{i:02d}" for i in range(1, 23)]
PARENTING = ([f"vpa_estilo{i:02d}" for i in range(1, 7)]
             + [f"vpa_estilos{i:02d}" for i in range(7, 17)])
SUBSTANCE = ["vpa_fumar", "vpa_porros", "vpa_alcohol", "vpa_binge",
             "vpa_drogas"]

# Documented permitted sets, from the value labels in the .dta itself.
SCALES = {"dsi": set(range(0, 6)),
          "parenting": set(range(0, 7)),
          "substance_use": set(range(0, 5))}

COVS = {"pais": "cov_country", "titularidad": "cov_school_ownership",
        "tipo": "cov_school_type", "zona": "cov_zone",
        "vpa_edad": "cov_age", "vpa_sexo": "cov_sex",
        "vpa_estudios_p": "cov_father_education",
        "vpa_estudios_m": "cov_mother_education",
        "vpa_religion": "cov_religion", "vpa_iglesia": "cov_worship_attendance",
        "vpa_rezar": "cov_prayer_frequency", "vpa_fe": "cov_faith_importance"}

BLOCKS = {"dsi": DSI, "parenting": PARENTING, "substance_use": SUBSTANCE}


def convert():
    df, meta = pyreadstat.read_dta(RAW)
    print(f"raw: {df.shape}")

    # `oleada` records which wave a class is in and holds a single value (1)
    # for every row, so there is no longitudinal structure to carry.
    assert df["oleada"].dropna().nunique() <= 1, "oleada now varies -- add wave"

    # Prove the derived DSI copy before dropping it, and find each one's
    # source by searching all 22 candidates -- not by trusting the numbering.
    derived = [f"dos{i:02d}" for i in range(1, 22)]
    for b in derived:
        best, best_r = None, -1.0
        for a in DSI:
            both = df[[a, b]].dropna()
            if both.empty:
                continue
            r = ((both[a] + both[b]) == 6).mean()
            if r > best_r:
                best, best_r = a, r
        assert best_r == 1.0, f"{b}: closest is {best} at {best_r:.3f}, not 1.0"
        assert best == f"vpa_{b}", f"{b} reverses {best}, not vpa_{b}"
    print(f"dropping {derived[0]}..{derived[-1]}: each is exactly "
          f"6 - its vpa_dos twin on every row where both are present "
          f"(derived reverse-coded copy; vpa_dos22 has no twin)")

    cov_src = {k: v for k, v in COVS.items() if k in df.columns}
    covs = df[["id"] + list(cov_src)].rename(columns=cov_src).copy()

    # Balance the books: every source column is an item, a covariate, or a
    # printed skip.
    accounted = set(["id", "oleada"]) | set(cov_src)
    for cols in BLOCKS.values():
        accounted |= set(cols)
    skipped = {}
    for c in df.columns:
        if c in accounted:
            continue
        if c in derived:
            skipped[c] = "derived reverse-coded DSI copy (proved 6-x above)"
        elif c in ("afecto", "control", "reac", "dist", "diferenciacion"):
            skipped[c] = "subscale mean (fractional), derived"
        elif c.endswith("_dic"):
            skipped[c] = "dichotomised recode of a column already carried"
        elif c.endswith(("2", "5", "0")) or c in ("edad", "relig_3cat",
                                                  "consumos", "padresuniv"):
            skipped[c] = "categorised/quantile recode of a column carried above"
        elif c in ("institucion", "clase"):
            skipped[c] = "free-text school/class label, not a covariate"
        else:
            skipped[c] = "not an item, covariate or recode"
    for c, why in sorted(skipped.items()):
        print(f"  skip {c:24} {why}")
    assert accounted | set(skipped) == set(df.columns), "books do not balance"

    written = set()
    for name, cols in BLOCKS.items():
        present = [c for c in cols if c in df.columns]
        assert len(present) == len(cols), f"{name}: missing {set(cols)-set(present)}"
        long = df[["id"] + present].melt(id_vars="id", var_name="item",
                                         value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(float)

        bad = set(long["resp"].unique()) - SCALES[name]
        assert not bad, f"{name}: {sorted(bad)} outside the documented scale"

        long = long.merge(covs, on="id", how="left")
        assert long["item"].nunique() > 1, f"{name}: single item"
        assert long["id"].nunique() >= 100, f"{name}: N={long['id'].nunique()}"

        out_cols = ["id", "item", "resp"] + [c for c in cov_src.values()
                                             if c in long.columns]
        long = long[out_cols]
        out_name = f"osorio_2025_{name}"
        assert out_name not in written, f"duplicate output name {out_name}"
        written.add(out_name)
        long.to_csv(os.path.join(OUT_DIR, f"{out_name}.csv"), index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
