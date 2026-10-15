#!/usr/bin/env python3
"""Item text for the thirteen kellstedt_2017_* tables (Dataverse 10.7910/DVN/SRC9HN). English
administration (US national telephone survey, 2004).

Cheap case: data/kellstedt_2017_climate_survey.py stems() reads each item's Stata variable label
(an abbreviated stem such as "concern now - social security") and its value labels; the item code is
the deposit's own column name. The 0-10 scales are labelled only at the endpoints (the deposit's
midpoint labels are the bare digit, "1|"), so option_text is blank on 1-9; the 1-4 and 0/1 scales are
fully labelled. The questionnaire's full question wording is not in the deposit.
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("kellstedt_2017_climate_survey")
INSTRUMENT = {
    "kellstedt_2017_concern_now": "Concern about national issues (now)",
    "kellstedt_2017_concern_future": "Concern about national issues (future)",
    "kellstedt_2017_informed": "How informed about national issues",
    "kellstedt_2017_science_quiz": "Science and climate knowledge (true/false)",
    "kellstedt_2017_nep": "New Ecological Paradigm items",
    "kellstedt_2017_eco_behavior": "Pro-environmental behaviour frequency",
    "kellstedt_2017_civic_action": "Political and environmental actions taken",
    "kellstedt_2017_gwcc_attitudes": "Global warming and climate change attitudes",
    "kellstedt_2017_info_source_use": "Information source use",
    "kellstedt_2017_info_source_trust": "Information source trust",
    "kellstedt_2017_competence": "Perceived competence of institutions on climate change",
    "kellstedt_2017_policy_support": "Climate policy support",
    "kellstedt_2017_climate_effects": "Expected effects of climate change",
}


def main():
    for table, items in mod.stems().items():
        rows = []
        for code, label, vl in items:
            for r in sorted(vl):
                opt = vl[r]
                if opt.endswith("|"):  # unlabeled midpoint of a 0-10 scale
                    opt = ""
                rows.append(row(table, f"{table}_1", code, INSTRUMENT[table], "", int(r), label, option_text=opt))
        write(table, rows)


if __name__ == "__main__":
    main()
