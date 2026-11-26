"""Provenance + mapping-verification text for the 2026-11-25c item text batch, one entry per table.
Read by records_repos_2026-11-25c.py. Builder: make_itemtext_repos_2026-11-25c.py."""
import re
from pathlib import Path

BUILDER = "itemtext_verification/make_itemtext_repos_2026-11-25c.py"
DATA = Path(__file__).resolve().parent.parent.parent / "data"


def tables_of(script):
    src = (DATA / f"{script}.py").read_text(encoding="utf-8")
    m = re.search(r"^BLOCKS = (\{.*?\n\})", src, re.S | re.M) or re.search(r"^BLOCKS = (\{.*?\})\n", src, re.S | re.M)
    return list(eval(m.group(1)))


RECORDS = {}


def add(script, *, source_ref, note, evidence, mapping_basis="data_labels",
        text_source="study_materials", public_note="", tables=None, per_table=None):
    for t in tables or tables_of(script):
        extra = (per_table or {}).get(t, "")
        RECORDS[t] = dict(mapping_basis=mapping_basis, text_source=text_source, source_ref=source_ref,
                          note=note + (" " + extra if extra else ""), public_note=public_note,
                          route="exempt: data_labels", status="NOT_NEEDED", evidence=evidence)


def hold(script, *, source_ref, note, tables=None, mapping_basis="data_labels", text_source="study_materials"):
    for t in tables or tables_of(script):
        RECORDS[t] = dict(mapping_basis=mapping_basis, text_source=text_source, source_ref=source_ref,
                          note="HELD, NOT SHIPPED 2026-11-25. " + note, public_note="", shipped=False)


GEN = f"Generated at processing time (automated_finding Step 3.5, repos leads 2026-11-25c) by {BUILDER}; gates run against the staged irw_output/<table>.csv (--resp-csv / --resp-dir)."

# --- herrera ----------------------------------------------------------------------------------
add("herrera_2026_market_traders",
    source_ref="10.5281/zenodo.23455377 ; diccionario_de_datos.csv (codigo, enunciado, escala)",
    note=("instrument: study-authored questionnaire (Herrera Lopez, Mires Jara & Puican Rodriguez 2026) -- "
          "stems match no published scale (searched 2 verbatim: GFN1 'Lleva un control de los ingresos de su "
          "negocio', CTD1 'Presenta sus declaraciones tributarias mediante plataformas virtuales'; no hits), "
          "the items are specific to Peruvian SUNAT practice and the deposit cites no source scale; rights: "
          "study-authored under the deposit's CC BY 4.0 (Zenodo record + LEEME.txt). " + GEN +
          " Codes are diccionario_de_datos.csv's `codigo`, which is the data file's own column name, kept "
          "unchanged by data/herrera_2026_market_traders.py, so the tie is by name. Anchors from the same "
          "file's `escala` (1 = nunca .. 5 = siempre), asserted identical for all 36 items. language=Spanish; "
          "English in *_translated is IRW's own (translation_source = machine_translation; owes an "
          "itemtext_issues.qmd entry). instructions blank: the deposit publishes none."),
    public_note=("The English item and option wording on this table was translated by IRW, not published "
                 "by the source; the administered Spanish is in item_text and option_text."),
    evidence=("NOT_NEEDED. The item id is the data file's column name (GFN1..TRD4, unchanged by "
              "data/herrera_2026_market_traders.py) and the deposit's diccionario_de_datos.csv gives the "
              "same code (`codigo`) beside each statement (`enunciado`) -- an explicit code-label match, one "
              "dictionary row per item, 36/36 across the five tables. No positional step."))

# --- croitoru ---------------------------------------------------------------------------------
add("croitoru_2026_workplace_comm", text_source="translated_substitute",
    source_ref="10.5281/zenodo.23503832 ; README_codebook.txt (VARIABLES, MEASUREMENT SCALE)",
    note=("instrument: study-authored items (Croitoru, Florea, Diaconeasa & Stanescu 2026) -- stems match "
          "no published scale (searched 3 verbatim: CM_1 'My direct supervisor shows me consideration when "
          "I encounter difficulties', CA_1 'My colleagues listen carefully to me when I tell them about a "
          "work problem', PERF_1/PERF_2 'I perform my tasks with few errors' / 'I manage to complete my "
          "workload'; no hits), and the README cites no source scale; rights: study-authored under the "
          "deposit's CC BY 4.0. " + GEN + " Administered in Romanian (README: 'items translated from "
          "English by back-translation'); the deposit publishes only the English, checked in README_codebook.txt "
          "and Export_SmartPLS.csv (the only two files), neither of which carries Romanian item wording. So "
          "the English ships in the base fields as the fallback: text_source=translated_substitute, "
          "language=Romanian, *_translated empty; translation_source = study_supplied (the depositors' own "
          "English). Codes CM_1..PERF_4 are the CSV column names, kept by data/croitoru_2026_workplace_comm.py; "
          "the README lists each code beside its statement. Anchors from the README's MEASUREMENT SCALE."),
    public_note=("Respondents answered a Romanian version of these items; the deposit publishes only the "
                 "authors' English wording, which is what this table carries."),
    evidence=("NOT_NEEDED. The item id is the Export_SmartPLS.csv column name (CM_1..PERF_4, unchanged by "
              "data/croitoru_2026_workplace_comm.py) and README_codebook.txt prints that same code beside "
              "each statement -- an explicit code-label match, 20/20 across the five tables (the builder "
              "asserts exactly 20 parsed). No positional step."))

# --- ahmad ------------------------------------------------------------------------------------
add("ahmad_2026_ai_code_trust",
    source_ref=("10.6084/m9.figshare.35106577 ; workbook sheet Instrument_EN ('Item text (exactly as shown "
                "to respondents)', 'Response format'); Variable_Codebook (knowledge key)"),
    note=("instrument: author-written questionnaire (Ahmad 2026) -- the deposit's own Instrument_EN sheet "
          "marks every one of these items 'Author-written' in its 'Source or note' column (asserted by the "
          "builder); rights: author-written under the deposit's CC BY 4.0. " + GEN + " Item ids are the "
          "Data_Entry column names, equal to Instrument_EN's 'Item ID'. Administered in English to 270 and "
          "in French to 72 respondents (cov_language); the French wording is in the Bilingual_Instrument_A1 "
          "sheet, but the schema carries one administered text, so language = 'English; French' and the base "
          "fields hold the English version (the 2026-09-11 multi-language ruling)."),
    public_note="72 of the 342 respondents read the French version of the questionnaire; this table carries the English wording.",
    per_table={"ahmad_2026_secure_coding_knowledge": (
        "K1-K6 are multiple-choice (A-D) and IRW scores them 0/1 against the codebook key (B,C,B,B,B,A, "
        "asserted): item_text holds the question with its four options exactly as Instrument_EN prints "
        "them, correct_response the keyed letter, and the resp 0/1 rows have blank option_text because "
        "the source labels no scored level.")},
    evidence=("NOT_NEEDED. The item id is the Data_Entry column name (UR1..K6, unchanged by "
              "data/ahmad_2026_ai_code_trust.py) and the deposit's Instrument_EN sheet gives the same code "
              "('Item ID') beside the item text and response format -- an explicit code-label match, 31/31 "
              "across the five tables. No positional step."))

LANG_UNSET = "Administration language not stated in the deposit; English as deposited, language unset (the 2026-10 precedent for English-only deposits)."
NN = "NOT_NEEDED. The item id is the source file's own column name ({codes}, kept by data/{script}.py) and {src} gives that same code beside each statement -- an explicit code-label match, {n}. No positional step."


def ship(script, *, ref, instrument_note, how, codes, srcdesc, n, text_source="study_materials",
         public_note="", tables=None, per_table=None):
    add(script, source_ref=ref, text_source=text_source, public_note=public_note, tables=tables, per_table=per_table,
        note=instrument_note + " " + GEN + " " + how,
        evidence=NN.format(codes=codes, script=script, src=srcdesc, n=n))


MT = ("English in *_translated is IRW's own (translation_source = machine_translation; owes an itemtext_issues.qmd entry).")
MT_PUB = "The English item wording on this table was translated by IRW, not published by the source; the administered {lang} is in item_text."

ship("sengarie_2026_sustainable_fashion", ref="10.5281/zenodo.23879195 ; xlsx sheet 'Codebook' (Variable, Construct, Description / Item)",
     instrument_note=("instrument: study-authored items (Sengarie & Ratnaputri 2026) -- stems match no published scale (searched 2 "
                      "verbatim: GBI1 'This local fashion brand is known for its commitment to environmental sustainability', EW1 "
                      "'I have sufficient knowledge of environmental degradation issues'; no hits); the deposit cites no source scale; "
                      "rights: study-authored under the deposit's CC BY 4.0."),
     how="Construct per code asserted from the Codebook's Construct column. No anchors anywhere in the deposit: option_text blank on every point. " + LANG_UNSET,
     codes="EW1..PI7", srcdesc="the xlsx Codebook sheet's Variable column", n="42/42 across the four tables")

ship("efawati_2026_entrepreneurial_leadership", ref="10.7910/DVN/DHFHMV ; xlsx sheet 'codebook' (Variable code, Full item wording) + 'Supplementary Data 2 - Questionnaire.pdf' (instructions, anchors)",
     instrument_note=("instrument: study-authored items (Efawati, Chaniago, Andriani & Veranita 2026) -- stems match no published scale "
                      "(searched 3 verbatim: EL1 'Inspires me by explaining my vision and work goals', IC4 'I feel more creative when "
                      "working in a supportive team', EL9 'Provides clear work rules without stifling creativity'; no hits); not the "
                      "Renko ENTRELEAD items; rights: study-authored under the deposit's CC0 1.0."),
     how=("instructions and the 1 = Strongly disagree .. 5 = Strongly agree anchors from the deposit's questionnaire PDF, which is "
          "printed in English. " + LANG_UNSET),
     codes="EL1..WP10", srcdesc="the xlsx codebook sheet's 'Variable code' column", n="29/29 across the three tables")

ship("lee_2026_ai_reliance", ref="10.7910/DVN/O4E9YN ; Data.xlsx sheet 'Codebook' (Variable, Construct, English label or item, Values and coding)",
     tables=["lee_2026_meaning_making", "lee_2026_perceived_control", "lee_2026_trust_in_ai", "lee_2026_creepiness",
             "lee_2026_task_oriented_reliance", "lee_2026_overreliance", "lee_2026_ai_avoidance"],
     instrument_note=("instrument: Lee (2026) AI-reliance questionnaire -- stems searched verbatim (A01 'I actively spend time reflecting on "
                      "events that happen in my life', H01/H03 overreliance items; no published match); rights: study-authored under the "
                      "deposit's CC0 1.0, except as noted per table."),
     how=("Construct per code and the 1-5 anchors asserted from the Codebook for every item. The Codebook heads its wording column "
          "'English label or item' and the record names no paper, so the administration language cannot be established. " + LANG_UNSET +
          " Two of the nine constructs are held (lee_2026_mastery: Pearlin Mastery Scale; lee_2026_self_esteem: CSES/RSES mix)."),
     per_table={"lee_2026_creepiness": ("The four items read as the Creepiness of Situation Scale's emotional-creepiness wording "
                                        "(Langer & Konig 2018) reworded for AI; CRoSS was first published under CC BY 4.0 (Frontiers in "
                                        "Psychology 10.3389/fpsyg.2018.02220), register row CRoSS (ship) written 2026-11-25.")},
     codes="A01..I04", srcdesc="the Codebook sheet's Variable column", n="one codebook row per item, 27/27 across the seven tables")

ship("umoru_2026_older_farmers", ref="10.6084/m9.figshare.35100916 ; AR_Codebook.xlsx sheet 'Variables' (Variable, Label in SPSS file, value labels) + AR_Studies_Questionnaire.docx (section anchors)",
     tables=["umoru_2026_social_capital", "umoru_2026_health_stressors"],
     instrument_note=("instrument: study-authored items (Umoru et al. 2026) -- the social-capital and health-stressor items are written "
                      "for Kogi State farmers (Esusu/Adashi groups, ploughed land, farm inputs) and match no published scale (searched 1 "
                      "verbatim, SC5; no hit); rights: study-authored under the deposit's CC BY 4.0."),
     how=("Interviewer-administered; " + LANG_UNSET + " SC anchors from the questionnaire's Section C header (3 = Neither agree nor "
          "disagree); HS1-HS6 difficulty and HS7-HS16 frequency anchors from the codebook, asserted per item. The life-satisfaction "
          "block (umoru_2026_life_satisfaction) is held: SWLS-derived."),
     codes="SC1..HS16", srcdesc="AR_Codebook.xlsx's Variable column", n="26/26 across the two tables")

ship("charzynska_2026_work_addiction", ref="10.5281/zenodo.24139252 ; Codebook.csv (Variable, Label, Values)",
     tables=["charzynska_2026_iwas5"],
     instrument_note=("instrument: International Work Addiction Scale, 5-item form (IWAS-5), Atroszko, Charzynska et al., J Behav Addict "
                      "2025 -- identified from the codebook's own 'IWAS' labels and the published scale; rights: depositor-originated (the "
                      "deposit's authors are the IWAS's authors), under the deposit's CC BY 4.0; register row IWAS (ship) written 2026-11-25."),
     how=("instructions = the shared stem 'How often during THE LAST YEAR have you...' (asserted identical across the five labels), "
          "item_text = the remainder; anchors from Values. Administered in the languages of 85 cultures; the deposit publishes only the "
          "English master and maps no culture to a language, so language is unset and the public_note says so. UWES-3 and MWMS-6 held."),
     public_note="Respondents in 85 cultures answered translated versions; this table carries the English master wording published with the data.",
     codes="IWAS1..IWAS5", srcdesc="Codebook.csv", n="5/5")

ship("wren_2026_trauma_help_seeking", ref="10.6084/m9.figshare.33623410 ; Qualtrics .sav variable + value labels",
     tables=["wren_2026_ace"],
     instrument_note=("instrument: Adverse Childhood Experiences questionnaire, 10 items, in the 'Finding Your ACE Score' wording "
                      "(read on the labels: 'Did a parent or other adult in the household often swear at you...'); rights: the register's "
                      "ACE row (ship, Ben 2026-10-18, irw#3078) covers exactly this wording."),
     how=("data/wren_2026_trauma_help_seeking.py recodes Q4-Q13 from 1 = Yes / 2 = No to 1/0; the builder asserts every item's value "
          "labels are {1: Yes, 2: No}, so resp 1 = Yes and resp 0 = No. CTQ-SF, the three GHSQ tables and CAGE-AID are held."),
     codes="Q4..Q13", srcdesc="the .sav's own variable labels", n="10/10")

ship("anon_2026_perceived_narcissism", ref="10.5281/zenodo.23982003 ; EFAData.sav + CFAData.sav variable + value labels (survey PDFs not used)",
     instrument_note=("instrument: a Perceived Narcissism Inventory under development by the depositors (Towson University; EFA then CFA "
                      "samples), plus their own impression items -- the deposit is the instrument's development data and its statements "
                      "('This person is selfish' ...) match no published scale; rights: study-authored under the deposit's CC BY 4.0."),
     how=("Labels and value labels asserted identical wherever the two .sav files share a column. Codes ending in R are the "
          "depositors' reverse-keyed statements, stored as answered (not reflected). Prolific IDs were never read."),
     codes="selfish..GladEX", srcdesc="the variable label of that column in EFAData.sav / CFAData.sav", n="44/44 across the two tables")

ship("ye_2026_game_music", ref="10.6084/m9.figshare.33425338 ; 'Raw Data.xlsx' sheet rows 1-3 (English, Chinese, code)",
     instrument_note=("instrument: study-authored game-music questionnaire (Ye 2026) -- stems match no published scale (searched 2 verbatim: "
                      "MC3/MC2, CC1; no hits); the deposit cites no source scale; rights: study-authored under the deposit's CC BY 4.0."),
     how=("Administered in Chinese (row 2, 'Questionnaire item in Chinese') -> item_text; the depositor's own English (row 1) -> "
          "item_text_translated (translation_source = study_supplied). No anchors in the deposit: option_text blank."),
     codes="MC1..CC4", srcdesc="the sheet's row 3, column by column, beside rows 1-2", n="26/26 across the six tables")

ship("sucipto_2026_genai_finlit", ref="10.5281/zenodo.23313645 ; Google Forms export headers ('<code> <Indonesian stem>')",
     instrument_note=("instrument: study-authored TAM-style items specific to Generative AI and retail investors' financial literacy "
                      "(Sucipto, Susanto & Utama 2026) -- searched 1 verbatim (PEOU2), no published source; not Davis's PU/PEOU wording; "
                      "rights: study-authored under the deposit's CC BY 4.0."),
     how=("language=Indonesian; " + MT + " No anchors in the deposit: option_text blank (every item observed 1-4)."),
     public_note=MT_PUB.format(lang="Indonesian"),
     codes="PEOU1..AU4 (the second 'PU3' header -> PU3_b)", srcdesc="the same Google Forms header", n="23/23 across the seven tables")

add("aini_2026_high_protein_food",
    source_ref="10.5281/zenodo.23295180 ; Google Forms export headers (each header is the Indonesian stem)",
    note=("instrument: study-authored items (Aini 2026) -- searched 1 verbatim (smm1), no published source; the deposit cites none; "
          "rights: study-authored under the deposit's CC BY 4.0. " + GEN + " The deposit has NO codes: the codes are positional, "
          "assigned by data/aini_2026_high_protein_food.py (header 2-7 = smm1-6, 8-14 = reviews1-7, 15-21 = hb1-7, 22-24 = value1-3, "
          "25-28 = purchase_intention1-4); the builder applies the identical slicing to the same header row (28 headers asserted), so "
          "each item_text is the header whose column the script melted under that code. Block names are IRW's reading of the stems. "
          "language=Indonesian; " + MT + " No anchors: option_text blank."),
    public_note=MT_PUB.format(lang="Indonesian"),
    evidence=("NOT_NEEDED. The item_text IS the source column's own header (Google Forms writes the full stem as the header). The "
              "IRW code was assigned to that column by position in data/aini_2026_high_protein_food.py, and the builder re-derives the "
              "tie by applying the script's own slicing to the same header row rather than by matching stem order to a document, so "
              "there is no second ordering to get wrong: 27/27 across the five tables."))

ship("tothe_2021_student_satisfaction", ref="10.17632/7cjz65mg6g ; educational-factors.xlsx sheet 'details' (variable name, details)",
     instrument_note=("instrument: author-developed questionnaire (To-The, Khuc-Van, Hoang-Duc et al. 2021) -- the deposit cites no source "
                      "scale; rights: study-authored under the deposit's CC BY 4.0. One exception: b4_8 'I am satisfied with my life' "
                      "matches the register's SWLS row (block) word for word, so its item_text is left blank pending a ruling."),
     how=("Gated against the LIVE tables (uploaded 2026-11-23) via irw_table_sets(); audit_batch.R run live. Anchors: only the "
          "endpoints are labelled in the source (1 = Bad, 5 = Good); 2-4 blank. Vietnamese students; " + LANG_UNSET),
     per_table={"tothe_2021_other_satisfaction": "b4_8's item_text is blank by design (SWLS register match, see above); 7 of 8 items worded."},
     codes="a13_1..b4_8", srcdesc="the details sheet", n="one details row per item, 75/75 across the thirteen tables")

ship("minozzo_2026_seafood_consumers", ref="10.5281/zenodo.22284893 ; amostra_calibracao.xlsx headers ('<prompt> [<Portuguese item>]') + Supplementary_Material_EN Table_S1 (English)",
     instrument_note=("instrument: study-authored seafood-consumer survey (Minozzo Giordani 2026) -- Table_S1 calls the wording the study's "
                      "own and cites no source scale; stems are specific to Brazilian seafood purchase; rights: study-authored under the "
                      "deposit's CC BY 4.0."),
     how=("Codes come from data/minozzo_2026_seafood_consumers.py's explicit header->code dict (no position), re-read by the builder. "
          "item_text = the bracketed Portuguese, section_prompt = the header's block prompt (one section_id per distinct prompt within "
          "a table). English: the depositor's Table_S1 translation for the 48 listed items (Table_S1's Portuguese asserted equal to the "
          "header); the 7 barrier items and the block prompts are IRW's own translation (machine_translation; owes an issues-page "
          "entry). Anchors from Table_S1's note: 1 = discordo totalmente, 7 = concordo totalmente; 2-6 unlabelled. language=Portuguese."),
     public_note=("The English for the section prompts (and, on the barriers table, for the items) was translated by IRW; the item "
                  "translations elsewhere are the author's own. The administered Portuguese is in item_text and section_prompt."),
     codes="frescor..barreira_7", srcdesc="the Google Forms header the script renames by exact text", n="55/55 across the thirteen tables")

add("upoma_2026_ai_learning_stress", tables=["upoma_2026_ai_literacy_ethics", "upoma_2026_ai_stressors"],
    source_ref="10.17632/f26fhdpw23 ; AI_Learning_Stress_Master_Codebook.xlsx sheet Variable_Codebook (Variable, Source Question, Value Labels, Notes)",
    note=("instrument: the deposit's own study-specific items -- the README and the codebook's Notes column mark exactly these blocks "
          "'study-specific' (AI Literacy & Ethics Q18-Q21; AI stressors Q132-Q133, 'NOT part of PSS-10'), asserted by the builder; "
          "rights: study-authored under the deposit's CC BY 4.0. " + GEN + " Gated against the LIVE tables (uploaded 2026-11-23). "
          "item_text = the bracketed part of Source Question; anchors from Value Labels. English administration "
          "(survey_instrument_english.docx). The TAM/AAIUS/GADS/GAIES/SDLRS/PSS-derived tables are held."),
    evidence=("NOT_NEEDED. The item id is the source CSV column name (Q18..Q21, Q132, Q133, unchanged by "
              "data/upoma_2026_ai_learning_stress.py) and the codebook's Variable_Codebook gives that same code beside its Source "
              "Question -- an explicit code-label match, 6/6. No positional step."))

# --- holds ------------------------------------------------------------------------------------
import csv as _csv
_HL = Path(__file__).resolve().parent.parent / "itemtext_hold_2026-11-25.csv"
for _r in _csv.DictReader(open(_HL, newline="", encoding="utf-8")):
    RECORDS[_r["table"]] = dict(mapping_basis="data_labels", text_source="study_materials",
                                source_ref="see automated_finding/itemtext_hold_2026-11-25.csv",
                                note=("HELD, NOT SHIPPED 2026-11-25. instrument: " + _r["instrument"] + "; rights: none found -- "
                                      + _r["reason"] + " Built and gated (" + BUILDER + "), parked in "
                                      "itemtext_output/held_2026-11-25/; the response table ships."), shipped=False)

for _t in ["upoma_2026_tam_usefulness", "upoma_2026_tam_ease_of_use", "upoma_2026_aaius", "upoma_2026_gads",
           "upoma_2026_gaies_interaction", "upoma_2026_gaies_frequency", "upoma_2026_sdlrs_self_management",
           "upoma_2026_sdlrs_self_control", "upoma_2026_sdlrs_desire_learning", "upoma_2026_pss"]:
    RECORDS[_t] = dict(mapping_basis="unknown", text_source="unknown", source_ref="10.17632/f26fhdpw23",
                       note=("HELD, NOT SHIPPED 2026-11-25 (not built). instrument: the deposit's README calls these blocks adapted "
                             "from TAM (Davis), AAIUS, GADS, GAIES, SDLRS (Guglielmino) and the PSS-10 (Cohen); rights: none found -- "
                             "PSS is BLOCK and the TAM PU triad HOLD in the register; the rest are named third-party instruments with no "
                             "grant (register row 'Upoma-2026-adapted-battery' hold). Wording is in survey_instrument_english.docx and "
                             "the codebook's Source Question column."), shipped=False)

for _t in ["vilkaitevaitone_2026_ewom_credibility", "vilkaitevaitone_2026_argument_strength", "vilkaitevaitone_2026_product_attitude",
           "vilkaitevaitone_2026_ewom_adoption", "vilkaitevaitone_2026_purchase_intention", "vilkaitevaitone_2026_source_homophily",
           "vilkaitevaitone_2026_source_trust"]:
    RECORDS[_t] = dict(mapping_basis="unknown", text_source="unknown", source_ref="10.7910/DVN/Y5S7QY",
                       note=("HELD, NOT SHIPPED 2026-11-25 (not built). instrument: items adapted from cited third-party scales -- the "
                             "deposit's own 'Variables and codebook' Source column names Cheung et al. 2009, Durmaz & Yuksel 2017, Jiang & "
                             "Benbasat 2007, Lu et al. 2014, Dhun & Dangi 2023 / Onofrei et al. 2022, Fisher et al. 1979; rights: none "
                             "found -- the Wu et al. (2025) adapted-battery precedent (hold); register row 'Vilkaitevaitone-2026-eWOM-battery' "
                             "hold. Stems are in the .sav variable labels and the codebook, anchors in the value labels."), shipped=False)
