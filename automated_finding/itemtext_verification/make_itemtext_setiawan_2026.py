"""Build the three setiawan_2026_cybersecurity_* item text tables.

Source: CSLE_instrument_ID-EN.csv from Mendeley Data 10.17632/8mvkw9kjvp. It
has one row per item with `variable` naming the data column, `item_indonesian`
and `item_english` giving the wording, and `response_scale` spelling out the
anchors. Nothing here is positional: the tie between item code and stem is the
deposit's own `variable` column.

The administration was Indonesian (Google Forms, Riau and West Java), so the
base text fields carry the Indonesian and the `_translated` fields the
depositors' own English.

`option_text` is deliberately BLANK while `option_text_translated` is
populated. The deposit states the anchors only in English, inside
`response_scale` ("1 = strongly disagree, 2 = disagree, ..."); the Indonesian
labels respondents actually saw are not published anywhere in it. Blank is
what the standard asks for when the administered wording is not in hand --
the alternative would be to invent an Indonesian anchor or to pass the English
off as administered wording.

Usage:
  python3 make_itemtext_setiawan_2026.py <CSLE_instrument_ID-EN.csv> <outdir>
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

INSTR = Path(sys.argv[1])
OUT = Path(sys.argv[2])

INSTRUMENT = ("Cybersecurity Literacy of Educators (CSLE) questionnaire, "
              "Setiawan, Abdullah & Salam (2026) -- study-authored")

BLOCKS = {
    "KN": ("setiawan_2026_cybersecurity_knowledge",
           "Cybersecurity knowledge (CSK)"),
    "ET": ("setiawan_2026_cybersecurity_ethics",
           "Cybersecurity ethics (CSE)"),
    "BH": ("setiawan_2026_cybersecurity_behaviour",
           "Cybersecurity behaviour (CSB)"),
}

FIELDS = ["table", "section_id", "item", "instrument", "language",
          "instructions", "section_prompt", "item_text", "correct_response",
          "option_text", "resp",
          "instructions_translated", "section_prompt_translated",
          "item_text_translated", "option_text_translated"]


def anchors(response_scale: str) -> list[tuple[int, str]]:
    """Parse "1 = strongly disagree, 2 = disagree, ..." out of response_scale.

    The sentence that follows the anchor list ("Higher = greater ...") is cut
    off at the first full stop so it cannot be read as an anchor label.
    """
    head = response_scale.split(".")[0]
    pairs = re.findall(r"(\d+)\s*=\s*([^,]+)", head)
    out = [(int(n), label.strip()) for n, label in pairs]
    assert out, response_scale
    return out


def main() -> None:
    rows_by_block: dict[str, list[dict]] = {k: [] for k in BLOCKS}
    with INSTR.open(newline="", encoding="utf-8") as fh:
        src = list(csv.DictReader(fh))
    assert len(src) == 60, len(src)

    for row in src:
        code = row["variable"].strip()
        prefix = code[:2]
        assert prefix in BLOCKS, code
        table, subscale = BLOCKS[prefix]
        assert row["subscale"].strip() == subscale, (code, row["subscale"])
        opts = anchors(row["response_scale"])
        for resp, label in opts:
            rows_by_block[prefix].append({
                "table": table,
                "section_id": f"{table}_1",
                "item": code,
                "instrument": INSTRUMENT,
                "language": "Indonesian",
                "instructions": "",
                "section_prompt": "",
                "item_text": row["item_indonesian"].strip(),
                "correct_response": "",
                "option_text": "",
                "resp": resp,
                "instructions_translated": "",
                "section_prompt_translated": "",
                "item_text_translated": row["item_english"].strip(),
                "option_text_translated": label,
            })

    for prefix, (table, _) in BLOCKS.items():
        rows = rows_by_block[prefix]
        assert len({r["item"] for r in rows}) == 20, table
        path = OUT / f"{table}__items.csv"
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        print(f"{path.name}: {len(rows)} rows, "
              f"{len({r['item'] for r in rows})} items, "
              f"resp {sorted({r['resp'] for r in rows})}")


if __name__ == "__main__":
    main()
