#!/usr/bin/env python3
"""Item text for the six reinhardt_2023_* tables (OSF hmnpt, Unipark .sav exports, English MTurk administration).
Stems = variable labels, anchors = value labels; item codes are the export's column names (data/reinhardt_2023_counterfeit.py
keeps them). Value labels of the form "2" (a bare scale number) are an unlabeled point and ship blank; "1 (strongly
disagree)" ships as the anchor text without its number. Study 2's file carries labels for every shipped item; the
pooled HH / counterfeit tables take their labels from Study 2 (identical wording to Study 1, checked)."""
import re
import pyreadstat
from _itemtext_writer_c import HERE, row, write, load_script

RAW = HERE / "runs" / "raw" / "osf_hmnpt"
mod = load_script("reinhardt_2023_counterfeit")
TABLES = {"reinhardt_2023_honesty_humility": (mod.HH, "HEXACO Honesty-Humility, 16 agreement items"),
          "reinhardt_2023_counterfeit_attitude": (mod.CF, "Attitude toward counterfeit luxury brands, 15 agreement items"),
          "reinhardt_2023_self_concept_clarity": (mod.SCC, "Self-Concept Clarity Scale, 12 agreement items"),
          "reinhardt_2023_risk_aversion": (mod.RISK, "Risk aversion, 6 agreement items"),
          "reinhardt_2023_materialism": (mod.MAT, "Materialism, 7 agreement items"),
          "reinhardt_2023_integrity": (mod.INT, "Integrity / rule-following, 7 agreement items")}


def anchor(label: str) -> str:
    label = label.strip()
    if re.fullmatch(r"\d+", label):
        return ""
    m = re.fullmatch(r"\d+\s*\((.*)\)", label)
    return m.group(1).strip() if m else label


def main():
    d1, m1 = pyreadstat.read_sav(str(RAW / "Study 1_Raw.sav"))
    d2, m2 = pyreadstat.read_sav(str(RAW / "Study 2_Raw.sav"))
    for c in mod.HH + mod.CF:
        assert m1.column_names_to_labels[c] == m2.column_names_to_labels[c], c
    for table, (items, instrument) in TABLES.items():
        rows = []
        for c in items:
            stem = m2.column_names_to_labels[c].replace("^", "'").strip()
            vl = m2.variable_value_labels[c]
            for r in sorted(vl):
                rows.append(row(table, f"{table}_1", c, instrument, "eng", int(r), stem, option_text=anchor(vl[r])))
        write(table, rows)


if __name__ == "__main__":
    main()
