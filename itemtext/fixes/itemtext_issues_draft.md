# Draft `itemtext_issues.qmd` additions -- 2026-09-22, APPLIED

**These 29 entries were applied** to `itemtext_issues.qmd` on branch
`itemtext-issues-2026-09-22` and opened as **datapages/irw#225**. Kept here as the
record of what was drafted for the irw_text_2 v6.3 release (batches 293-299, 305-308).

28 came from `draft_issues_qmd.R` (generated from each batch's `provenance.csv`
`public_note`). The 29th, `christensen_2018_wsssf_5831`, is HAND-WRITTEN: the drafter
reads only `public_note` and that table's caveats live in `notes.csv`, which is the
blind spot its own "REVIEW THESE TOO" section exists to flag.

Verified before opening the PR: `yaml.load` parses the page to 1005 entries, all with
`table` and `issue`, no duplicate tables; `check_issues_page.R` reports zero DUE.

---

- table: chile_2023_children-adolescents-survey_aa
  issue: |-
    The English in the _translated columns of this table was produced by IRW, not by the study: EANNA 2023 published its questionnaire only in Spanish, and the Spanish in the base fields is what respondents actually heard. Note also that ten of the 38 items (a8_78, a8_87, a8_88, a8_99, a9_78, a9_87, a9_88, a9_99, a11_88, a11_99) are the 'nobody', 'not applicable', 'don't know' and 'no answer' checkboxes of three multiple-select questions rather than substantive items
- table: christensen_2018_wsssf_2171
  issue: |-
    resp is the SCORED value, not the literal answer: 1 always means the schizotypy-keyed response, and option_text records which literal True/False answer that was for each item, because the keying direction differs item by item (e.g. resp=1 is 'True' for pb01 but 'False' for py01). Item codes mi/pb/py/sa do not encode item content.
- table: dwyer_2019_clinton_activist
  issue: |-
    Respondents answered the Activist Identity and Commitment Scale on a 0-to-5 scale, but IRW stores the SPSS codes 1-6, so each resp value is one higher than the number on the scale the respondent saw; option_text gives the anchor wording for the corresponding point.
- table: kermen_2022_self_efficacy
  issue: |-
    The 11 reverse-scored items of this scale are stored already reversed, so the response anchors shipped for them run in the opposite direction to the other six: for b2, b4, b5, b6, b7, b10, b11, b12, b14, b16 and b17 a stored resp of 1 is the administered answer 'cok iyi' (very well) and 5 is 'hic' (not at all). The English item text was translated by IRW from the published Turkish form; only the two scale endpoints were labelled in the source, so resp 2-4 carry no option text
- table: kumlander_2018_scs
  issue: |-
    English for the three middle response anchors (resp 2, 3 and 4) was rendered by IRW from the Finnish; the study published English only for the two endpoints, and the Finnish in option_text is what respondents actually read.
- table: milavic_2019_psisysf
  issue: |-
    Item wording for this table is English while the instrument was administered in Croatian: the study's data deposit and its single supplementary file carry no Croatian text, so the English printed in the paper's Table 1 is shipped in its place, and the anchors in option_text (1 = strongly disagree, 5 = strongly agree) are taken from that table's footnote even though the same paper's Methods section instead describes the scale as running from 1 = almost never to 5 = almost always
- table: rdatasets_gssabortion
  issue: |-
    Item text comes from the published original instrument rather than this study's own materials
- table: risticdedic_2025_dhq_currentstate
  issue: |-
    The DHQ was administered in ten languages across nine EU countries (Croatian, Dutch, Finnish, German, English, Catalan, Slovenian, French, Greek and Spanish); the item text shipped here is the English master version, which 87 of the 834 schools answered directly and from which the other nine versions were translated. All ten language versions are published by the authors at doi.org/10.5281/zenodo.13767190. The 0-100 slider is labelled only at its endpoints, so option_text is populated for resp=0 and resp=100 only.
- table: risticdedic_2025_dhq_expectation
  issue: |-
    The DHQ was administered in ten languages across nine EU countries (Croatian, Dutch, Finnish, German, English, Catalan, Slovenian, French, Greek and Spanish); the item text shipped here is the English master version, which 87 of the 834 schools answered directly and from which the other nine versions were translated. All ten language versions are published by the authors at doi.org/10.5281/zenodo.13767190. The 0-100 slider is labelled only at its endpoints, so option_text is populated for resp=0 and resp=100 only.
- table: risticdedic_2025_dhq_importance
  issue: |-
    The DHQ was administered in ten languages across nine EU countries (Croatian, Dutch, Finnish, German, English, Catalan, Slovenian, French, Greek and Spanish); the item text shipped here is the English master version, which 87 of the 834 schools answered directly and from which the other nine versions were translated. All ten language versions are published by the authors at doi.org/10.5281/zenodo.13767190. The 0-100 slider is labelled only at its endpoints, so option_text is populated for resp=0 and resp=100 only
- table: spain_2025_ageism_agreement
  issue: |-
    The English item, instruction and response-option wording for this table was produced by IRW, not by CIS, which publishes Estudio 3493 in Spanish only; the administered Spanish is in the base fields. Note also that the response values run 1, 2, 4, 5 with no option row for 3: respondents could volunteer a middle 'Regular (ni de acuerdo ni en desacuerdo)' answer (CIS code 3, not read aloud) which the IRW processing script drops to missing along with 8 'N.S.' and 9 'N.C.'.
- table: spain_2025_ageism_bureaucracy
  issue: |-
    The English item, instruction and response-option wording for this table was produced by IRW, not by CIS, which publishes Estudio 3493 in Spanish only; the administered Spanish is in the base fields. Two things to know about the responses: the P.11 block was asked only of respondents aged 65 and over (1,030 of the study's 5,006 interviews), and the scale runs from 1 'En muchas ocasiones' (most frequent) to 4 'Nunca', with the not-read-aloud category 6 'No he realizado nunca esta gestion' plus 'N.S.'/'N.C.' dropped to missing by the IRW processing script, so those have no option row.
- table: spain_2025_ageism_comparison
  issue: |-
    The English item and response-option wording for this table was produced by IRW, not by CIS, which publishes Estudio 3493 in Spanish only; the administered Spanish is in the base columns. Note also that each of the three questions allowed a volunteered, not-read-aloud 'both equally' answer (CIS code 3, worded differently in each question) which the IRW processing script drops to missing along with 8 'N.S.' and 9 'N.C.', so the live scale is the two read-aloud categories only and no option row exists for those codes.
- table: spain_2025_ageism_difficulty
  issue: |-
    The English item, instruction and response-option wording for this table was produced by IRW, not by CIS, which publishes Estudio 3493 in Spanish only; the administered Spanish is in the base fields. Note also that P.12 was asked only of respondents aged 65 and over (the questionnaire routes anyone under 65 past the block), and that the response values run 1, 2, 4, 5 with no option row for 3 or 6: respondents could volunteer a middle 'Regular (ni facil ni dificil)' answer (CIS code 3) or 'nunca ha necesitado realizar esta gestion' (code 6), neither of which the interviewer read aloud, and the IRW processing script drops both to missing along with 8 'N.S.' and 9 'N.C.'.
- table: spain_2025_ageism_elderpriority
  issue: |-
    The English item, instruction and response-option wording for this table was produced by IRW, not by CIS, which publishes Estudio 3493 in Spanish only; the administered Spanish is in the base fields. Note also that the 0-10 priority scale was labelled at its two ends only -- 0 'Ninguna prioridad' and 10 'Maxima prioridad' -- so values 1 to 9 carry no option text because the study printed none, and 'N.S.'/'N.C.' (CIS codes 98 and 99) are dropped to missing by the IRW processing script.
- table: spain_2025_ageism_elderslights
  issue: |-
    The English item, instruction and response-option wording for this table was produced by IRW, not by CIS, which publishes Estudio 3493 in Spanish only; the administered Spanish is in the base fields. Two things to know about the responses: the P.13 block was asked only of respondents aged 65 and over (1,030 of the study's 5,006 interviews), and the fourth response category was coded 7 'Ninguna vez' by CIS and recoded to 4 by the IRW processing script to give a contiguous 1-4 scale, so resp runs from 1 'Muchas veces' (most frequent) to 4 'Ninguna vez' (never).
- table: spain_2025_ageism_problems
  issue: |-
    The English item and response-option wording for this table was produced by IRW, not by CIS, which publishes Estudio 3493 in Spanish only; the administered Spanish is in the base columns. Two things to know about the responses: the scale runs from 1 'Muchos problemas' (most problems) to 5 'Ningun problema' (none), so a higher value means fewer perceived problems; and the values 1, 2, 4, 5 are non-contiguous because respondents could volunteer a middle 'Ni muchos ni pocos' answer (CIS code 3) that the interviewer did not read aloud, which the IRW processing script drops to missing along with 'N.S.' and 'N.C.', so no option row exists for it. Note also that p2's administered wording is elliptical -- the interviewer asked only 'And young people under 35?' immediately after p1, so p2's response frame is the one stated in p1's question.
- table: spain_2025_ageism_youthpriority
  issue: |-
    The English item, instruction and response-option wording for this table was produced by IRW, not by CIS, which publishes Estudio 3493 in Spanish only; the administered Spanish is in the base fields. Note also that the 0-10 priority scale was labelled at its two ends only -- 0 'Ninguna prioridad' and 10 'Maxima prioridad' -- so values 1 to 9 carry no option text because the study printed none, and 'N.S.'/'N.C.' (CIS codes 98 and 99) are dropped to missing by the IRW processing script.
- table: spain_2025_ageism_youthslights
  issue: |-
    The English item, instruction and response-option wording for this table was produced by IRW, not by CIS, which publishes Estudio 3493 in Spanish only; the administered Spanish is in the base fields, and item 1's diminutives 'nino/a' and 'nene/a' have no exact English equivalent. Two things to know about the responses: the P.16 block was asked only of respondents aged 18 to 34 (975 of the study's 5,006 interviews), and the resp scale is deliberately non-contiguous -- CIS coded the volunteered '(NO LEER) Regular' category 3 and the IRW processing script drops it, while recoding CIS's 'Ninguna vez' from 7 to 5, so resp runs 1 'Muchas veces' (most frequent), 2 'Bastantes veces', 4 'Pocas veces', 5 'Ninguna vez' (never) with no value 3.
- table: spain_2025_democracy_efficacy
  issue: |-
    The English item, instruction and response-option wording for this table was produced by IRW, not by CIS, which publishes this questionnaire only in Spanish; the administered Spanish is in the base fields. Note also that respondents could volunteer a middle 'Ni de acuerdo ni en desacuerdo' answer (CIS code 3, not read aloud, chosen by 0.1-0.7% of the sample) which the IRW processing script treats as missing, so the response values run 1, 2, 4, 5 with no option row for 3.
- table: spain_2025_democracy_internal
  issue: |-
    The item and response wording for this CIS survey question is in Spanish, as administered; the English in the _translated columns was produced by IRW, not by CIS.
- table: spain_2025_democracy_judiciary
  issue: |-
    The response scale respondents heard was 1 Muy de acuerdo / 2 De acuerdo / 4 En desacuerdo / 5 Muy en desacuerdo, with a fifth, not-read-aloud category 3 'Ni de acuerdo ni en desacuerdo' plus 8 'N.S.' and 9 'N.C.' that the IRW processing script drops to missing, which is why resp jumps from 2 to 4 and no option row exists for 3; the English in the _translated columns was produced by IRW, not by CIS.
- table: spain_2025_democracy_media
  issue: |-
    The response scale respondents heard was 1 Muy de acuerdo / 2 De acuerdo / 4 En desacuerdo / 5 Muy en desacuerdo, with a fifth, not-read-aloud category 3 'Ni de acuerdo ni en desacuerdo' plus 8 'N.S.' and 9 'N.C.' that the IRW processing script drops to missing, which is why resp jumps from 2 to 4 and no option row exists for 3; the English in the _translated columns was produced by IRW, not by CIS, which publishes this questionnaire in Spanish only.
- table: spain_2025_democracy_parties
  issue: |-
    The English item, instruction and response-option wording for this table was produced by IRW, not by CIS, which publishes Estudio 3497 in Spanish only; the administered Spanish is in the base fields. Note also that the response values run 1, 2, 4, 5 with no option row for 3: respondents could volunteer a middle 'Ni de acuerdo ni en desacuerdo' answer (CIS code 3, not read aloud) which the IRW processing script drops to missing along with 8 'N.S.' and 9 'N.C.'.
- table: spain_2025_democracy_priorities
  issue: |-
    The item, instruction and response-option wording in the _translated columns is IRW's own English; CIS publishes this questionnaire only in Spanish, and the administered Spanish is in the base fields.
- table: spain_2025_democracy_system
  issue: |-
    The English item, option and question text for this table was machine-translated by IRW from the Spanish that CIS actually administered in Estudio 3497; the administered Spanish is the authoritative text and sits in the base columns.
- table: spain_2025_democracy_trust
  issue: |-
    Respondents answered on an 0-10 trust scale on which only the endpoints were labelled ('Ninguna confianza' at 0, 'Total confianza' at 10), so option_text is deliberately blank for resp 1-9 rather than repeating the numeral; the codes 98 'N.S.' and 99 'N.C.' are dropped to missing by the IRW processing script and have no option row; and the English in the _translated columns was produced by IRW, not by CIS, which publishes this questionnaire in Spanish only.
- table: trivia_fastrich_2017
  issue: |-
    Five of the 244 trivia questions were reworded part way through data collection, so the item text IRW ships is the later of two administered wordings: item 135 and 234 read 'poisonous' rather than 'venomous' for the first 387 and 266 responses, item 167 read 'what county' for its first 370, item 224 read 'gas marks' for its first 330, and item 267's 'Hippolyte Mege-Mouries' appeared for 322 responses with its accented characters corrupted; both wordings of each are visible in the response table's own cov_question column.

- table: christensen_2018_wsssf_5831
  issue: |-
    option_text is item-dependent for this table, because it stores keyed scores rather than raw answers: resp=1 reads 'True' on the 42 items the study does not mark reversed and 'False' on the 18 it does, all items having been scored so that a higher score means more schizotypy. The endorsement rates confirm it (the reverse-keyed items are ordinary pleasant experiences and run 0.036-0.276, not the ~0.9 a raw true/false coding would give). The authors' ' (reversed)' annotation was stripped from item_text as scoring notation rather than administered wording, and no instruction text is published anywhere in the deposit or article, so instructions is empty.
