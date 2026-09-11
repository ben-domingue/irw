#!/usr/bin/env python3
"""
ENEM 2023 item text -- append the discrepancy + mapping-verification records.

DO NOT RUN until 04_validate.sbatch has passed for all four tables: the evidence
strings below assert that it did.

Appends to two files in the repo:
  itemtext/itemtables/pending_index_notes.csv   table,note
  itemtext/mapping_verification.csv             table,batch,mapping_basis,uploaded,
                                                route,status,evidence

Vocabularies follow the existing files. mapping_basis="data_labels" because the
position->item map is INEP's own ITENS_PROVA_2023.csv, shipped with the microdata,
not something reconstructed or read out of a paper.
"""
import csv, os, sys

REPO = "/home/users/mazzafe/irw"
NOTES = os.path.join(REPO, "itemtext/itemtables/pending_index_notes.csv")
MAPV = os.path.join(REPO, "itemtext/mapping_verification.csv")
UPLOADED = "2026-09-03"
BATCH = "enem_2023"

COMMON = (
    "Item text comes from INEP's own accessibility booklet (LARANJA - Braille / "
    "Adaptada Ledor), read from the DOSVOX screen-reader plain text shipped in the "
    "2023 microdata. That booklet is the preferred source because INEP wrote verbal "
    "descriptions of the figures, graphs and tables into it, so image content is "
    "INEP's wording rather than generated. Booklet position -> IRW item via "
    "ITENS_PROVA_2023.csv (CO_POSICAO -> CO_ITEM) for {prova}. No ENEM item shares a "
    "passage with another (verified: no shared-passage markers, no question lacking "
    "its own stem, no adjacent stems >45% similar, no long sentence in two stems), so "
    "section_id and section_prompt are empty and each item's stimulus sits in "
    "item_text."
)

AI = (
    "Descriptions marked inline '(gerada por IA)' are NOT INEP's - INEP wrote none for "
    "these, so they were generated from the rendered booklet page. Everything not so "
    "marked is INEP's own wording. See runkit/ITEMTEXT provenance notes."
)

NOTE = {
 "enem_2023_1mil_lc": COMMON.format(prova="CO_PROVA 1207") +
   " All 50 items covered. The 50-for-45-positions count is the foreign-language "
   "block: positions 1-5 appear twice, once per language, disambiguated by TP_LINGUA "
   "(0 = English, 1 = Spanish) and by the booklet's explicit '(opcao ingles)' / "
   "'(opcao espanhol)' headers. The REDACAO essay prompt that trails the objective "
   "questions is not an item in the response table and is not shipped.",

 "enem_2023_1mil_ch": COMMON.format(prova="CO_PROVA 1197") +
   " All 45 items covered from the accessibility booklet; no gaps, no generated "
   "descriptions.",

 "enem_2023_1mil_cn": COMMON.format(prova="CO_PROVA 1227") +
   " 43 of 45 items came from the accessibility booklet. Items 78578 and 54804 are "
   "substituted away in that booklet and were transcribed instead from the standard "
   "day-2 AZUL booklet PDF (ENEM_2023_P1_CAD_07_DIA_2_AZUL.pdf, positions 110 and "
   "123), read as rendered page images. For those two items every figure, table, "
   "equation and option description is generated; for 78578 the five options ARE "
   "graphs with no printed text, so all of its option_text is generated. Item 60332's "
   "figure (structure of Aldrin) is in the accessibility booklet but INEP declined to "
   "describe it ('nao foi descrita, pois suas informacoes nao foram solicitadas para a "
   "resolucao da questao'); a generated description replaces that sentence, and the "
   "item text is otherwise INEP's. This is the only declined description in all 185 "
   "items of 2023. The booklet's two substitute items (14385, 14397) have text but no "
   "counterpart in the response table, so they are not shipped. " + AI,

 "enem_2023_1mil_mt": COMMON.format(prova="CO_PROVA 1217") +
   " 43 of 45 items came from the accessibility booklet. Items 125902 and 81742 are "
   "substituted away in that booklet and were transcribed from the standard day-2 AZUL "
   "booklet PDF (positions 163 and 176); for 125902 the five options ARE diagrams with "
   "no printed text, so all of its option_text is generated. Item 14887 is annulled by "
   "INEP (IN_ITEM_ABAN=1, motive 'Exclusao pedagogica', TX_GABARITO='X'), i.e. it has "
   "no correct answer: correct_response is blank and all five options carry resp=0. "
   "That mirrors the response table, where data/enem_2023.R computes "
   "resp = if_else(raw == key, 1, 0) and no response letter can equal 'X', so every "
   "respondent is scored 0 on it. Ten such annulled items exist across the ENEM years "
   "(2018, 2020 x2, 2021, 2022, 2023, 2024, 2025 x3) and are a response-data question, "
   "not an item-text one. The booklet's two substitute items (141552, 14435) have text "
   "but no counterpart in the response table, so they are not shipped. " + AI,
}

EVID = (
 "Mapping is INEP's own published position->item table (ITENS_PROVA_2023.csv, "
 "{prova}), so item values are taken verbatim from the publisher rather than "
 "reconstructed. Cross-checks: (1) validate_items.R --resp-csv against the local "
 "45M-row response CSV passed on both the item set and the resp set ({nitem} items, "
 "resp {{0,1}}); (2) option order is fixed across booklet colours - all 381 2023 "
 "CO_ITEMs have exactly one TX_GABARITO across every CO_PROVA - so text transcribed "
 "from one booklet is valid for that item regardless of the booklet a respondent sat; "
 "(3) Braille and Adaptada Ledor booklets have identical position->item maps in all "
 "four areas, so the DOSVOX file's booklet identity is unambiguous; (4) for each of "
 "the five items sourced or patched from the standard AZUL PDF, the key recorded in "
 "ITENS_PROVA was confirmed against the content at that letter in the PDF - 78578=B "
 "by stoichiometry (0,01 mol needs 1,16 g NaCl, yields 4,72 g, matching option B's "
 "plateau), 54804=E (the only one of five compounds drawn with stereobonds), "
 "125902=A (constant speed with distance rising, holding, then falling implies a "
 "circular sector), 81742=E (n(3n-1)/2 at n=8 = 92), 60332=E (a low-polarity "
 "lipophilic compound concentrates in milk fat). Item order IS permuted across "
 "booklets, so positions were always looked up for the booklet actually being read."
)
NITEM = {"enem_2023_1mil_lc": 50, "enem_2023_1mil_ch": 45,
         "enem_2023_1mil_cn": 45, "enem_2023_1mil_mt": 45}
PROVA = {"enem_2023_1mil_lc": "CO_PROVA 1207", "enem_2023_1mil_ch": "CO_PROVA 1197",
         "enem_2023_1mil_cn": "CO_PROVA 1227", "enem_2023_1mil_mt": "CO_PROVA 1217"}


def append(path, fieldnames, newrows, keycol="table"):
    existing = list(csv.DictReader(open(path, encoding="utf-8")))
    have = {r[keycol] for r in existing}
    add = [r for r in newrows if r[keycol] not in have]
    skip = [r[keycol] for r in newrows if r[keycol] in have]
    if skip:
        print(f"  already present, skipped: {skip}")
    if not add:
        return 0
    with open(path, "a", newline="", encoding="utf-8") as fh:
        csv.DictWriter(fh, fieldnames, quoting=csv.QUOTE_ALL).writerows(add)
    return len(add)


def main():
    if "--yes" not in sys.argv:
        sys.exit("refusing to write to the repo without --yes")

    n1 = append(NOTES, ["table", "note"],
                [{"table": t, "note": NOTE[t]} for t in sorted(NOTE)])
    print(f"pending_index_notes.csv: +{n1} rows")

    mrows = [{"table": t, "batch": BATCH, "mapping_basis": "data_labels",
              "uploaded": UPLOADED, "route": "publisher_position_item_map",
              "status": "VERIFIED",
              "evidence": EVID.format(prova=PROVA[t], nitem=NITEM[t])}
             for t in sorted(NOTE)]
    n2 = append(MAPV, ["table", "batch", "mapping_basis", "uploaded", "route",
                       "status", "evidence"], mrows)
    print(f"mapping_verification.csv: +{n2} rows")


if __name__ == "__main__":
    main()
