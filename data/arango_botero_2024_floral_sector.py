#!/usr/bin/env python3
# Source: https://zenodo.org/records/10535997
# DOI: none recorded on the deposit (no related identifiers, empty
#   description).
#   Arango-Botero, D., Franco-Castaño, S., Quintero Idárraga, S., et al.
#   (2024). "Multifactorial assessment of job satisfaction in the floral
#   sector: Examining Stress, Burnout, Emotional Intelligence, and
#   Motivation." Zenodo.
# Data: Zenodo 10535997, "Encuestas.xlsx", sheet 'Sábana' (1272 rows x 90
#       columns; flower-growing workers in 23 municipalities of Antioquia,
#       Colombia).
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# Item text: NOT shipped, and the reason is the deposit rather than the
#   rights. The record holds exactly one file, this spreadsheet; it ships no
#   codebook, no questionnaire and an empty description, and .xlsx carries
#   neither a variable-label nor a value-label level. So the headers are all
#   there is, and they are bare question numbers ("P7.FU1", "P4.3"). The
#   wording is in the authors' unpublished instrument -- there is no paper
#   DOI on the record to chase it through. That is where the text is.
#
# BLOCK NOTE: the 67 P7 columns carry 15 undocumented subscale prefixes --
#   FU 6, UP 6, A 4, NS 3, APR 5, C 3, VPC 3, VPE 5, VPV 4, VPS 4, CP 3,
#   IN 6, SP 6, CFP 4, IU 5. The title names four constructs (stress,
#   burnout, emotional intelligence, motivation), so these prefixes are
#   subscales of several instruments, but nothing in the deposit says which
#   prefix belongs to which. They are therefore carried verbatim as the item
#   codes and shipped as ONE table: P7 is one matrix question on one 1-5
#   response format, and splitting it 15 ways would assert a construct
#   boundary the source does not document (ben-domingue 2026-10-15, on the
#   16 opaque-block tables: they ship as-is). run_qc's multi_scale warning
#   is expected here and is the reason for this note.
#
# Tables:
#   arango_botero_2024_floral_sector   67 items, prefix P7 stripped, 1-5.
#   arango_botero_2024_financial_access  10 items, codes P4.1-P4.10 kept
#       whole, 1-5, a separate matrix question earlier in the survey. The
#       P4. prefix is NOT stripped: without it the codes would be the bare
#       numbers 1-10, which identify nothing.
#
# DATA-ENTRY ERRORS: four cells hold a doubled digit -- P7.FU4 = 44,
#   P7.APR2 = 24, P7.VPS2 = 32, P4.7 = 13 -- each a single cell in an
#   otherwise strict 1-5 item. They are dropped rather than repaired to
#   4/2/3/1: the intended value is a guess, and one isolated implausible
#   value in a single item is the signature of a typo, not of a wider code
#   (memory: feedback_resp_error_diagnostic). P4.10 reaches 6 in exactly one
#   cell while every other P4 item stops at 5, which is the same one-cell
#   signature, so it is dropped on the same rule; every dropped cell is
#   printed at run time.
#
# Dropped, with reasons:
#   '#'        row number -> becomes `id`
#   P6         free text, 620 distinct reasons for not holding a bank card
#   P1,P2,P3,P5  four single standalone questions, not a block
#   Municipio, D1-D6  -> cov_*
# id: the file's own '#' column (1..1272).
# Covariates: cov_municipality (text), cov_d1..cov_d6 (the deposit's
#   demographic block, codes carried as given -- it names none of them).

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
DATA_URL = ("https://zenodo.org/api/records/10535997/files/"
            "Encuestas.xlsx/content")
ALLOWED = {1, 2, 3, 4, 5}
DCOVS = [f"D{i}" for i in range(1, 7)]
SINGLES = ["P1", "P2", "P3", "P5"]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), sheet_name="Sábana")
    assert d.shape == (1272, 90), d.shape
    cols = [str(c) for c in d.columns]
    d.columns = cols

    p7 = [c for c in cols if c.startswith("P7.")]
    p4 = [c for c in cols if re.fullmatch(r"P4\.\d+", c)]
    assert len(p7) == 67 and len(p4) == 10, (len(p7), len(p4))

    # Balance the books.
    known = set(p7) | set(p4) | set(DCOVS) | set(SINGLES) | {"#", "P6",
                                                             "Municipio"}
    assert set(cols) == known, set(cols) ^ known
    for c in ["#", "P6"] + SINGLES:
        print(f"[drop] {c}")
    print(f"[cols] {len(p7)} P7 items + {len(p4)} P4 items, "
          f"{1 + len(DCOVS)} covariates, {2 + len(SINGLES)} dropped")

    assert d["#"].is_unique and d["#"].notna().all()
    d = d.rename(columns={"#": "id", "Municipio": "cov_municipality"})
    d["cov_municipality"] = d["cov_municipality"].ffill().astype(str).str.strip()
    for c in DCOVS:
        d["cov_" + c.lower()] = pd.to_numeric(d[c], errors="coerce").astype("Int64")
    cov_cols = ["cov_municipality"] + ["cov_" + c.lower() for c in DCOVS]

    def build(table, items, strip):
        sub = d[["id"] + cov_cols + items].copy()
        ren = {c: re.sub(strip, "", c) for c in items}
        assert len(set(ren.values())) == len(items), "item code collision"
        sub = sub.rename(columns=ren)
        names = [ren[c] for c in items]
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=names,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        bad = long["resp"].notna() & ~long["resp"].isin(ALLOWED)
        if bad.any():
            for it, g in long[bad].groupby("item"):
                print(f"  [typo] {table}: {it} drops "
                      f"{sorted(set(g['resp']))} ({len(g)} cell(s))")
            long = long[~bad]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["item"].nunique() == len(items)
        checks = run_qc(long, permitted_values={n: ALLOWED for n in names})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [warn] {table}: {c.name}: {c.detail[:120]}")
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")
        return len(long)

    t = 0
    t += build("arango_botero_2024_floral_sector", p7, r"^P7\.")
    t += build("arango_botero_2024_financial_access", p4, r"(?!)")
    print(f"[total] {t} responses across 2 tables")


if __name__ == "__main__":
    main()
