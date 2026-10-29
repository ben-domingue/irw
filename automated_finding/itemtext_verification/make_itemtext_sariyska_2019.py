"""
Item text for sariyska_2019_food_frequency.

Source: Sariyska, R., Markett, S., Lachmann, B., & Montag, C. (2019). Frontiers
        in Psychology 10:2591. Data: 10.3389/fpsyg.2019.02591.s001, CC BY 4.0.

Only the food-frequency block ships. The same workbook's SD3 block is the Short
Dark Triad reproduced verbatim and is HELD -- see the register row this batch
wrote for it. These ten items are the study's own dietary questions, so they are
study-authored material under the deposit's CC BY.

Everything here is PARSED from the workbook's "Variable description" sheet
rather than retyped: that sheet is a real codebook with three columns --
variable name, label, and the value list -- so the file ties each item code to
its wording and its anchors directly. Two details of its shape that the parser
handles explicitly rather than around:

  * The shared stem appears ONCE, on the first item of the block: EBQ_03's label
    is "How many times per week do you consume the following products (on
    average)? honey", and EBQ_04..EBQ_12's labels are the bare food name. So the
    stem is split off the first label and becomes `instructions` (it applies to
    every item in the table), and `item_text` is the food name for all ten --
    including EBQ_03, whose name is what is left after the stem.
  * The anchors are given as one `1 = "never", 2 = "once", ...` string, parsed
    into the seven option rows. They are identical across the ten items, which
    the script asserts.

`item` is the lowercased source column name, exactly as
data/sariyska_2019_dark_triad.py assigns it.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pandas as pd

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])

TABLE = "sariyska_2019_food_frequency"
COLS = [f"EBQ_{i:02d}" for i in range(3, 13)]
FIELDS = ["table", "section_id", "item", "instrument", "instructions",
          "section_prompt", "item_text", "correct_response", "option_text",
          "resp"]
INSTRUMENT = ("Food-frequency questions (study-authored), Sariyska, Markett, "
              "Lachmann & Montag 2019")
# The stem ends at the question mark; what follows on that first label is the
# first item's own name.
STEM_RE = re.compile(r"^(.*\?)\s*(.*)$", re.S)
VALUE_RE = re.compile(r'(\d+)\s*=\s*"([^"]*)"')


def main() -> None:
    book = pd.read_excel(SRC, sheet_name="Variable description", header=None)
    # The codebook's three columns are name / label / values, under a header row.
    desc = {}
    for _i, row in book.iterrows():
        name = str(row[0]).strip()
        if name in COLS:
            desc[name] = (str(row[1]).strip(), str(row[2]).strip())
    assert set(desc) == set(COLS), sorted(set(COLS) - set(desc))

    first_label, first_values = desc[COLS[0]]
    m = STEM_RE.match(first_label)
    assert m, first_label
    instructions, first_item = m.group(1).strip(), m.group(2).strip()
    assert instructions.endswith("?") and first_item, (instructions, first_item)

    stems = {COLS[0]: first_item}
    for c in COLS[1:]:
        label, _v = desc[c]
        assert "?" not in label, (c, label)   # only the first carries the stem
        stems[c] = label
    assert len(set(stems.values())) == len(COLS), stems

    options = dict(VALUE_RE.findall(first_values))
    assert len(options) == 7, options
    for c in COLS:
        assert dict(VALUE_RE.findall(desc[c][1])) == options, c
    print(f"parsed from the codebook sheet: shared stem {instructions!r}, "
          f"{len(stems)} item names, {len(options)} identical anchors")

    rows = []
    for c in COLS:
        for resp, text in sorted(options.items(), key=lambda kv: int(kv[0])):
            rows.append({
                "table": TABLE,
                "section_id": f"{TABLE}_1",
                "item": c.lower(),
                "instrument": INSTRUMENT,
                "instructions": instructions,
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
    print(f"{path}: {len(rows)} rows, {len(COLS)} items x {len(options)} options")


if __name__ == "__main__":
    main()
