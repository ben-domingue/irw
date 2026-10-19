#!/usr/bin/env python3
"""Item text for gerou_2023_dass21 (#3077, 2026-10-19a batch).

WHAT SHIPS, AND WHY IT IS THE ENGLISH. The administration was GREEK: all 21
stems are in the deposit's own .sav variable labels, verbatim, and they are the
DASS-21 in canonical order (checked item by item against the official English
form -- item 1 "Δεν μπορούσα να ηρεμήσω τον εαυτό μου" / "I found it hard to
wind down", item 2 dry mouth, ... item 21 "life was meaningless"). So the
administered wording is recoverable and the code-to-text mapping is certain.

It is still NOT what ships, on rights:

  * The DASS-21 itself is public domain. itemtext/instrument_rights_register.csv
    carries the verdict `ship` (2026-09-10, Ben), on the DASS FAQ's "The DASS
    questionnaire is public domain, and so permission is not needed to use it".
    The official download page repeats it: "The DASS questionnaire forms may be
    downloaded and copied without restriction. However, the scales may not be
    modified or sold for profit."
  * The GREEK TRANSLATION is a separate work by George Lyrakos and Chrysa
    Arvaniti (University of Athens; Lyrakos et al. 2011, Eur Psychiatry 26,
    1731), and the register row's own note records that the FAQ requires
    translations to be public domain too. The DASS site hosts the Greek form
    but its translations page states only "This page provides links to
    translations ... carried out by others. We are not able to provide any
    assurances about the adequacy or validity of the translations. Please
    address all enquiries to the person or group who carried out the
    translation" -- a disclaimer, not a grant. No terms for the Greek version
    could be located.

Under the 2026-10-15 rule that silence on a named third-party work is a hold,
the Greek wording is held and the English canonical form ships in its place.
That is the schema's documented FALLBACK (itemtext_standard.md, "The fallback,
and what `language` holds in it"): the English goes in the base fields,
`language` still says Greek because it is a fact about the study, the
`_translated` columns stay empty, and `text_source=translated_substitute`
records it. Populated `language` + empty `item_text_translated` is exactly the
query that finds this table for a later backfill if the Greek is ever cleared.

A ruling on one question releases the Greek: does the DASS site's
"copied without restriction" grant extend to the translations it hosts? If
yes, this table is re-run with the .sav's Greek labels in the base fields and
this English moved into `_translated`.

SOURCE OF THE ENGLISH, fetched 2026-10-19 (recorded here because
itemtext_provenance.csv has no translation_source column -- see TODO.md):
  https://www2.psy.unsw.edu.au/dass/Download%20files/Dass21.pdf
  sha256 8644cc86534d397e371985d5b25422ba76c4cdae0a5aed8f1a4453c17a5cd393
Instructions, all 21 stems and all four anchors are transcribed from that one
form, so nothing here is IRW-authored and nothing is a machine translation.
The deposit's own English value labels differ trivially from the official
anchors ("Do not apply to me at all" for "Did not apply to me at all"); the
official form wins, since that is the version being shipped.

MAPPING: `data_labels`. The .sav variable labels tie each DASS_n column to its
stem with no inference, the column names are the source's own (not positional),
and the canonical order was confirmed stem by stem as above. `resp` 0-3 is the
DASS's own scoring, and the staged response table's resp set is exactly {0,1,2,3}.
The .sav also carries a vestigial fifth value label for 4 ("Applied to me very
much, or most of the time"), which no respondent used; no option row is written
for it, because the item/resp sets must match the shipped table exactly.
"""
import csv
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent / "itemtext_output"
TABLE = "gerou_2023_dass21"
SECTION = f"{TABLE}_1"
INSTRUMENT = ("Depression Anxiety Stress Scales (DASS-21), Lovibond & "
              "Lovibond")
LANGUAGE = "Greek"
INSTRUCTIONS = ("Please read each statement and circle a number 0, 1, 2 or 3 "
                "which indicates how much the statement applied to you over "
                "the past week. There are no right or wrong answers. Do not "
                "spend too much time on any statement.")

# Verbatim from Dass21.pdf (sha256 above), in the form's own order.
STEMS = [
    "I found it hard to wind down",
    "I was aware of dryness of my mouth",
    "I couldn't seem to experience any positive feeling at all",
    "I experienced breathing difficulty (eg, excessively rapid breathing, "
    "breathlessness in the absence of physical exertion)",
    "I found it difficult to work up the initiative to do things",
    "I tended to over-react to situations",
    "I experienced trembling (eg, in the hands)",
    "I felt that I was using a lot of nervous energy",
    "I was worried about situations in which I might panic and make a fool of "
    "myself",
    "I felt that I had nothing to look forward to",
    "I found myself getting agitated",
    "I found it difficult to relax",
    "I felt down-hearted and blue",
    "I was intolerant of anything that kept me from getting on with what I was "
    "doing",
    "I felt I was close to panic",
    "I was unable to become enthusiastic about anything",
    "I felt I wasn't worth much as a person",
    "I felt that I was rather touchy",
    "I was aware of the action of my heart in the absence of physical exertion "
    "(eg, sense of heart rate increase, heart missing a beat)",
    "I felt scared without any good reason",
    "I felt that life was meaningless",
]
ANCHORS = {
    0: "Did not apply to me at all",
    1: "Applied to me to some degree, or some of the time",
    2: "Applied to me to a considerable degree, or a good part of time",
    3: "Applied to me very much, or most of the time",
}

COLUMNS = ["table", "section_id", "item", "instrument", "language",
           "instructions", "instructions_translated", "section_prompt",
           "section_prompt_translated", "item_text", "item_text_translated",
           "correct_response", "option_text", "option_text_translated", "resp"]


def main():
    assert len(STEMS) == 21
    rows = []
    for i, stem in enumerate(STEMS, start=1):
        for resp, anchor in ANCHORS.items():
            rows.append({
                "table": TABLE,
                "section_id": SECTION,
                "item": f"DASS_{i}",
                "instrument": INSTRUMENT,
                "language": LANGUAGE,
                "instructions": INSTRUCTIONS,
                "instructions_translated": "",
                "section_prompt": "",
                "section_prompt_translated": "",
                "item_text": stem,
                "item_text_translated": "",
                "correct_response": "",
                "option_text": anchor,
                "option_text_translated": "",
                "resp": resp,
            })

    # The join keys must match the staged response table exactly.
    resp_csv = HERE.parent / "irw_output" / f"{TABLE}.csv"
    with open(resp_csv, newline="", encoding="utf-8") as f:
        live = list(csv.DictReader(f))
    assert {r["item"] for r in live} == {r["item"] for r in rows}, "item sets differ"
    assert {int(r["resp"]) for r in live} == set(ANCHORS), "resp sets differ"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{TABLE}__items.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{os.path.basename(out)}: {len(rows)} rows, "
          f"{len({r['item'] for r in rows})} items x {len(ANCHORS)} options")


if __name__ == "__main__":
    main()
