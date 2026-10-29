"""Item text for four of the twenty-one lee_whiting_2025_* (GPO-AI) tables.

Source: gpo-ai_codebook.docx in https://borealisdata.ca/dataset.xhtml?
persistentId=doi:10.5683/SP3/WCUN0S (CC BY-NC 4.0).

**Only four tables, and the reason is the mapping, not the text.** The codebook
documents the other seventeen blocks as a table: one header row of response
options, then one unlabelled row per item, in order. Nothing in it names
`populism_3` or `Justice_5`, so the only thing tying a stem to an item code
there is ROW ORDER -- the positional case that produced every mapping defect
found in the 2026-10 itemtext review. Those seventeen are recorded as not
shipped, with the codebook named as where the text is, rather than shipped on
an assumption.

These four are different: their columns are named by CONTENT, and the codebook
documents each variable by that name, so the tie is the source's own labelling.
`Digital_gvt_laid` is documented as the laid-off version, `TO_health_30m` as
the 30-minute wait, `neighbour_replace` as the local-community one. An
off-by-one is not available to go wrong.

Administered in 12 languages across 21 countries; the deposit publishes only
the English master questionnaire. So this is the standard's documented
fallback: the English goes in the base fields, `_translated` stays empty,
`language` names all twelve (it is a fact about the study, not a claim about
`item_text`), and `text_source=translated_substitute` with a
`translation_source` in provenance. For the seven English-fielding countries
this wording is the administered original; for the other fourteen it is a
stand-in.

For the two forced-choice tables, `option_text` is the respondent's own two
options, taken from the data values themselves -- the AI side and the human
side, verbatim, per item.

Run:  python3 make_itemtext_lee_whiting_2025.py <out_dir> <staged_response_dir>
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
RESP_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("../irw_output")

LANGUAGE = ("Chinese (Simplified); English; French; German; Indonesian; "
            "Italian; Japanese; Polish; Portuguese (Portugal); "
            "Portuguese (Brazil); Spanish (Spain); Spanish (Latin America)")

AMOUNT = [(1, "None at all"), (2, "A few"), (3, "A lot"), (4, "A great deal")]
AGREE = [(1, "Strongly disagree"), (2, "Somewhat disagree"),
         (3, "Neither agree nor disagree"), (4, "Somewhat agree"),
         (5, "Strongly agree")]

# table -> (instrument, instructions, {item code: stem}, options)
# `options` is None for the forced-choice tables, whose option text is read
# from the response data instead.
BLOCKS = {
    "lee_whiting_2025_job_loss_expectations": (
        "Expected job loss to automation, GPO-AI 2023",
        "",
        {
            "friendsfam_replace":
                "How many of your friends and family do you think will lose "
                "their jobs to a computer or machine in the next 10 years?",
            "neighbour_replace":
                "How many members of your local community do you think will "
                "lose their jobs to a computer or machine in the next 10 "
                "years?",
            "generation_replace":
                "How many members of future generations do you think will "
                "lose their jobs to a computer or machine?",
        },
        AMOUNT),
    "lee_whiting_2025_digital_government": (
        "AI in government digital services, GPO-AI 2023",
        "How much do you agree or disagree with the following statements",
        {
            "digital_gvt_both":
                "The government should modernize and integrate Artificial "
                "Intelligence (AI) into its digital services if it means "
                "people will be laid-off and services will be more efficient "
                "and quick?",
            "digital_gvt_efficien":
                "The government should modernize and integrate Artificial "
                "Intelligence (AI) into its digital services if it means "
                "services will be quicker and more efficient?",
            "digital_gvt_laid":
                "The government should modernize and integrate Artificial "
                "Intelligence (AI) into its digital services even if it means "
                "people will be laid-off?",
        },
        AGREE),
    "lee_whiting_2025_ai_vs_human_choice": (
        "AI-versus-human decision trade-offs, GPO-AI 2023",
        "",
        {
            "to_border":
                "Airports are often extremely busy, increasing travel time. "
                "Some governments now use Artificial Intelligence "
                "(AI)-algorithms at the border as security agents to process "
                "people entering the country. Would you prefer…",
            "to_finance":
                "Artificial Intelligence (AI) algorithms are used in credit "
                "scoring to assess an individual's creditworthiness based on "
                "their credit history and other financial information. Would "
                "you prefer…",
            "to_immigration":
                "Some governments use point systems or other metrics to make "
                "immigration-related decision, in which a potential immigrant "
                "is scored according to their education, age, skill sets, and "
                "other factors related to their likelihood of success. Would "
                "you prefer…",
            "to_justice":
                "Artificial Intelligence (AI) algorithms are used in policing "
                "to predict crime hotspots and allocate resources "
                "accordingly. In bail decisions, algorithms are used to "
                "assess a defendant's risk of flight or reoffending. Would "
                "you prefer…",
        },
        None),
    "lee_whiting_2025_ai_nurse_tradeoff": (
        "AI nurse versus waiting for a human nurse, GPO-AI 2023",
        "",
        {
            code:
                "Imagine that you are not feeling well and your government "
                "has just introduced a new telephone service which will allow "
                "you to find the healthcare services and information. Would "
                "you prefer:"
            for code in ("to_health_10m", "to_health_30m", "to_health_1h",
                         "to_health_2h", "to_health_3h")
        },
        None),
}

COLS = ["table", "section_id", "item", "instrument", "language",
        "instructions", "section_prompt", "item_text", "correct_response",
        "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated",
        "option_text_translated"]


# The two option strings per forced-choice item, verbatim from the data, with
# the code the processing script assigned. Written out rather than re-derived
# so this file is readable beside the response table.
CHOICE_OPTIONS = {
    "to_border": {
        1: "An Artificial Intelligence (AI)-algorithm to decide who to screen "
           "more carefully",
        0: "A human to decide who to screen more carefully"},
    "to_finance": {
        1: "An Artificial Intelligence (AI)-algorithm to make the final "
           "decision about whether you get a loan.",
        0: "A human to make the final decision in whether you get a loan."},
    "to_immigration": {
        1: "An Artificial Intelligence (AI)-algorithm making choices to "
           "select the immigrant most likely to succeed.",
        0: "Public servants interviewing potential immigrants to select the "
           "immigrant most likely to succeed."},
    "to_justice": {
        1: "An Artificial Intelligence (AI)-algorithm to make the final "
           "decision on parole.",
        0: "A human to make the final decision on parole."},
    "to_health_10m": {
        1: "Chatting with an Artificial Intelligence (AI)-robot nurse right "
           "now",
        0: "Talking to a human-nurse after waiting on hold more than 10 "
           "minutes"},
    "to_health_30m": {
        1: "Chatting with an Artificial Intelligence (AI)-robot nurse right "
           "now",
        0: "Talking to a human-nurse after waiting on hold more than 30 "
           "minutes"},
    "to_health_1h": {
        1: "Chatting with an Artificial Intelligence (AI)-robot nurse right "
           "now",
        0: "Talking to a human-nurse after waiting on hold more than 1 hour"},
    "to_health_2h": {
        1: "Chatting with an Artificial Intelligence (AI)-robot nurse right "
           "now",
        0: "Talking to a human-nurse after waiting on hold more than 2 hours"},
    "to_health_3h": {
        1: "Chatting with an Artificial Intelligence (AI)-robot nurse right "
           "now",
        0: "Talking to a human-nurse after waiting on hold more than 3 hours"},
}


def observed(table: str) -> dict:
    """{item: set(resp)} actually present in the staged response CSV."""
    out: dict = {}
    with open(RESP_DIR / f"{table}.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.setdefault(r["item"], set()).add(int(r["resp"]))
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for table, (instrument, instructions, stems, options) in BLOCKS.items():
        seen = observed(table)
        assert set(seen) == set(stems), (table, sorted(set(seen) ^ set(stems)))
        rows = []
        for code, stem in stems.items():
            opts = (options if options is not None
                    else sorted(CHOICE_OPTIONS[code].items(), reverse=True))
            for resp, text in opts:
                if resp not in seen[code]:
                    continue
                rows.append({
                    "table": table,
                    "section_id": f"{table}_1",
                    "item": code,
                    "instrument": instrument,
                    "language": LANGUAGE,
                    "instructions": instructions,
                    "section_prompt": "",
                    "item_text": stem,
                    "correct_response": "",
                    "option_text": text,
                    "resp": resp,
                    "instructions_translated": "",
                    "section_prompt_translated": "",
                    "item_text_translated": "",
                    "option_text_translated": "",
                })
        path = OUT / f"{table}__items.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            w.writeheader()
            w.writerows(rows)
        print(f"  -> {path.name}: {len(rows)} rows, {len(stems)} items")


if __name__ == "__main__":
    main()
