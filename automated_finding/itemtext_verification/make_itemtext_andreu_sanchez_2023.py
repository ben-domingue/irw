"""
Item text for andreu_sanchez_2023_information_sources and
andreu_sanchez_2023_lifestyle.

Source: Andreu-Sánchez, C., & Martín-Pascual, M. Á. (2023). Data - Positive
        and Negative Affect Schedule in early COVID-19 pandemic [Dataset].
        Zenodo. DOI: 10.5281/zenodo.8057093
License: CC BY 4.0 (verified on the Zenodo record, metadata.license.id =
        cc-by-4.0). Both blocks are study-authored COVID-era items, not a
        published instrument, so the deposit's licence is the wording's licence.

Mapping basis: data_labels. The workbook's ENGLISH and SPANISH sheets are the
same 45 columns of the same 333 respondents with the headers translated, and
each item column header IS the item wording, inside brackets
("Information [Television]" / "Información [Televisión]"). The item code used
by data/andreu_sanchez_2023_panas.py is the slugified English bracketed label,
so this script re-derives it with the same rule from the same sheet rather
than restating a list -- the join key cannot drift. The Spanish wording is
taken from the SPANISH sheet at the same column position, which is checked
below to be the same block prefix and the same column count.

Administration: Spanish for 308 of the 333 respondents, English for 25
(the deposit's "Language in which the questionnaire was answered" column, kept
in the response tables as cov_language). So `language` is "Spanish; English",
the base fields hold the Spanish as the majority administered version, and the
_translated fields hold the deposit's OWN published English -- not an
IRW-generated gloss.

Instructions, section prompts and the response-option labels come from the
deposit's "QUESTIONNAIRE IN SPANISH" / "QUESTIONNAIRE IN ENGLISH" sheets.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pandas as pd

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])

FIELDS = ["table", "section_id", "item", "instrument", "language",
          "instructions", "section_prompt", "item_text", "correct_response",
          "option_text", "resp", "instructions_translated",
          "section_prompt_translated", "item_text_translated",
          "option_text_translated"]

# Both texts are quoted verbatim from the deposit's two questionnaire sheets
# (rows 38-40 for the media block, 53-55 for the sports block).
BLOCKS = {
    "andreu_sanchez_2023_information_sources": dict(
        prefix_en="Information", prefix_es="Información", n=10,
        instrument="Information-source use during the early COVID-19 pandemic "
                   "(study-authored, Andreu-Sánchez & Martín-Pascual 2023)",
        instructions_es="HÁBITOS DE LOS MEDIOS. Durante la pandemia o el "
                        "periodo de aislamiento social por el COVID-19, te "
                        "informas a través de:",
        instructions_en="MEDIA HABITS. During the COVID-19 pandemic or the "
                        "period of social isolation due to COVID-19, you stay "
                        "informed through:",
        options={1: ("Nada o ligeramente", "Very slightly or not at all"),
                 2: ("Un poco", "A little"),
                 3: ("Moderadamente", "Moderately"),
                 4: ("Bastante", "Quite a bit"),
                 5: ("Mucho", "Extremely")},
    ),
    "andreu_sanchez_2023_lifestyle": dict(
        prefix_en="Sports", prefix_es="Deporte", n=6,
        instrument="Lockdown lifestyle change items (study-authored, "
                   "Andreu-Sánchez & Martín-Pascual 2023)",
        instructions_es="PARTICIPACIÓN DEPORTIVA. Desde que se declaró la "
                        "pandemia o el periodo de aislamiento social por el "
                        "COVID-19:",
        instructions_en="SPORTS PARTICIPATION. Since the COVID-19 pandemic or "
                        "period of social isolation due to COVID-19 was "
                        "declared:",
        options={1: ("Sí", "Yes"), 0: ("No", "No")},
    ),
}


def slug(header: str) -> str:
    """The same rule data/andreu_sanchez_2023_panas.py assigns codes with."""
    m = re.search(r"\[(.+?)\]", header)
    assert m, f"no bracketed label in {header!r}"
    return re.sub(r"[^a-z0-9]+", "_", m.group(1).lower()).strip("_")


def label(header: str) -> str:
    m = re.search(r"\[(.+?)\]", str(header))
    assert m, f"no bracketed label in {header!r}"
    return m.group(1).strip()


def main() -> None:
    en = pd.read_excel(SRC, sheet_name="ENGLISH", nrows=1)
    es = pd.read_excel(SRC, sheet_name="SPANISH", nrows=1)
    assert len(en.columns) == len(es.columns) == 45, (len(en.columns),
                                                      len(es.columns))

    for table, spec in BLOCKS.items():
        pairs = [(a, b) for a, b in zip(en.columns, es.columns)
                 if str(a).startswith(spec["prefix_en"])]
        assert len(pairs) == spec["n"], (table, len(pairs))
        # the Spanish column at the same position must be the same block
        for a, b in pairs:
            assert str(b).startswith(spec["prefix_es"]), (a, b)

        rows = []
        for a, b in pairs:
            code = slug(str(a))
            for resp, (opt_es, opt_en) in spec["options"].items():
                rows.append({
                    "table": table,
                    "section_id": f"{table}_1",
                    "item": code,
                    "instrument": spec["instrument"],
                    "language": "Spanish; English",
                    "instructions": spec["instructions_es"],
                    "section_prompt": "",
                    "item_text": label(b),
                    "correct_response": "",
                    "option_text": opt_es,
                    "resp": resp,
                    "instructions_translated": spec["instructions_en"],
                    "section_prompt_translated": "",
                    "item_text_translated": label(a),
                    "option_text_translated": opt_en,
                })
        path = OUT / f"{table}__items.csv"
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{path}: {len(rows)} rows, {spec['n']} items x "
              f"{len(spec['options'])} options")


if __name__ == "__main__":
    main()
