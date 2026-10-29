"""
Item text for teriba_2026_self_compassion.

Source: Teriba, A. (2026). Psychological Well-Being and Sport Satisfaction
        [Dataset]. Harvard Dataverse. DOI 10.7910/DVN/IQSSOU, CC0 1.0.

ONLY the self-compassion block of this six-instrument deposit ships. The
instrument is the Self-Compassion Scale Short Form (SCS-SF, 12 items; Raes,
Pommier, Neff & Van Gucht 2011), identified from the stems themselves -- six of
the twelve match the register's own `match_item_text` fragments verbatim
("become consumed by feelings of inadequacy", "try to see my failings as part of
the human condition", "give myself the caring and tenderness I need", "tend to
obsess and fixate on everything", "disapproving and judgmental about my own
flaws", "tend to feel alone in my failure") -- and it is registered **ship**:
irw#2381 rights bank R03, Neff's own information PDF granting use "for any
purpose whatsoever". The administration here is English, which is what that row
covers.

The other five instruments in the same file are NOT shipped and are not open
questions: WHO-5, Grit-S and the ERQ are registered `block`, Dweck's ITIS is
`hold`, and the 16-item sport-satisfaction battery has no register row at all.

Mapping basis: `data_labels`. Each item's SPSS variable label is the shared
instruction followed by " - " and then the item's own wording, so the source
file ties code to text directly; this script splits on that separator rather
than restating any stem. Item codes are the lowercased source column names,
exactly as data/teriba_2026_sport_satisfaction.py assigns them.

The response anchors come from the same file's value labels, which read
"Almost never 1", "2", "3", "4", "Almost always 5". The numerals are the scale
points echoed back, not wording, so option_text ships "Almost never" and
"Almost always" with the trailing numeral stripped and BLANK for the three
unlabelled midpoints -- padding an unlabelled point with its own number is what
audit_batch.R warns about.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pyreadstat

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])

TABLE = "teriba_2026_self_compassion"
COLS = [f"Self_compassion_{i}" for i in range(1, 13)]
FIELDS = ["table", "section_id", "item", "instrument", "instructions",
          "section_prompt", "item_text", "correct_response", "option_text",
          "resp"]
INSTRUMENT = ("Self-Compassion Scale Short Form (SCS-SF), Raes, Pommier, Neff "
              "& Van Gucht 2011")
SEP = " - "

# Register fragments that must appear among the stems, so the identification is
# checked rather than asserted.
EXPECTED = [
    "become consumed by feelings of inadequacy",
    "try to see my failings as part of the human condition",
    "give myself the caring and tenderness i need",
    "tend to obsess and fixate on everything",
    "disapproving and judgmental about my own flaws",
    "tend to feel alone in my failure",
]


def anchor(text: str) -> str:
    """Strip the echoed scale point; a bare numeral means unlabelled."""
    stripped = re.sub(r"\s*\d+\s*$", "", text).strip()
    return "" if not stripped or stripped.isdigit() else stripped


def main() -> None:
    _df, meta = pyreadstat.read_sav(SRC)
    labels = {c: meta.column_names_to_labels[c] for c in COLS}
    options = {c: meta.variable_value_labels[c] for c in COLS}

    instructions = set()
    stems = {}
    for c in COLS:
        head, sep, tail = labels[c].partition(SEP)
        assert sep and tail.strip(), (c, labels[c])
        instructions.add(head.strip())
        stems[c] = tail.strip()
    assert len(instructions) == 1, instructions
    instruction = instructions.pop()
    assert len(set(stems.values())) == 12, stems

    joined = " | ".join(stems.values()).lower()
    missing = [f for f in EXPECTED if f not in joined]
    assert not missing, f"stems do not match the SCS-SF register row: {missing}"
    print(f"identification checked: {len(EXPECTED)} of the register's "
          "match_item_text fragments appear verbatim in these 12 stems")

    # Every item must offer the same anchors, which is what makes one shared
    # option set correct.
    assert len({tuple(sorted(v.items())) for v in options.values()}) == 1

    rows = []
    for c in COLS:
        for resp, text in sorted(options[c].items()):
            rows.append({
                "table": TABLE,
                "section_id": f"{TABLE}_1",
                "item": c.lower(),
                "instrument": INSTRUMENT,
                "instructions": instruction,
                "section_prompt": "",
                "item_text": stems[c],
                "correct_response": "",
                "option_text": anchor(text),
                "resp": int(resp),
            })
    path = OUT / f"{TABLE}__items.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    blank = sum(1 for r in rows if not r["option_text"])
    print(f"{path}: {len(rows)} rows, 12 items x 5 options "
          f"({blank} option_text blank -- the unlabelled midpoints)")


if __name__ == "__main__":
    main()
