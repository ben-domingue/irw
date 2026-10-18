#!/usr/bin/env python3
# Source: https://zenodo.org/records/17234245
# DOI: 10.5281/zenodo.17234245
# Data: "Religiosity and Conspiracy Beliefs Patterns of Relationships.sav"
#   (SPSS, LimeSurvey export; variable labels carry the full Polish stem for
#   every item, value labels absent throughout)
# License: CC BY 4.0 (verified on the Zenodo record)
# Reference: Turska-Kawa, Agnieszka (2025). Religiosity and Conspiracy
#   Beliefs: Patterns of Relationships.
#
# 898 Polish respondents, one row each, two blocks on the same 1-5 scale:
#
#   CT1_SQ001..SQ027  conspiracy beliefs, 27 items  -> _conspiracy_beliefs
#   Rel2_SQ001..SQ005 religiosity, 5 items          -> _religiosity
#
# RIGHTS. The conspiracy block opens with the Generic Conspiracist Beliefs
# Scale: SQ001-SQ015 are GCB items in Polish translation, recognisable from
# the stems ("Rząd w sekrecie jest zamieszany w morderstwa niewinnych
# obywateli", "Niewielka, tajna grupa jest odpowiedzialna za wszystkie
# najważniejsze decyzje", "Tajne organizacje komunikują się z istotami
# pozaziemskimi", "Technologia umożliwiająca kontrolę umysłu jest
# stosowana..."). The register's "Generic Conspiracist Beliefs Scale family:
# GCB" row is verdict **ship**, so this is clear. SQ016-SQ027 are the study's
# own additions on vaccines, the war in Ukraine, 5G and COVID-19. They were
# administered as one matrix under one section prompt on one scale, so they
# ship as one table rather than being split on provenance.
#
# The five religiosity items have no register row.
#
# ONE DATA-ENTRY ERROR. `CT1_SQ022` holds a single `33` on a 1-5 scale; every
# other response in that item and that row is in range, which is a keying
# slip rather than a wider scale. That one item-response is dropped and the
# respondent keeps the rest.
#
# `Age`, `Fin`, `Edu` arrive as strings from the LimeSurvey export and are
# carried as covariates unparsed. `Fin2_SQ001` runs -5..5 and is a single
# bipolar self-assessment, not part of either instrument.
#
# PII: none. The value-level email screen and the variable-label screen are
# both clean. `submitdate`, `startdate`, `datestamp` and `seed` are LimeSurvey
# bookkeeping and are dropped -- a submission timestamp is not a covariate.
#
# Item text: NOT shipped, and the gap is specifically the anchors. BOTH label
# levels were checked. Variable labels carry the administered Polish stem for
# all 32 items, in LimeSurvey's "[stem] section prompt" form, so the stems and
# even the section prompts are in hand. Value labels are EMPTY for every item,
# so the 1-5 anchors are unknown -- and the administration is Polish with no
# author English, which would additionally owe a `translation_source` and a
# public issues-page callout. Where the text is: this .sav's variable labels
# for stems and prompts; the anchors need the paper or the questionnaire.

import os
import re

import pandas as pd
import pyreadstat

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from irw_validate._checks import run_qc  # noqa: E402


# --- raw input -------------------------------------------------------------
# Self-contained by design: the script fetches the deposit itself and caches
# it next to this file, so it re-runs in a fresh checkout (which is what
# metadata/covariate_labels/harvest.py does). Set TURSKAKAWA_RAW to point at an
# already-downloaded copy instead.
_URL = ("https://zenodo.org/api/records/17234245/files/Religiosity%20and%20Conspiracy%20Beliefs%20Patterns%20of%20Relationships.sav/content")
_NAME = "zenodo_17234245__religiosity_conspiracy.sav"


def _raw():
    override = os.environ.get("TURSKAKAWA_RAW")
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

SCALE = {1.0, 2.0, 3.0, 4.0, 5.0}
COVS = {"Sex": "cov_sex", "Age": "cov_age_group", "Edu": "cov_education",
        "Fin1": "cov_financial_situation", "MS1": "cov_marital_status"}


def convert():
    df, meta = pyreadstat.read_sav(_raw())
    labs = meta.column_names_to_labels or {}
    vlabs = meta.variable_value_labels or {}
    print(f"raw: {df.shape}")

    ct = sorted([c for c in df.columns if re.match(r"^CT1_SQ\d+$", c)])
    rel = sorted([c for c in df.columns if re.match(r"^Rel2_SQ\d+$", c)])
    print(f"blocks: conspiracy {len(ct)} items, religiosity {len(rel)} items")

    assert df["id"].nunique() == len(df), "id is not unique"

    n_stem = sum(1 for c in ct + rel if (labs.get(c) or "").strip())
    n_anchor = sum(1 for c in ct + rel if vlabs.get(c))
    print(f"label levels: {n_stem}/{len(ct)+len(rel)} items have a stem, "
          f"{n_anchor}/{len(ct)+len(rel)} have anchors -> no item text shipped")

    cov_src = {k: v for k, v in COVS.items() if k in df.columns}
    accounted = set(["id"]) | set(cov_src) | set(ct) | set(rel)
    skipped = {}
    for c in df.columns:
        if c in accounted:
            continue
        if c in ("submitdate", "startdate", "datestamp", "lastpage",
                 "startlanguage", "seed", "Consent"):
            skipped[c] = "LimeSurvey bookkeeping / consent, not data"
        elif c.startswith("Fin2"):
            skipped[c] = "single bipolar -5..5 self-assessment, not an item block"
        elif c.startswith("Fin") or c.startswith("MS") or c.startswith("Rel1"):
            skipped[c] = "single background question, not part of an instrument"
        else:
            skipped[c] = "not an item or covariate"
    for c, why in sorted(skipped.items()):
        print(f"  skip {c:16} {why}")
    assert accounted | set(skipped) == set(df.columns), "books do not balance"

    written = 0
    for name, cols in (("conspiracy_beliefs", ct), ("religiosity", rel)):
        long = (df[["id"] + cols].melt(id_vars="id", var_name="item",
                                       value_name="resp")
                .dropna(subset=["resp"]))
        long["resp"] = long["resp"].astype(float)

        off = long[~long["resp"].isin(SCALE)]
        for _, r in off.iterrows():
            print(f"    drop {r['item']}={r['resp']:g} (one cell outside the "
                  f"1-5 scale -- keying slip)")
        assert len(off) <= 2, f"{name}: {len(off)} off-scale cells"
        long = long[long["resp"].isin(SCALE)]

        long = long.merge(df[["id"] + list(cov_src)].rename(columns=cov_src),
                          on="id", how="left")
        assert long["item"].nunique() > 1, f"{name}: single item"
        assert long["id"].nunique() >= 100, f"{name}: N={long['id'].nunique()}"
        long = long[["id", "item", "resp"] + list(cov_src.values())]

        out_name = f"turska_kawa_2025_{name}"
        # The shared checks, which the script's own assertions are not
        # (irw_validate.contract `no_validator`). Fails block; the
        # warnings here are legitimate and are printed.
        _checks = run_qc(long)
        _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
        assert not _fails, _fails
        for _c in _checks:
            if _c.status == "warn":
                print(f"    [qc warn] {_c.name}: {_c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, f"{out_name}.csv"), index=False)
        written += len(long)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")
    print(f"total responses: {written}")


if __name__ == "__main__":
    convert()
