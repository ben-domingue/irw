#!/usr/bin/env python3
# Source: https://osf.io/2sxub/
# DOI: none minted by the OSF node (the component has no DOI; cite the node URL)
#   Jansseune, L., Weyn, S. & Bijttebier, P. "Beyond Broad Traits: A Nuanced,
#   Facet-Level Personality Profile of Sensory Processing Sensitivity." OSF project
#   2sxub (public node, contributors in that order).
# Data: "SPSQ_NEO_Data_2024.csv" (osfstorage, osf.io/download/vwmu2/) -- a two-tier
#       header file: row 1 holds the broad domain names (Data / Personality /
#       Sensitivity), row 2 the actual variable names, rows 3-338 the N=336
#       participants. Read with header=1. Columns: age, gender, education, P1-P240
#       (NEO-PI-3, 1-5), S1-S43 (Sensory Processing Sensitivity Questionnaire, 1-7).
#       The deposit's README.md documents exactly this layout and sample size.
# License: CC0 1.0 Universal -- the OSF node reports license object
#          563c1cf88c5e4a3877f9e96c, resolved via
#          https://api.osf.io/v2/licenses/563c1cf88c5e4a3877f9e96c/ to "CC0 1.0
#          Universal"; the node is public (`public: true`).
#
# Item text: not shipped. The CSV carries no labels of any kind (it is a plain CSV, so
#   there is no variable-label or value-label level to check), and the headers are
#   positional codes P1-P240 / S1-S43. The README is a scoring guide and does not
#   reproduce any stem. Where the text actually is: the NEO-PI-3 item wording is
#   proprietary (PAR / Costa & McCrae) and the SPSQ wording is in its own publication
#   (Weyn et al.) -- both a hop outside this deposit.
#
# Item codes: the source headers P1-P240 and S1-S43 are kept verbatim as `item`.
# Tables:
#   jansseune_2024_neo_pi3  240 items, 1-5
#   jansseune_2024_spsq      43 items, 1-7
# id: the file carries no respondent identifier, so id is the 1-based row index; it
#   links a participant across the two tables.
from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s3"
URL = "https://osf.io/download/vwmu2/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COVS = {"age": "cov_age", "gender": "cov_gender", "education": "cov_education"}


def screen_for_pii(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"[pii] examined {df.shape[1]} columns, {len(text_cols)} of them string-typed")
    assert df.shape[1] > 0 and len(text_cols) > 0
    pats = {
        "email": r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}",
        "phone": r"\+?\d[\d \-()]{8,}",
        "postal": r"^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$",
        "ip": r"^\d{1,3}(\.\d{1,3}){3}$",
        "date": r"\d{1,4}[/-]\d{1,2}[/-]\d{1,4}",
    }
    hits = [(c, k) for c in text_cols for k, p in pats.items()
            if df[c].dropna().astype(str).str.contains(p, regex=True, na=False).any()]
    assert not hits, hits
    print(f"[pii] string columns are {text_cols}: closed category labels, no identifiers")


def emit(name: str, t: pd.DataFrame, pv: list) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    assert not t.duplicated(["id", "item"]).any(), name
    assert t["id"].nunique() >= 100 and t["item"].nunique() >= 3, name
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {name} {c.name}: {c.detail[:160]}")
    rep = irw_validate.validate_frame(t, label=name, profile="upload",
                                      context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, (name, [(f.check, f.message) for f in rep.errors])
    for f in rep.warnings:
        print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
          f"resp={t['resp'].min():g}-{t['resp'].max():g}")


def convert() -> None:
    r = requests.get(URL, headers=UA, timeout=300)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content), header=1, low_memory=False)
    assert df.shape == (336, 286), df.shape
    screen_for_pii(df)

    df.insert(0, "id", range(1, len(df) + 1))
    df = df.rename(columns=COVS)
    cov_cols = list(COVS.values())

    blocks = {
        "jansseune_2024_neo_pi3": ([f"P{k}" for k in range(1, 241)], [1, 2, 3, 4, 5]),
        "jansseune_2024_spsq": ([f"S{k}" for k in range(1, 44)], [1, 2, 3, 4, 5, 6, 7]),
    }
    accounted = set(cov_cols)
    tables = {}
    for name, (cols, pv) in blocks.items():
        assert all(c in df.columns for c in cols), name
        accounted |= set(cols)
        long = df[["id"] + cov_cols + cols].melt(
            id_vars=["id"] + cov_cols, value_vars=cols,
            var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        # Likert columns must be whole scale points: a fractional value here would be
        # an imputation, not a response.
        assert (long["resp"] % 1 == 0).all(), name
        long = long[["id", "item", "resp"] + cov_cols].reset_index(drop=True)
        tables[name] = (long, pv)

    leftover = [c for c in df.columns if c not in accounted and c != "id"]
    assert not leftover, f"unaccounted source columns: {leftover}"
    print(f"[books] {len(accounted)} source columns accounted for "
          f"(3 covariates + 283 items), 0 skipped")

    assert len(set(tables)) == len(tables)
    for name, (t, pv) in tables.items():
        emit(name, t, pv)


if __name__ == "__main__":
    convert()
