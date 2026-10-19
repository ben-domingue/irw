#!/usr/bin/env python3
# Source: https://zenodo.org/records/5117904
# DOI: 10.5281/zenodo.5117904
# Data: "! Base datos ansiedad estudiantes covid19.sav" (SPSS; variable AND
#   value labels populated for every GAD-7 item)
# License: CC BY 4.0 (verified on the Zenodo record)
# Reference: Chaple-Gil, A. M., Monzón-Pérez, M. E., Rodríguez, ... (2021).
#   Base de datos - Ansiedad de estudiantes de Estomatología cubanos e
#   intención de abandonar estudios durante la COVID-19.
#
# 917 Cuban dentistry students. One instrument: the GAD-7, `GAD7_1..GAD7_7`,
# scored 0-3 with the standard anchors ("Nunca" / "Algunos días" / "Más de la
# mitad de los días" / "Casi todos los días"), taken from the file's own value
# labels rather than assumed.
#
# RIGHTS: the "PHQ and GAD screener family (PHQ-2/9, GAD-2/7)" row in
# itemtext/instrument_rights_register.csv is verdict `ship`, and its matcher
# `^phq|^gad` matches these codes, so this is one of the rare cases where the
# automated check and the hand read agree.
#
# `Sumatoria_GAD7` is the scored total and `Ansiedad` its clinical cut, both
# derived and dropped. The `Nec_*` set is a multi-select "which resources do
# you need" question expanded one column per option, each 1/2 -- those are
# nine separate binary answers to one checklist, not an ordinal instrument,
# so they are carried as covariates rather than melted into items.
#
# PII: none. `Espec_Otro` is the "other needs, specify" free text; all 49
# non-empty values were read and they describe study resources (laptops,
# laboratories, teaching materials). No names, contacts or clinical
# narratives. The value-level email screen is also clean.
#
# Item text: NOT shipped, and this one is a close call worth recording. BOTH
# label levels are populated -- variable labels carry the administered Spanish
# stem for all seven items ("Se ha sentido nervioso, ansioso o alterado") and
# value labels carry all four anchors. So the administered wording is in hand.
# What is missing is author-supplied English: the GAD-7's canonical English
# exists but reproducing it here would make IRW the source of that text,
# owing a `translation_source` and a public issues-page callout. Queued with
# the other non-English deposits (TODO) rather than decided inside a response
# batch. Where the text is: this .sav's own variable and value labels.

import os

import pandas as pd
import pyreadstat

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from irw_validate._checks import run_qc  # noqa: E402


# --- raw input -------------------------------------------------------------
# Self-contained by design: the script fetches the deposit itself and caches
# it next to this file, so it re-runs in a fresh checkout (which is what
# metadata/covariate_labels/harvest.py does). Set CHAPLEGIL_RAW to point at an
# already-downloaded copy instead.
_URL = ("https://zenodo.org/api/records/5117904/files/%21%20Base%20datos%20ansiedad%20estudiantes%20covid19.sav/content")
_NAME = "zenodo_5117904__ansiedad.sav"


def _raw():
    override = os.environ.get("CHAPLEGIL_RAW")
    if override:
        return override if os.path.isfile(override) else os.path.join(override, _NAME)
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "automated_finding", "runs", "raw_cache")
    os.makedirs(cache, exist_ok=True)
    dest = os.path.join(cache, _NAME)
    if not os.path.exists(dest):
        import urllib.request
        req = urllib.request.Request(
            _URL, headers={"User-Agent":
                           "IRW-Finder/1.0 (ben.domingue@gmail.com)"})
        with urllib.request.urlopen(req, timeout=300) as r, \
                open(dest, "wb") as fh:
            fh.write(r.read())
    return dest

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

GAD7 = [f"GAD7_{i}" for i in range(1, 8)]

COVS = {"Edad": "cov_age_group", "Genero": "cov_gender", "Raza": "cov_race",
        "Programa": "cov_programme", "Curso": "cov_year_of_study",
        "Universidad": "cov_university", "Solo_Aislado": "cov_feels_isolated",
        "COVID19_Impacto_SM": "cov_covid_mental_health_impact",
        "Abandonar_Est": "cov_wishes_to_drop_out"}
NEC = {"Nec_None": "cov_needs_none", "Nec_Biblio": "cov_needs_library",
       "Nec_Electr": "cov_needs_elibrary", "Nec_Esp_Sil": "cov_needs_quiet_space",
       "Nec_Serv_Tut": "cov_needs_tutoring", "Nec_Internet": "cov_needs_internet",
       "Nec_Libros_Fisicos": "cov_needs_print_books",
       "Nec_Libros_Elect": "cov_needs_ebooks", "Nec_Otros": "cov_needs_other"}


def convert():
    df, meta = pyreadstat.read_sav(_raw())
    print(f"raw: {df.shape}")
    vlabs = meta.variable_value_labels or {}

    # The deposit has no respondent key; the row index is the person.
    df = df.reset_index().rename(columns={"index": "id"})
    df["id"] = df["id"] + 1

    cov_src = {**COVS, **NEC}
    cov_src = {k: v for k, v in cov_src.items() if k in df.columns}

    accounted = set(["id"]) | set(cov_src) | set(GAD7)
    skipped = {}
    for c in df.columns:
        if c in accounted:
            continue
        if c == "Sumatoria_GAD7":
            skipped[c] = "scored GAD-7 total, derived"
        elif c == "Ansiedad":
            skipped[c] = "clinical cut of the GAD-7 total, derived"
        elif c == "Dico_COVID19_Impacto":
            skipped[c] = "dichotomised recode of COVID19_Impacto_SM"
        elif c == "Espec_Otro":
            skipped[c] = "free-text 'other needs'; read, no PII, not an item"
        elif c in ("Beb_Alcoh", "Pag_Facturas", "Dif_Pago_Fac", "Comp_Alimen",
                   "Dif_Comp_Alim", "Selecc_Ant", "Empezar_carr_elegir") \
                or c.startswith("Fac_"):
            skipped[c] = "single background question, not part of an instrument"
        else:
            skipped[c] = "not an item or covariate"
    for c, why in sorted(skipped.items()):
        print(f"  skip {c:22} {why}")
    assert accounted | set(skipped) == set(df.columns), "books do not balance"

    long = df[["id"] + GAD7].melt(id_vars="id", var_name="item",
                                  value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(float)

    # Documented permitted set, per item, from the file's own value labels.
    for c in GAD7:
        permitted = set(float(k) for k in (vlabs.get(c) or {}))
        assert permitted == {0.0, 1.0, 2.0, 3.0}, f"{c}: labels {permitted}"
        bad = set(long.loc[long["item"] == c, "resp"].unique()) - permitted
        assert not bad, f"{c}: {sorted(bad)} outside its value labels"
    print("  every GAD-7 item within its documented 0-3 anchor set")

    long = long.merge(df[["id"] + list(cov_src)].rename(columns=cov_src),
                      on="id", how="left")
    assert long["item"].nunique() == 7, "GAD-7 should have 7 items"
    assert long["id"].nunique() >= 100, f"N={long['id'].nunique()}"
    long = long[["id", "item", "resp"] + list(cov_src.values())]

    name = "chaple_gil_2021_gad7"
    # The shared checks, which the script's own assertions are not
    # (irw_validate.contract `no_validator`). Fails block; the
    # warnings here are legitimate and are printed.
    _checks = run_qc(long)
    _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
    assert not _fails, _fails
    for _c in _checks:
        if _c.status == "warn":
            print(f"    [qc warn] {_c.name}: {_c.detail[:160]}")
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
