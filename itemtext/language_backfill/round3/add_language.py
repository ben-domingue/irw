#!/usr/bin/env python3
"""Round 3 of the administered-language backfill (irw#1777, ruled on #3224).

Two tables, and they are what is LEFT of tier A rather than the start of it.
The 2026-09-01 audit listed 79 tier-A tables; re-measured 2026-10-25 against the
live listing and the published text:

    79  tier A in audit_2026-09-01.csv
   -16  no longer serve item text at all (withdrawn since the audit)
  = 63  live
   -61  already carry `language`, done by the item-text rounds since September
  =  2  this script

Nothing about the text changes. What changes is that the table says which
language respondents read: `language` names it, and the four `_translated`
columns are present and NA, which is the schema's documented signal that the
base text fields ARE the administered wording and no English rendering ships
with them (itemresponsewarehouse.org/itemtext.html).

Translations are deliberately NOT generated here. `spanishmegastudy` is the
audit's DEFERRED case -- 1,270 item stems and 3,989 option labels, ~5,259
strings, which needs a bulk machine-translation pass and a review afterwards --
and IRW has no translator configured since OpenAI was retired from the project.
Naming the language does not depend on translating it, and is the half that
makes the table honest about what it holds.

    python3 round3/add_language.py          # writes round3/staging/
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]

#: Each language is the audit's per-field verdict, which is proof rather than
#: likelihood: a field counts as administered-language only on a non-Latin
#: script or more than three non-ASCII letters. Both of these are Latin-script
#: with diacritics, and both were confirmed by eye against the published text
#: on 2026-10-25 (Portuguese: "Eu tento fazer com que o/a (nome da crianca)
#: termine de comer toda a sua comida"; Spanish: "A que deidad griega
#: representa la estatua de El Coloso de Rodas?").
LANGUAGE = {
    "pedroso_2021_ifsq_pressuring": "Portuguese",
    "spanishmegastudy": "Spanish",
}

#: Untouched by this script. Asserted field by field after writing, because the
#: only thing that makes a wording backfill safe to run unattended is that it
#: cannot have changed a word of the wording.
TEXT_COLS = ("item", "resp", "item_text", "option_text", "instructions",
             "section_prompt", "instrument", "correct_response", "section_id")


def main():
    n = 0
    for table, lang in sorted(LANGUAGE.items()):
        src = os.path.join(HERE, "published", f"{table}.csv")
        with open(src, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            sys.exit(f"{table}: no published rows at {src}")
        if any((r.get("language") or "").strip() for r in rows):
            sys.exit(f"{table}: already carries a language; refusing to overwrite it")

        out = []
        for r in rows:
            r = dict(r)
            r["language"] = lang
            for c in ("instructions_translated", "section_prompt_translated",
                      "item_text_translated", "option_text_translated"):
                r[c] = "NA"
            out.append(r)

        dst = os.path.join(HERE, "staging", f"{table}__items.csv")
        with open(dst, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            w.writeheader()
            for r in out:
                w.writerow({c: r.get(c, "NA") for c in COLS})

        for before, after in zip(rows, out):
            for c in TEXT_COLS:
                assert (before.get(c) or "") == (after.get(c) or ""), f"{table}: {c} changed"
        # ...and the file on disk says the same thing, since the assertion above
        # only checks what was held in memory.
        with open(dst, encoding="utf-8") as f:
            written = list(csv.DictReader(f))
        assert len(written) == len(rows), f"{table}: {len(written)} rows written, {len(rows)} read"
        for before, after in zip(rows, written):
            for c in TEXT_COLS:
                assert (before.get(c) or "") == (after.get(c) or ""), f"{table}: {c} changed on disk"
            assert after["language"] == lang

        print(f"  {table:<32} {lang:<12} {len(out):>5} rows")
        n += 1
    print(f"\n{n} table(s) written to round3/staging/ -- upload with red_up")


if __name__ == "__main__":
    main()
