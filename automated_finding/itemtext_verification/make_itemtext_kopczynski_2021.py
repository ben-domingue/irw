"""
Item text for three of the five kopczynski_2021_* tables.

Source: Kopczynski, T., & Bartoszek, A. (2021). COVID-19 anxiety versus
        well-being - students' sense of support and self-esteem [Dataset].
        Zenodo. DOI 10.5281/zenodo.5506610, CC BY 4.0.

Everything here is PARSED from the `.sav`'s own metadata, not retyped: the
variable label carries each item's full Polish stem and the value labels carry
its response anchors. The script asserts the anchors are identical across the
items of a block, so a block whose coding is not uniform fails rather than
shipping one item's anchors as if they were all of them.

THREE of the five blocks ship, and the split is a rights question. The wording
exists for all five -- 98 of 109 variables are labelled -- but:
  * KW5 (pandemic appraisal) is the study's OWN 23-adjective checklist, so the
    deposit's CC BY is the wording's licence;
  * KW3 is the MSPSS, registered `ship`;
  * KW4 is the FCV-19S, registered `ship`;
  * KW1 is the WHOQOL family, registered `block` -- no wording ships;
  * KW2 is the CSES, which had no register row until this batch wrote one with
    verdict `hold` -- so no wording ships.

The administered language is POLISH and the Polish wording is what ships, in
the base `item_text`/`option_text` fields. No English gloss is produced: the
deposit publishes none, and an IRW-written translation would be generated text
owing a disclosure. The provenance note records this as not_translated, i.e.
"not English, and no English ships on purpose", rather than leaving a reader to
wonder whether an English version was lost.

`item` is the lowercased source column with the dot replaced, exactly as
data/kopczynski_2021_covid_wellbeing.py assigns it (KW3.01 -> kw3_01).
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pyreadstat

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])

FIELDS = ["table", "section_id", "item", "instrument", "instructions",
          "section_prompt", "item_text", "correct_response", "option_text",
          "resp"]

# table -> (source prefix, instrument label, the shared stem that the item
# labels hang off, if the block has one)
SHIPS = {
    "kopczynski_2021_mspss": (
        "KW3",
        "Multidimensional Scale of Perceived Social Support (MSPSS, 12 items), "
        "Zimet, Dahlem, Zimet & Farley (1988), Polish administration",
        ""),
    "kopczynski_2021_fcv19s": (
        "KW4",
        "Fear of COVID-19 Scale (FCV-19S, 7 items), Ahorsu, Lin, Imani, "
        "Saffari, Griffiths & Pakpour (2020), Polish administration",
        ""),
    "kopczynski_2021_pandemic_appraisal": (
        "KW5",
        "Pandemic appraisal adjective checklist (study-authored), "
        "Kopczynski & Bartoszek 2021",
        "Pandemia COVID-19 jest dla mnie:"),
}
# KW5's labels are bare adjectives ("mobilizujaca", "krzywdzaca"), which are
# the checklist's items; the stem above is the deposit's own framing, recorded
# as section_prompt rather than invented into each item_text.

LABEL_RE = re.compile(r"^\s*KW\d+\.\d+\.?\s*(.*)$", re.S)


def main() -> None:
    df, meta = pyreadstat.read_sav(SRC)
    for table, (prefix, instrument, stem) in SHIPS.items():
        cols = sorted((c for c in df.columns
                       if re.match(rf"^{prefix}\.\d+$", c)),
                      key=lambda c: int(c.split(".")[1]))
        assert cols, prefix

        stems = {}
        for c in cols:
            lab = (meta.column_names_to_labels.get(c) or "").strip()
            assert lab, f"{c} has no variable label"
            m = LABEL_RE.match(lab)
            # The label repeats the column name before the stem; strip it so
            # item_text is the question, not "KW3.01. the question".
            stems[c] = (m.group(1) if m else lab).strip()
            assert stems[c], (c, lab)
        assert len(set(stems.values())) == len(cols), \
            f"{table}: duplicate stems {sorted(stems.values())}"

        anchors = meta.variable_value_labels.get(cols[0])
        assert anchors, f"{cols[0]} has no value labels"
        for c in cols:
            assert meta.variable_value_labels.get(c) == anchors, \
                f"{table}: {c}'s anchors differ from {cols[0]}'s"
        print(f"{table}: parsed {len(cols)} Polish stems and "
              f"{len(anchors)} identical anchors from the .sav metadata")

        rows = []
        for c in cols:
            for code, text in sorted(anchors.items(), key=lambda kv: kv[0]):
                rows.append({
                    "table": table,
                    "section_id": f"{table}_1",
                    "item": c.lower().replace(".", "_"),
                    "instrument": instrument,
                    "instructions": "",
                    "section_prompt": stem,
                    "item_text": stems[c],
                    "correct_response": "",
                    "option_text": str(text).strip(),
                    "resp": int(code),
                })
        path = OUT / f"{table}__items.csv"
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"  -> {path}: {len(rows)} rows, {len(cols)} items x "
              f"{len(anchors)} options")


if __name__ == "__main__":
    main()
