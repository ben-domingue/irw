"""
Item text for hohn_2024_library_agreement.

Source: Hohn, A. (2024). answered questionnaire to a Bachelor Thesis on the
        Max Planck Institute for Evolutionary Anthropology library's resource
        discovery system [Dataset]. Zenodo. DOI 10.5281/zenodo.13269659,
        CC BY 4.0.

Everything here is PARSED from the CSV's column headers, not retyped. The
survey platform wrote each question into the header in full -- the shared stem,
then the statement in parentheses, then its own section marker "(Eigene
Kriterien)" -- so the file ties each item code to its wording directly. The
parsing shares `_split_header()` with data/hohn_2024_library_resources.py by
reimplementing the same balanced-parenthesis rule, and asserts the stem is
identical across the five items.

The questions are the library's own, so the deposit's CC BY is the wording's
licence and no third-party instrument is in play.

`option_text` is the four options the processing script maps, in its order:
4 "I agree", 3 "I rather agree", 2 "I rather disagree", 1 "I disagree". The
survey's fifth option, "I don't know", is deliberately absent from both the
response table and here -- it is not a point on the agreement scale, and
placing it among the four would assert an ordering the deposit never states.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pandas as pd

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])

TABLE = "hohn_2024_library_agreement"
STEM = "Please indicate how much you agree or disagree with the following"
SECTION_MARKER = "(Eigene Kriterien)"
FIELDS = ["table", "section_id", "item", "instrument", "instructions",
          "section_prompt", "item_text", "correct_response", "option_text",
          "resp"]
INSTRUMENT = ("Library resource-discovery agreement statements "
              "(study-authored), Hohn 2024")
OPTIONS = {4: "I agree", 3: "I rather agree",
           2: "I rather disagree", 1: "I disagree"}


def split_header(header: str):
    """(stem, item) with BALANCED parentheses -- see the processing script."""
    h = header.strip()
    assert h.endswith(SECTION_MARKER), h
    h = h[:-len(SECTION_MARKER)].rstrip()
    assert h.endswith(")"), h
    depth = 0
    for i in range(len(h) - 1, -1, -1):
        if h[i] == ")":
            depth += 1
        elif h[i] == "(":
            depth -= 1
            if depth == 0:
                return h[:i].strip(), h[i + 1:-1].strip()
    raise AssertionError(header)


def code(item: str) -> str:
    c = re.sub(r"[^a-z0-9]+", "_", item.lower())
    return re.sub(r"_+", "_", c).strip("_")[:40]


def main() -> None:
    df = pd.read_csv(SRC, sep=";", encoding="latin-1")
    cols = [c for c in df.columns if c.startswith(STEM)]
    assert len(cols) == 5, len(cols)

    parsed = [split_header(c) for c in cols]
    stems = {p[0] for p in parsed}
    assert len(stems) == 1, stems
    instructions = stems.pop()
    items = [p[1] for p in parsed]
    assert len(set(items)) == 5, items
    codes = [code(i) for i in items]
    assert len(set(codes)) == 5, codes
    print(f"parsed from the headers: shared stem {instructions!r}, "
          f"{len(items)} distinct statements")

    rows = []
    for c, text in zip(codes, items):
        for resp, opt in sorted(OPTIONS.items()):
            rows.append({
                "table": TABLE,
                "section_id": f"{TABLE}_1",
                "item": c,
                "instrument": INSTRUMENT,
                "instructions": instructions,
                "section_prompt": "",
                "item_text": text,
                "correct_response": "",
                "option_text": opt,
                "resp": resp,
            })
    path = OUT / f"{TABLE}__items.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{path}: {len(rows)} rows, 5 items x {len(OPTIONS)} options")


if __name__ == "__main__":
    main()
