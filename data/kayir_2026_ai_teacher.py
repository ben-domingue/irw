#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/KRWI6E
# DOI: none found (Harvard Dataverse deposit only; no linked publication in
#   its metadata, and a Crossref title search found no paper as of
#   2026-10-02).
#   Kayir, G. (2026). "Validation of the Turkish AI Specific Teacher Attitude
#   Questionnaire with Measurement Invariance across Gender and Teaching
#   Level." Harvard Dataverse.
# Data: Dataverse datafile 14075946, data.sav (format=original; 392 rows x
#       73 columns; Turkish in-service teachers).
# License: CC0 1.0 (Dataverse dataset licence).
#
# Item text: not shipped. Both label levels checked: no variable labels on
#   any item; value labels only on the AI-use frequency block (Turkish
#   frequency anchors) and the covariates. Item stems are not in the
#   deposit; the AI-STAQ, TIPI, TAMPST and Innovativeness Scale wording is
#   in their published sources.
#
# Tables (item codes are the source column names). The deposit description
# names the instruments: AI-STAQ, the Ten-Item Personality Inventory (TIPI),
# the Technology Acceptance Measure for Pre-service Teachers (TAMPST) and the
# Innovativeness Scale (IS).
#   kayir_2026_aistaq          YZ1-YZ8  AI-Specific Teacher Attitude
#                              Questionnaire, Turkish (two factors: perceived
#                              importance YZ1-4, interest YZ5-8). TOTALYZteacher
#                              equals their sum (asserted).
#   kayir_2026_innovativeness  Bireyselyenilikcilik1-5  Innovativeness Scale
#   kayir_2026_tampst          OgretmenBIT1-7  TAMPST
#   kayir_2026_tipi            BIGfive1-10  TIPI (observed 1-5; the original
#                              TIPI is 7-point, so this is an adapted format)
#   kayir_2026_ai_use          SINAVicinYZ .. YAZIMKONTROLU (8 items)  how
#                              often the teacher uses AI for exams, creating
#                              homework, reading homework, lesson design,
#                              e-reports, project writing, personal
#                              development, spell-checking. Value-labelled
#                              1 = never .. 5 = always, asserted.
#   The Likert blocks' response formats are NOT documented in the deposit (no
#   value labels, no codebook, no paper), so no permitted-value set is
#   asserted for them; values are only checked to be whole numbers.
#
# Dropped:
#   - alt1, alt4, alt5, alt7: reverse-coded copies of BIGfive1/4/5/7
#     (alt = 6 - BIGfive in every row, asserted).
#   - Composites: TOTALYZteacher, TOTALbireyselyenilikcilik, totalTEACHERbit,
#     the five TIPI trait scores and their *ALT versions, BOY1FAK, BOY2FAK,
#     and three z-scores.
#   - BRANS: an undocumented 0/1 code that does not match ALTBRANS.
#   - EGITIMDEbilinenuygulamalar, KullanilanYZ: only 0 or missing in every
#     row (empty multi-select stubs).
# id: row index (no respondent id in the file).
# Covariates: cov_teacher_type (1 classroom, 2 subject), cov_gender
#   (1 female, 2 male), cov_age, cov_seniority (years), cov_school_level
#   (1 primary, 2 middle, 3 high), cov_degree (1 bachelor, 2 graduate),
#   cov_perceived_ses (1-10), cov_ai_training (1 trained, 2 not),
#   cov_ai_daily_use (1 yes, 2 no), cov_ai_in_curriculum (1 should, 2 no
#   need).

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
URL = ("https://dataverse.harvard.edu/api/access/datafile/14075946"
       "?format=original")

AI_USE = ["SINAVicinYZ", "ÖDEVOLUSTUR", "ÖDEVOKU", "DERSTASARIMI",
          "MEBeRAPOR", "PROJEYAZMA", "KİŞİSELGELİŞİM", "YAZIMKONTROLÜ"]
TABLES = {
    "kayir_2026_aistaq": [f"YZ{i}" for i in range(1, 9)],
    "kayir_2026_innovativeness": [f"Bireyselyenilikcilik{i}"
                                  for i in range(1, 6)],
    "kayir_2026_tampst": [f"ÖğretmenBİT{i}" for i in range(1, 8)],
    "kayir_2026_tipi": [f"BİGfive{i}" for i in range(1, 11)],
    "kayir_2026_ai_use": AI_USE,
}
DOCUMENTED = {"kayir_2026_ai_use": range(1, 6)}
REVERSED = {"alt1": "BİGfive1", "alt4": "BİGfive4", "alt5": "BİGfive5",
            "alt7": "BİGfive7"}
COMPOSITES = {"TOTALYZteacher", "TOTALbireyselyenilikçilik", "totalTEACHERbit",
              "dışadönüklük", "uyumluluk", "sorumluluk", "nörotiklik",
              "deneyimeaçıklık", "extraALT", "UyumALT", "dengesizlikALT",
              "yeniaçıklıkALT", "sorumlulukALT", "BOY1FAK", "BOY2FAK",
              "ZTOTALYZteacher", "ZSco01", "StdZ01"}
OTHER_DROPPED = {"BRANŞ", "EĞİTİMDEbilinenuygulamalar", "KullanılanYZ"}
COVS = {"ALTBRANŞ": "cov_teacher_type", "CİNSİYET": "cov_gender",
        "YAŞ": "cov_age", "KIDEM": "cov_seniority",
        "KURUMGÖREVYAPILAN": "cov_school_level",
        "EĞİTİMDÜZEYİ": "cov_degree", "algılananSED": "cov_perceived_ses",
        "YZeğitim": "cov_ai_training",
        "gündelikyaşamYZkullanma": "cov_ai_daily_use",
        "YZmufredattaolmalı": "cov_ai_in_curriculum"}


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
    assert d.shape == (392, 73), d.shape

    # Balance the books.
    items = {c for its in TABLES.values() for c in its}
    known = items | set(REVERSED) | COMPOSITES | OTHER_DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known

    for alt, src in REVERSED.items():
        assert (d[alt] == 6 - d[src]).all(), alt
    assert (d["TOTALYZteacher"] == d[TABLES["kayir_2026_aistaq"]].sum(
        axis=1)).all()
    for c in ("EĞİTİMDEbilinenuygulamalar", "KullanılanYZ"):
        assert set(d[c].dropna()) == {0}, c
    labels = {1.0: "HİÇBİRZAMAN", 2.0: "NADİREN", 3.0: "BAZEN",
              4.0: "SIKSIK", 5.0: "HERZAMAN"}
    for c in AI_USE:
        assert meta.variable_value_labels[c] == labels, c

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
            allowed = set(DOCUMENTED[table])
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
