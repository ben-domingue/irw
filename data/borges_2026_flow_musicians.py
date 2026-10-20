#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Dataset_of_Flow_State_Scale_Responses_in_Portuguese_Musicians_Excel_em/30166636
# DOI: 10.6084/m9.figshare.30166636 (v2)
#   Nery Borges (2026). The deposit record for THIS DOI names no individual author --
#   its sole listed author is the placeholder "Research Team" (figshare author id
#   22277993, inactive) and its own citation reads "Team, Research (2025)". The author
#   is identified from the same group's companion deposit
#   10.6084/m9.figshare.32995919 ("Dataset of Portuguese Musicians' Responses to the
#   Flow State Scale-1 (FSS-1)", Nery Borges 2026), which carries the identical 36
#   EEF_VP_Q1..Q36 item columns and the same Participant numbering.
#
# DUPLICATE DEPOSIT -- read before shipping. 32995919 holds 194 of these 382
#   respondents: joining the two on (Participant, item) gives 6,962 shared cells and
#   100% agreement on every one of them, with no cell in 32995919 absent here. This
#   file is therefore a strict superset, and only one of the two should reach IRW.
#   `data/borges_2026_flow_state.py` (same batch, slice 2) builds the 194-respondent
#   version from 32995919; this script builds the 382-respondent version from
#   30166636. Ship this one and drop that one, or the corpus carries the same 194
#   respondents twice under two table names.
# Data: "Research_Data, Dataset, Musical_flow_in_context, Music&Science.csv" --
#       semicolon-delimited, 382 rows x 65 columns: Participant (a unique integer per
#       row, 382 distinct), ten background variables, D1-D9, the 36 FSS-1 items
#       EEF_VP_Q1..EEF_VP_Q36 on a 1-5 scale, and F1-F9. The deposit description
#       documents exactly this ("responses to the 36 FSS-1 items (9 subscales)") and
#       states the data are fully anonymised. One missing item cell in the whole file.
#       (The description's "194 musicians" refers to an earlier version; v2 holds 382
#       distinct Participant values with no duplicated row and no duplicated id.)
# License: CC BY 4.0 (figshare API record for article 30166636: license value 1,
#          "CC BY 4.0").
#
# Item text: not shipped. The CSV has no label level at all and the item headers are
#   positional codes (EEF_VP_Q1..Q36). The instrument is Jackson & Marsh's (1996) Flow
#   State Scale, whose wording is distributed under licence by Mind Garden, and the
#   Portuguese adaptation administered here has its own unestablished terms; neither has
#   a row in itemtext/instrument_rights_register.csv, and silence does not ship. Where
#   the text actually is: the published FSS-1 and its (unlocated) Portuguese adaptation
#   -- not in this deposit, which contains the data file alone.
#
# Item codes: the source headers EEF_VP_Q1..EEF_VP_Q36 are kept verbatim as `item`.
# Columns skipped: D1-D9 and F1-F9 -- fractional per-subscale means over the item
#   columns (e.g. 3.75, 2.25), i.e. derived composites rather than responses. The
#   deposit description calls these "indicators related to psychometric validation
#   procedures".
# Table:
#   borges_2026_flow_musicians  36 items, 1-5
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s3"
URL = "https://ndownloader.figshare.com/files/58098634"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
NAME = "borges_2026_flow_musicians"

COVS = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Instrument": "cov_instrument",
    "Activit": "cov_activity",
    "Actuation": "cov_actuation",
    "Academic_degree": "cov_academic_degree",
    "Instrument_years": "cov_instrument_years",
    "Study_days_per_week": "cov_study_days_per_week",
    "Daity_study_hours": "cov_daily_study_hours",
    "Performance_year": "cov_performance_year",
}
ITEMS = [f"EEF_VP_Q{k}" for k in range(1, 37)]


def screen_for_pii(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"[pii] examined {df.shape[1]} columns, {len(text_cols)} of them string-typed")
    assert df.shape[1] > 0
    pats = [r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}", r"\+?\d[\d \-()]{8,}",
            r"\d{1,4}[/-]\d{1,2}[/-]\d{1,4}"]
    hits = [(c, p) for c in text_cols for p in pats
            if df[c].dropna().astype(str).str.contains(p, regex=True, na=False).any()]
    assert not hits, hits
    print("[pii] every column is numeric (codes and Likert responses); no free text, "
          "no name/email/date column")


def convert() -> None:
    r = requests.get(URL, headers=UA, timeout=300)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content), sep=";")
    assert df.shape == (382, 65), df.shape
    screen_for_pii(df)
    assert not df["Participant"].duplicated().any() and df["Participant"].nunique() == 382

    derived = [c for c in df.columns if re.fullmatch(r"[DF]\d", str(c))]
    assert len(derived) == 18, derived
    print(f"[books] skipped {derived}: fractional per-subscale means over the 36 items")

    accounted = {"Participant"} | set(COVS) | set(ITEMS) | set(derived)
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    print(f"[books] 65 source columns accounted for (1 id + {len(COVS)} covariates + "
          f"{len(ITEMS)} items + {len(derived)} skipped)")

    df = df.rename(columns={"Participant": "id", **COVS})
    cov_cols = list(COVS.values())
    t = df[["id"] + cov_cols + ITEMS].melt(
        id_vars=["id"] + cov_cols, value_vars=ITEMS,
        var_name="item", value_name="resp")
    t["resp"] = pd.to_numeric(t["resp"], errors="coerce")
    n_na = int(t["resp"].isna().sum())
    t = t.dropna(subset=["resp"])
    print(f"[clean] dropped {n_na} missing item cell(s)")
    assert (t["resp"] % 1 == 0).all()
    t = t[["id", "item", "resp"] + cov_cols].reset_index(drop=True)

    pv = [1, 2, 3, 4, 5]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100 and t["item"].nunique() >= 3
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:180]}")
    rep = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                      context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, [(f.check, f.message) for f in rep.errors]
    for f in rep.warnings:
        print(f"    [validate warn] {f.check}: {f.message[:180]}")
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
          f"resp={t['resp'].min():g}-{t['resp'].max():g}")


if __name__ == "__main__":
    convert()
