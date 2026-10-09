#!/usr/bin/env python3
# Source: https://zenodo.org/records/15305238
# DOI: 10.5281/zenodo.15305238 (dataset; no paper DOI on the record)
#   Buzzi, Maria Claudia (2025). "Student questionnaire (technology and Covid-19)"
#   [data set]. Zenodo.
# Data: "results-survey220905_grezzi per correlazione.xlsx" -- a LimeSurvey export, in
#       Italian. Sheet 1: 145 students aged 18+ (upper-secondary and higher education)
#       x 104 columns; each header is "<code>. <question text> [<subquestion text>]".
#       Sheet "Foglio1": the questionnaire's response options per question (the codebook).
#       Record: "Data from 152 Italian students aged 18 and above collected to understand
#       how technology helped them cope with academic performance, emotional
#       well-being, behaviors and the support. Only in Italian."
# License: CC BY 4.0 (Zenodo record).
#
# Item text: buzzi_2025_autonomy shipped (header stems + Foglio1 options, Italian
#   administered wording; English *_translated is IRW's own; built by
#   automated_finding/itemtext_verification/make_itemtext_buzzi_2025.py).
#   buzzi_2025_cyrm12 not shipped, though cheap: its headers carry the 12 Italian CYRM-12
#   statements and Foglio1 the five options, but the Resilience Research Centre's page
#   says only that the CYRM is "available for free for researchers, academics and
#   front-line staff" -- neither a grant nor a clear restriction, so it is held for a
#   rights ruling. (An .xlsx has no SPSS label levels; the two levels here are the column
#   headers, which carry the stems, and Foglio1, which carries the options.)
#
# Tables:
#   buzzi_2025_autonomy  G01Q04_SQ001-SQ004  "Indica quanto sei autonoma/o nello svolgere
#                        le seguenti attività": study and school / sport / leisure /
#                        getting around. 1 per niente .. 5 completamente (header + Foglio1).
#   buzzi_2025_cyrm12    G05Q36_SQ012-SQ122  the 12 CYRM-12 statements (Liebenberg et al.
#                        2013), "Ripensando ai periodi di maggiori restrizioni in pandemia,
#                        in che misura ti riconosci nelle seguenti affermazioni?"
#                        1 per nulla .. 5 moltissimo (Foglio1).
#   Item codes are the LimeSurvey codes with the brackets made an underscore
#   ("G05Q36[SQ012]" -> "G05Q36_SQ012"), reversible.
# Skipped (each printed with its reason): submitdate; the seven multi-select checklists
#   (G02Q05, G02Q06, G02Q09, G02Q14, G02Q16, G01Q29, G01Q37: tick-all-that-apply
#   inventories of tools, subjects, activities and sources of support; 57 columns); and 26 single
#   questions on distinct topics with no shared construct (distance-learning conditions,
#   grades, changes in family life, fear, tiredness, screen time, exercise, eating,
#   socialising). Most are stored as option labels, not codes.
# Accepted QC warning: buzzi_2025_autonomy imputed_values* (every item has one value over
#   60%; 78% "completamente" on leisure). Adults rating their own autonomy at the ceiling;
#   no fractional cells, nothing to suggest filling.
# Covariates: cov_gender (female / male / prefer not to say), cov_age (18-24, "25+"),
#   cov_school (upper secondary / higher education / other), translated from the labels.
# id = the LimeSurvey response ID (unique).

import os
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "buzzi_2025"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/15305238/files/"
       "results-survey220905_grezzi%20per%20correlazione.xlsx/content")
TABLES = {"buzzi_2025_autonomy": "G01Q04", "buzzi_2025_cyrm12": "G05Q36"}
N_ITEMS = {"G01Q04": 4, "G05Q36": 12}
CHECKLISTS = ["G02Q05", "G02Q06", "G02Q09", "G02Q14", "G02Q16", "G01Q29", "G01Q37"]
COVS = {"G01Q01": "cov_gender", "G01Q02": "cov_age", "G01Q03": "cov_school"}
GENDER = {"Femminile": "female", "Maschile": "male",
          "Preferisco non rispondere": "prefer not to say"}
SCHOOL = {"Scuola secondaria di secondo grado (Liceo, Istituto Tecnico, ecc.)":
          "upper secondary",
          "Istruzione superiore (Università, Alta formazione Artistica, Musicale o "
          "Coreutica)": "higher education",
          "Altro": "other"}
HEAD = re.compile(r"^(G\d\dQ\d\d)(?:\[(SQ\d+)\])?\. (.*)$", re.S)


def fetch() -> Path:
    p = RAW_DIR / "results-survey220905.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def code(col: str) -> str:
    q, sq, _ = HEAD.match(col).groups()
    return f"{q}_{sq}" if sq else q


def load() -> pd.DataFrame:
    d = pd.read_excel(fetch(), sheet_name=0)
    assert d.shape == (145, 104), d.shape
    return d


def stems(table: str) -> list:
    """(item code, question text, subquestion text) for a table, in column order."""
    q = TABLES[table]
    out = []
    for c in load().columns:
        m = HEAD.match(c)
        if m and m.group(1) == q:
            text = " ".join(m.group(3).split())
            stem, sub = re.match(r"^(.*?)\s*\[(.*)\]$", text).groups()
            out.append((code(c), stem, sub.strip()))
    return out


def options(question: str) -> dict:
    """resp -> option label for a question, from the Foglio1 codebook sheet."""
    f = pd.read_excel(fetch(), sheet_name="Foglio1", header=None)
    cols = [j for j in range(f.shape[1]) if str(f.iloc[0, j]).startswith(question)]
    labs = set()
    for j in cols:
        labs.add(tuple(" ".join(str(v).split()) for v in f.iloc[1:, j].dropna()))
    assert len(labs) == 1, labs
    out = {}
    for lab in labs.pop():
        k, txt = re.match(r"^(\d): (.*)$", lab).groups()
        out[int(k)] = txt
    return out


def main() -> None:
    d = load()
    assert d["id. ID risposta"].is_unique
    tables = {name: [c for c in d.columns if c.startswith(q + "[")]
              for name, q in TABLES.items()}
    for name, its in tables.items():
        assert len(its) == N_ITEMS[TABLES[name]], (name, len(its))
    items = [c for its in tables.values() for c in its]
    covsrc = {c: COVS[c.split(".")[0]] for c in d.columns if c.split(".")[0] in COVS}
    assert len(covsrc) == 3
    books = {}
    for c in d.columns:
        if c in items or c in covsrc or c == "id. ID risposta":
            continue
        q = HEAD.match(c).group(1) if HEAD.match(c) else c
        books[c] = ("submission date (administrative)" if c.startswith("submitdate")
                    else "multi-select checklist" if q in CHECKLISTS
                    else "single question, no shared construct")
    assert len(books) + len(items) + len(covsrc) + 1 == d.shape[1]
    for c, why in books.items():
        print(f"  [skip] {c[:60]}: {why}")
    d = d.rename(columns={"id. ID risposta": "id", **covsrc})
    d["cov_gender"] = d["cov_gender"].map(GENDER)
    d["cov_school"] = d["cov_school"].map(SCHOOL)
    d["cov_age"] = d["cov_age"].astype(str).str.strip().replace({">= 25 anni": "25+"})
    assert d[["cov_gender", "cov_school"]].notna().all().all()
    assert set(d["cov_age"]) <= {str(a) for a in range(18, 25)} | {"25+"}
    covs = ["cov_gender", "cov_age", "cov_school"]
    names = list(tables)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, its in tables.items():
        q = TABLES[name]
        assert sorted(options(q)) == [1, 2, 3, 4, 5]
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        t["item"] = t["item"].map(code)
        assert t["resp"].isin(range(1, 6)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert t["item"].nunique() == len(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(range(1, 6)) for i in t["item"].unique()}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
