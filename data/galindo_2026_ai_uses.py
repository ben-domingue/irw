#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/ZA15RI
# DOI: 10.7910/DVN/ZA15RI (dataset; manuscript "Psychological Uses of Artificial
#   Intelligence in Adolescence: Scale Development, Cross-Cultural Invariance, and Links to
#   Loneliness and Emotional Intelligence" -- no DOI on the record)
#   Galindo Dominguez, Hector (2026), Harvard Dataverse.
# Data: DB-COMBINED.sav (file 13914855): 951 adolescents (Spain -- Basque- and Spanish-
#       language forms -- and Greece) x 107 columns. "DATASET OVERVIEW AND VARIABLE
#       STRUCTURE.docx" (file 13914854) describes the blocks. Variable labels carry each
#       item's code and Spanish wording (e.g. "SS01 Mi familia realmente trata de
#       ayudarme."); no value labels on the items.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Levels checked: .sav variable labels hold the Spanish wording
#   for every item (cheap: data_labels); value labels absent on the items, so the 1-5
#   anchors are not in the deposit. Not built here because 58% of respondents answered the
#   Basque form and 31% the Greek form, neither of which is deposited, and the English
#   _translated columns would be IRW-generated -- left for a later pass.
#
# Tables (item code = the code that opens each header and label, e.g. MPUAI01, MPUAI5,
#   SS01; all 1-5):
#   galindo_2026_mpu_ai          MPUAI01-24  psychological uses of AI (the authors' new
#                                            scale: emotional, relational, academic,
#                                            substitution uses)
#   galindo_2026_social_support  SS01-08     family and friend support
#   galindo_2026_emotional_intel EI01-16     emotional intelligence (self-appraisal,
#                                            others' appraisal, use, regulation)
#   galindo_2026_personality     PE01-10     ten-item personality descriptors
#   galindo_2026_suicidal_ideation SI01-04
#   galindo_2026_loneliness      LN01-03
#   galindo_2026_bullying        BL01-05     victimisation
#   galindo_2026_sexting         SX01-09
#   galindo_2026_grooming        GR01-08     contact with online strangers
# Skipped: the timestamp (date only); consent text (used only to recover the form
#   language); school name (free text); the six open-ended QU answers (free text); the
#   single item HPN01 ("En general te sientes feliz?"); factor and total scores (F1-F4,
#   EI_TT, LN_TT). Two rows that duplicate another row on every column, free text
#   included, are dropped as double submissions.
# Covariates: cov_form_language (Basque / Spanish / Greek, from the language the consent
#   statement was shown in; Idioma codes only Spanish vs Greek), cov_age (as typed; a few
#   implausible values such as 2 and 54 are kept as recorded), cov_gender (female / male /
#   non-binary, mapped from Basque, Spanish and Greek labels), cov_grade (as typed).
# id = row order after dropping the duplicates.

import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "galindo_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/13914855?format=original"

TABLES = {"galindo_2026_mpu_ai": "MPUAI", "galindo_2026_social_support": "SS",
          "galindo_2026_emotional_intel": "EI", "galindo_2026_personality": "PE",
          "galindo_2026_suicidal_ideation": "SI", "galindo_2026_loneliness": "LN",
          "galindo_2026_bullying": "BL", "galindo_2026_sexting": "SX",
          "galindo_2026_grooming": "GR"}
COUNTS = {"MPUAI": 24, "SS": 8, "EI": 16, "PE": 10, "SI": 4, "LN": 3, "BL": 5, "SX": 9, "GR": 8}
GENDER = {"Emakumezkoa": "female", "Femenino": "female", "Κορίτσι": "female",
          "Gizonezkoa": "male", "Masculino": "male", "Αγόρι": "male",
          "Ez binarioa": "non-binary"}


def fetch() -> Path:
    p = RAW_DIR / "data.sav"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def form_language(s: str) -> str:
    if s.startswith("Parte hartzeko"):
        return "Basque"
    if s.startswith("He leído"):
        return "Spanish"
    if s.startswith("Έχω"):
        return "Greek"
    raise ValueError(s)


def main() -> None:
    d, meta = pyreadstat.read_sav(fetch())
    assert d.shape == (951, 107), d.shape
    cols = {}
    for name, pre in TABLES.items():
        cs = [c for c in d.columns if re.match(rf"^{pre}\d+", c)]
        assert len(cs) == COUNTS[pre], (pre, len(cs))
        cols[name] = cs
    code = {c: re.match(r"^[A-Z]+\d+", c).group(0) for v in cols.values() for c in v}
    assert len(set(code.values())) == len(code)
    for c, k in code.items():  # each label opens with the same code
        assert re.sub(r"[\s-]", "", meta.column_names_to_labels[c]).startswith(k), c
    other = [c for c in d.columns if c not in code]
    print(f"  skip/cov {len(other)} columns: {other[:7]} ... QU*, HPN01, F1-F4, EI_TT, LN_TT")
    nd = d.duplicated().sum()
    d = d[~d.duplicated()].reset_index(drop=True)
    print(f"  dropped {nd} exact duplicate rows")
    d.insert(0, "id", d.index + 1)
    d["cov_form_language"] = d["Términosycondiciones"].map(form_language)
    d["cov_age"] = d["Edadsoloelnúmero"]
    d["cov_gender"] = d["Género"].map(GENDER)
    d["cov_grade"] = d["Curso"].str.strip()
    assert d["cov_gender"].notna().all()
    covs = ["cov_form_language", "cov_age", "cov_gender", "cov_grade"]
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, cs in cols.items():
        t = d[["id"] + covs + cs].rename(columns=code).melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(range(1, 6)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {code[c]: set(range(1, 6)) for c in cs}
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
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
