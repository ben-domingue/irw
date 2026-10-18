#!/usr/bin/env python3
# Source: https://zenodo.org/records/18227290
# DOI: none recorded on the deposit (no related identifiers).
#   Bismo, A. (2026). "Questionnaire & RAW data 'Adoption of AR Virtual Try
#   On in E-commerce: UTAUT Evidence, Trust Mediation'." Zenodo.
# Data: Zenodo 18227290, "[RAW Data Collection] Adoption of AR Virtual Try On
#       in E-commerce.xlsx", sheet 'Sheet1' (250 respondents x 25 items;
#       Indonesian online cosmetics shoppers).
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# TWO HEADER ROWS, and both are used: row 0 carries the item CODES (X1.1 ..
#   X4.4, Z1-Z4, Y1-Y4) for the item columns and is blank over the
#   demographics; row 1 carries the Indonesian item STEMS and the
#   demographic headers. The file is read with header=0 so the codes become
#   the column names, and row 1 -- the stem row -- is then dropped from the
#   data (it is text, not a response). Read with header=1 instead, the codes
#   are lost and the columns become full sentences.
#
# Item text: NOT shipped, and as with the rest of this batch's Indonesian
#   deposits the text is in hand rather than missing: row 1 holds every stem,
#   aligned to row 0's code by column position within the same file, so the
#   mapping is the source's own. itemtext_standard.md requires the English in
#   the parallel _translated fields for a non-English administration; the
#   authors ship no English, so it would be IRW-generated and owes a
#   translation_source and a public issues-page callout. These are the
#   study's own UTAUT-framed items, so no register entry blocks them.
#
# Tables:
#   bismo_2026_ar_tryon  25 items, the source's own codes, 1-5. One table:
#       one matrix question, one response format. The X/Z/Y prefixes are the
#       study's exogenous/mediator/endogenous construct groups, so
#       multi_scale is expected.
#
# Dropped, with reasons:
#   the 11 unlabelled leading columns (timestamp, two screening questions,
#       age, gender, region, occupation, which e-commerce app, which product
#       type, and two more) -- screening and demographics; six become cov_*,
#       the rest are free-text or multi-select and are printed at run time.
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
DATA_URL = ("https://zenodo.org/api/records/18227290/files/"
            "%5BRAW%20Data%20Collection%5D%20Adoption%20of%20AR%20Virtual%20"
            "Try%20On%20in%20E-commerce.xlsx/content")
TABLE = "bismo_2026_ar_tryon"
ALLOWED = {1, 2, 3, 4, 5}
CODE_RE = re.compile(r"^(X\d\.\d|[ZY]\d)$")
# Row 1's demographic headers, matched by fragment -> covariate name.
COVFRAG = [("usia", "cov_age_band"), ("jenis kelamin", "cov_gender"),
           ("daerah tempat tinggal", "cov_region"), ("pekerjaan", "cov_occupation")]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    raw = io.BytesIO(r.content)
    d = pd.read_excel(raw, sheet_name="Sheet1", header=0)
    d.columns = [str(c).strip() for c in d.columns]
    stems = d.iloc[0]                      # row 1 of the file: the stem row
    d = d.iloc[1:].reset_index(drop=True)  # drop it from the data
    assert d.shape[0] == 250, d.shape

    items = [c for c in d.columns if CODE_RE.match(c)]
    assert len(items) == 25, (len(items), items)
    assert len(set(items)) == len(items)
    print(f"[items] {len(items)} codes from header row 0: "
          f"{', '.join(items[:6])} ...")

    covmap = {}
    for c in d.columns:
        if c in items:
            continue
        label = " ".join(str(stems.get(c, "")).split()).lower()
        for frag, name in COVFRAG:
            if frag in label and name not in covmap.values():
                covmap[c] = name
                break
    assert len(covmap) == 4, sorted(covmap.values())
    for c in d.columns:
        if c not in items and c not in covmap:
            print(f"[drop] {c} -> {' '.join(str(stems.get(c,''))[:58].split())}")
    print(f"[cols] {len(items)} items, {len(covmap)} covariates, "
          f"{len(d.columns) - len(items) - len(covmap)} dropped")

    d = d.rename(columns=covmap)
    d["id"] = range(1, len(d) + 1)
    cov_cols = sorted(set(covmap.values()))
    for c in cov_cols:
        d[c] = d[c].astype(str).str.strip().replace({"nan": pd.NA})

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
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
    assert long["item"].nunique() == 25

    checks = run_qc(long, permitted_values={c: ALLOWED for c in items})
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
