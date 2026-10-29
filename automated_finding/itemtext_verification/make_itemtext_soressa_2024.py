"""
Item text for soressa_2024_dam_attitudes.

Source: Soressa, T. (2024). Local Community's Satisfaction, Attitude and
        Mitigation Measures Towards Dams [Dataset]. Harvard Dataverse.
        DOI 10.7910/DVN/2BD1HP, CC0 1.0.

Everything is read from the deposit's own SPSS labels, not retyped: each of the
31 variables carries a variable label that IS its full English wording, and
value labels giving all five anchors. The items are the study's own
dam-specific questions, so the deposit's CC0 is the wording's licence and no
third-party instrument is in play -- which is why this ships where most of this
batch's item text was held.

`item` is the lowercased source column name, exactly as
data/soressa_2024_dam_attitudes.py assigns it, so the tie is by name on both
sides and no position is involved.

The shared stem is NOT in the file. The labels are bare predicates ("Increases
employment opportunities", "Lose of forest areas") that plainly continued a
question the deposit does not record, so `instructions` and `section_prompt`
are left EMPTY rather than invented -- the standard's rule is to leave a field
blank rather than write wording nobody read.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import pyreadstat

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])

TABLE = "soressa_2024_dam_attitudes"
FIELDS = ["table", "section_id", "item", "instrument", "instructions",
          "section_prompt", "item_text", "correct_response", "option_text",
          "resp"]
INSTRUMENT = ("Local community attitudes to dams (study-authored), Soressa 2024")


def main() -> None:
    _df, meta = pyreadstat.read_sav(SRC)
    cols = list(meta.column_names_to_labels)
    assert len(cols) == 31, len(cols)

    stems = {c: (meta.column_names_to_labels[c] or "").strip() for c in cols}
    assert all(stems.values()) and len(set(stems.values())) == 31
    anchor_sets = {c: meta.variable_value_labels[c] for c in cols}
    one = anchor_sets[cols[0]]
    assert all(v == one for v in anchor_sets.values()), \
        "the 31 items do not share one anchor set"
    assert len(one) == 5, one

    rows = []
    for c in cols:
        for resp, text in sorted(one.items()):
            rows.append({
                "table": TABLE,
                "section_id": f"{TABLE}_1",
                "item": c.lower(),
                "instrument": INSTRUMENT,
                "instructions": "",
                "section_prompt": "",
                "item_text": stems[c],
                "correct_response": "",
                "option_text": text,
                "resp": int(resp),
            })
    path = OUT / f"{TABLE}__items.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{path}: {len(rows)} rows, {len(cols)} items x {len(one)} options")


if __name__ == "__main__":
    main()
