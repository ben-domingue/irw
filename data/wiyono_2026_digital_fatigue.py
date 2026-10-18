#!/usr/bin/env python3
# Source: https://zenodo.org/records/21408658
# DOI: none recorded on the deposit (no related identifiers).
#   Wiyono, K. W., Linardi, W., & Pujianto, R. S. (2026). "Digital Fatigue
#   Questionnaire Responses." Zenodo.
# Data: Zenodo 21408658, "Digital Fatigue Questionnaire (Responses).xlsx",
#       sheet 'Form Responses 1' (211 rows x 29 columns; Indonesian
#       university students using online learning platforms).
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# Item text: NOT shipped, and the text is fully in hand -- the Google Form
#   export's headers are "(OP1)\nSaya menggunakan berbagai platform digital
#   ...", i.e. the item CODE and the item STEM in one cell, so the
#   code-to-wording tie is the source's own and a later pass can split it on
#   the newline. What stops it here is the schema: the administration is
#   Indonesian, itemtext_standard.md requires the English in the parallel
#   _translated fields, the authors ship no English, and an IRW-generated
#   translation owes a translation_source plus a public issues-page callout.
#   Eight deposits in this batch sit in that same position and belong in one
#   deliberate translation round. These are the authors' own
#   technostress/fatigue items, not a named third-party instrument, so no
#   register entry blocks them.
#
# SCALE: 1-6. Every item uses all six codes, so this is a six-point
#   agreement scale, not a 1-5 with a stray value.
#
# Tables:
#   wiyono_2026_digital_fatigue  21 items, the source's own codes -- OP1-OP5
#       (overload of platforms), TO1-TO5 (technology overload), TS1-TS5
#       (technostress), DF1-DF6 (digital fatigue), 1-6. One table: one
#       matrix question, one response format; the four prefixes are the
#       study's constructs, so multi_scale is expected.
#
# Dropped, with reasons:
#   Timestamp                      submission time, not a response
#   "Jumlah Platform Digital ..."  count of platforms used -> cov_*
#   "Rata Rata Waktu ..."          average daily time -> cov_*
#   Jenis Kelamin, Usia, Universitas, Fakultas, Domisili -> cov_*
# id: row index + 1 (the export carries no respondent identifier).

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = ("https://zenodo.org/api/records/21408658/files/"
            "Digital%20Fatigue%20Questionnaire%20%28Responses%29.xlsx/content")
TABLE = "wiyono_2026_digital_fatigue"
ALLOWED = {1, 2, 3, 4, 5, 6}
CODE_RE = re.compile(r"^\(\s*(OP|TO|TS|DF)\s*(\d{1,2})\s*\)")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), sheet_name="Form Responses 1")
    d.columns = [str(c) for c in d.columns]
    assert d.shape == (211, 29), d.shape

    ren = {}
    for c in d.columns:
        mm = CODE_RE.match(c.strip())
        if mm:
            ren[c] = f"{mm.group(1)}{int(mm.group(2))}"
    assert len(set(ren.values())) == len(ren), "item code collision"
    assert len(ren) == 21, sorted(ren.values())

    covmap = {}
    for c in d.columns:
        k = " ".join(c.split()).lower()
        for frag, name in (("jenis kelamin", "cov_gender"),
                           ("usia", "cov_age_band"),
                           ("universitas", "cov_university"),
                           ("fakultas", "cov_faculty"),
                           ("domisili", "cov_domicile"),
                           ("jumlah platform", "cov_n_platforms"),
                           ("rata rata waktu", "cov_daily_time_band")):
            if c not in ren and frag in k and c not in covmap:
                covmap[c] = name
                break
    known = set(ren) | set(covmap)
    for c in d.columns:
        if c not in known:
            print(f"[drop] {' '.join(c.split())[:66]}")
    print(f"[cols] {len(ren)} items, {len(covmap)} covariates, "
          f"{len(d.columns) - len(known)} dropped")
    assert len(covmap) == 7, sorted(covmap.values())

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns={**ren, **covmap})
    codes = sorted(ren.values(),
                   key=lambda c: (re.match(r"[A-Z]+", c).group(),
                                  int(re.search(r"\d+", c).group())))
    cov_cols = sorted(set(covmap.values()))
    for c in cov_cols:
        d[c] = d[c].astype(str).str.strip().replace({"nan": pd.NA})

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=codes,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - ALLOWED
        assert not bad, (it, bad)
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["item"].nunique() == 21

    checks = run_qc(long, permitted_values={c: ALLOWED for c in codes})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {c.name}: {c.detail[:130]}")
    (OUT_DIR / f"{TABLE}.csv").write_text(long.to_csv(index=False))
    print(f"[write] {TABLE}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
