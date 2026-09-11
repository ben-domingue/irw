#!/usr/bin/env python3
"""
ENEM 2023 item text -- join to IRW `item` values and emit the per-table CSVs.

This is the year-independent half of the pipeline. 02_parse_dosvox_2023.py is the
year-specific part (it will need rewriting for the PDF-only years); this script
should carry over largely unchanged, since ITENS_PROVA_YYYY.csv exists for all 13
years with the same columns.

WHAT IT DOES
 1. maps (area, booklet position, language) -> CO_ITEM via ITENS_PROVA, using the
    regular-application LARANJA booklet, which is what the DOSVOX text transcribes
 2. drops booklet items with no counterpart in the IRW response table
 3. adds the items that the accessibility booklet substituted away, transcribed
    from the standard AZUL booklet PDF (01_pdf_sourced_2023.py)
 4. applies figure-description patches where INEP declined to describe a figure
 5. attaches instrument / instructions, and correct_response from TX_GABARITO
 6. writes {table}__items.csv per the itemtext standard

THE JOIN GATE. `item` and `resp` must match the live response table exactly.
`item` here is CO_ITEM taken verbatim from INEP's own position->item map, never
invented. `resp` is 0/1: the correct option scores 1, the four distractors 0,
matching the live table's resp values.

section_id / section_prompt are emitted empty: no ENEM 2023 item shares a passage
with another (verified four ways -- see STATUS.md).
"""
import csv, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.expanduser("~/enem/extracted_2023/microdados_enem_2023/DADOS")
ITENS = os.path.join(DADOS, "ITENS_PROVA_2023.csv")
MAIN = "/scratch/users/mazzafe/enem_output/regular/enem_2023_main_items.csv"

# Regular-application LARANJA (Braille / Adaptada Ledor) CO_PROVA per area. Braille
# and Ledor have identical position->item maps, so either serves; offset 7 is used.
LARANJA_REG = {"CH": "1197", "LC": "1207", "MT": "1217", "CN": "1227"}
TABLE = {a: f"enem_2023_1mil_{a.lower()}" for a in LARANJA_REG}

LANGUAGE = "Portuguese"   # ENEM is administered in Portuguese (irw#1777)

# Column order copied from itemtables/batch_015/weber2026_name_knowledge__items.csv,
# the first table shipped under the #1777 administered-language policy: the four
# _translated columns sit after resp, then `language`. raw_resp is appended last as
# this project's addition.
#
# raw_resp carries the printed option letter (A-E). The standard documents it as a
# stand-in for `resp` when no scoring key exists; here it is ADDITIONAL, because the
# live ENEM tables have both a scored `resp` (0/1) and a `text` column holding the raw
# letter. Without it there is no per-option letter anywhere in the item text, so
# option_text could not be joined to `text == "A"` -- and row order is not a safe
# substitute, since Redivis does not guarantee it. validate_items.R only falls back to
# raw_resp when `resp` is absent, so adding it alongside changes no gate.
SCHEMA = ["table", "section_id", "item", "instrument", "instructions",
          "section_prompt", "item_text", "correct_response", "option_text", "resp",
          "item_text_translated", "option_text_translated",
          "instructions_translated", "section_prompt_translated",
          "language", "raw_resp"]


def load_itens():
    """(area, position, tp_lingua) -> (co_item, gabarito) for the LARANJA booklets."""
    m, keys = {}, {}
    with open(ITENS, encoding="latin-1") as fh:
        rd = csv.DictReader(fh, delimiter=";")
        for r in rd:
            keys[r["CO_ITEM"]] = r["TX_GABARITO"]
            if r["CO_PROVA"] == LARANJA_REG.get(r["SG_AREA"]):
                k = (r["SG_AREA"], r["CO_POSICAO"], r["TP_LINGUA"] or "")
                if k in m and m[k] != r["CO_ITEM"]:
                    sys.exit(f"ambiguous position {k}: {m[k]} vs {r['CO_ITEM']}")
                m[k] = r["CO_ITEM"]
    return m, keys


def load_main():
    """area -> set of CO_ITEM in the IRW response tables."""
    s = defaultdict(set)
    with open(MAIN, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            s[r["SG_AREA"]].add(r["CO_ITEM"])
    return s


def load_translations():
    """Optional English renderings, keyed by item. Empty dict when not yet written.

    Shape: {"instructions": {<area>: str},
            "items": {<item>: {"stem": str, "options": {"A": str, ...}}}}
    """
    p = os.path.join(HERE, "translations_2023.json")
    if not os.path.exists(p):
        print("NOTE: translations_2023.json absent -- _translated columns will be "
              "empty, which is NOT shippable under irw#1777.\n")
        return {}
    import json
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    pos2item, keys = load_itens()
    tr = load_translations()
    tr_items = tr.get("items", {})
    tr_instr = tr.get("instructions", {})
    main_items = load_main()

    instr = {}
    with open(os.path.join(HERE, "parsed_dosvox_instrument_2023.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            instr[r["area"]] = (r["instrument"], r["instructions"])

    patches = {}
    with open(os.path.join(HERE, "figure_desc_patches_2023.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            patches[r["item"]] = (r["declined_text"], r["replacement"])

    # ---- 1-2. DOSVOX rows -> CO_ITEM, dropping items not in the IRW tables ----
    out = defaultdict(list)
    seen, dropped, unmapped = defaultdict(set), defaultdict(set), []
    annulled_items = defaultdict(set)
    with open(os.path.join(HERE, "parsed_dosvox_items_2023.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            area = r["area"]
            k = (area, r["position"], r["tp_lingua"])
            item = pos2item.get(k)
            if item is None:
                unmapped.append(k); continue
            if item not in main_items[area]:
                dropped[area].add(item); continue
            key = keys[item]
            # An annulled item (IN_ITEM_ABAN=1) has TX_GABARITO "X": there is no
            # correct answer. Per the itemtext standard correct_response is blank,
            # and every option scores 0 -- which is exactly what the response table
            # contains, since data/enem_YYYY.R computes resp as (raw == key) and no
            # response letter can equal "X".
            annulled = key not in ("A", "B", "C", "D", "E")
            if annulled:
                annulled_items[area].add(item)
            text = r["item_text"]
            if item in patches:
                declined, repl = patches[item]
                if declined not in text:
                    sys.exit(f"patch for {item}: declining text not found in item_text")
                text = text.replace(declined, repl)
            inst, instructions = instr[area]
            t = tr_items.get(item, {})
            out[area].append({
                "table": TABLE[area], "section_id": f"{TABLE[area]}_1", "item": item,
                "item_text_translated": t.get("stem", ""),
                "option_text_translated": t.get("options", {}).get(r["option_letter"], ""),
                "instructions_translated": tr_instr.get(area, ""),
                "section_prompt_translated": "",
                "language": LANGUAGE,
                "instrument": inst, "instructions": instructions,
                "section_prompt": "", "item_text": text,
                "correct_response": "" if annulled else key,
                "option_text": r["option_text"],
                "resp": 0 if annulled else (1 if r["option_letter"] == key else 0),
                "raw_resp": r["option_letter"],
                "_letter": r["option_letter"],
            })
            seen[area].add(item)

    if unmapped:
        sys.exit(f"positions with no ITENS_PROVA match: {unmapped}")

    # ---- 3. add the PDF-sourced items --------------------------------------
    added = defaultdict(set)
    with open(os.path.join(HERE, "pdf_sourced_items_2023.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            area = [a for a, t in TABLE.items() if t == r["table"]][0]
            item = r["item"]
            if item in seen[area]:
                sys.exit(f"{item} came from both DOSVOX and the PDF")
            if item not in main_items[area]:
                sys.exit(f"PDF-sourced {item} is not an IRW item")
            if r["correct_response"] != keys[item]:
                sys.exit(f"{item}: key {r['correct_response']} != ITENS_PROVA {keys[item]}")
            inst, instructions = instr[area]
            t = tr_items.get(item, {})
            out[area].append({
                "table": r["table"], "section_id": f"{r['table']}_1", "item": item,
                "item_text_translated": t.get("stem", ""),
                "option_text_translated": t.get("options", {}).get(r["option_letter"], ""),
                "instructions_translated": tr_instr.get(area, ""),
                "section_prompt_translated": "",
                "language": LANGUAGE,
                "instrument": inst, "instructions": instructions,
                "section_prompt": "", "item_text": r["item_text"],
                "correct_response": r["correct_response"],
                "option_text": r["option_text"], "resp": int(r["resp"]),
                "raw_resp": r["option_letter"],
                "_letter": r["option_letter"],
            })
            added[area].add(item)

    # ---- 6. write, and report coverage -------------------------------------
    print("coverage against the IRW response tables:")
    total_ok = True
    for area in ("LC", "CH", "CN", "MT"):
        got = seen[area] | added[area]
        want = main_items[area]
        missing, extra = want - got, got - want
        flag = "OK" if not missing and not extra else "GAP"
        if missing or extra: total_ok = False
        print(f"  {TABLE[area]:22} {len(got):>3}/{len(want):>3} items  "
              f"{len(out[area]):>4} rows  [{flag}]"
              f"{'  from PDF: ' + ','.join(sorted(added[area])) if added[area] else ''}")
        if missing: print(f"      MISSING: {sorted(missing)}")
        if extra:   print(f"      EXTRA:   {sorted(extra)}")
        if dropped[area]:
            print(f"      dropped (in booklet, not in IRW): {sorted(dropped[area])}")
        if annulled_items[area]:
            print(f"      annulled (no correct answer, correct_response blank, "
                  f"all options resp=0): {sorted(annulled_items[area])}")

        p = os.path.join(HERE, f"{TABLE[area]}__items.csv")
        with open(p, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, SCHEMA, extrasaction="ignore")
            w.writeheader()
            w.writerows(sorted(out[area],
                               key=lambda r: (int(r["item"]), r["_letter"])))

    done = sum(1 for a in out for r in out[a] if r["item_text_translated"].strip())
    tot = sum(len(out[a]) for a in out)
    print(f"\ntranslated rows: {done}/{tot}"
          f"  ({'COMPLETE' if done == tot else 'INCOMPLETE -- not shippable'})")
    print(f"wrote 4 files to {HERE}")
    print("all items accounted for" if total_ok else "SOME ITEMS UNACCOUNTED FOR")


if __name__ == "__main__":
    main()
