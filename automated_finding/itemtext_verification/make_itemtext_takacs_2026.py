#!/usr/bin/env python3
"""Item text for takacs_2026_{aces,phq9,gad7,maas} (figshare 10.6084/m9.figshare.32104447).

Cheap case: the deposit's Codebook.docx is one table with a row per variable --
wording | SPSS name | coding | scale type. data/takacs_2026_aces.py keeps the SPSS
names (ACE1, PHQ1, ...) as `item`, so each row ties wording to code by name. Wording
and option labels are taken verbatim (internal line breaks joined with a space;
the codebook's own numbering such as "1. " on ACE items kept; "Nearly every day" etc.
as written). The codebook's typo "adultsin" (ACE5) is kept.

Language: the participants were Hungarian-speaking and the Hungarian wording is not
in the deposit or its record; the codebook's English is the only wording available,
so this is the documented fallback -- English in the base fields, language =
Hungarian, no _translated columns, text_source = translated_substitute,
translation_source = study_supplied (the depositors' own codebook).
takacs_2026_cdrisc10 is not built: CD-RISC is blocked in the rights register.
"""
import csv
import re
from pathlib import Path

import docx
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
RAW = HERE / "runs" / "raw" / "takacs_2026" / "Codebook.docx"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
TABLES = {"ACE": ("takacs_2026_aces", "Adverse Childhood Experience Questionnaire for Adults"),
          "PHQ": ("takacs_2026_phq9", "Patient Health Questionnaire (PHQ-9)"),
          "GAD": ("takacs_2026_gad7", "Generalized Anxiety Disorder Scale (GAD-7)"),
          "MAAS": ("takacs_2026_maas", "The Mindful Attention Awareness Scale (MAAS)")}
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp"]


def norm(s):
    return " ".join(s.replace("\n", " ").split())


def options(cell):
    """Coding cells come as "0 = Not at all\n1 = ..." or "Yes = 1\nNo = 2"."""
    out = {}
    for part in re.split(r"[\n;]", cell):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"(\d+)\s*=\s*(.+)", part) or re.fullmatch(r"(.+?)\s*=\s*(\d+)", part)
        assert m, part
        a, b = m.groups()
        k, lab = (a, b) if a.isdigit() else (b, a)
        out[int(k)] = norm(lab)
    return out


def main():
    rows = [[c.text for c in r.cells] for t in docx.Document(str(RAW)).tables for r in t.rows]
    cb = {norm(r[1]): (norm(r[0]), r[2]) for r in rows[1:] if norm(r[1])}
    for pre, (table, instrument) in TABLES.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        items = sorted(resp["item"].unique(), key=lambda s: int(s[len(pre):]))
        out = []
        for it in items:
            text, coding = cb[it]
            opts = options(coding)
            assert set(resp.loc[resp["item"] == it, "resp"]) <= set(opts), (it, opts)
            for k, lab in sorted(opts.items()):
                out.append({"table": table, "section_id": f"{table}_1", "item": it,
                            "instrument": instrument, "language": "Hungarian",
                            "instructions": "", "section_prompt": "", "item_text": text,
                            "correct_response": "", "option_text": lab, "resp": k})
        assert {r["item"] for r in out} == set(resp["item"])
        p = OUT_DIR / f"{table}__items.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(out)
        print(f"{p.name}: {len(out)} rows; options {sorted({(r['resp'], r['option_text']) for r in out})}")


if __name__ == "__main__":
    main()
