#!/usr/bin/env python3
"""Item text for petrovici_2025_cultural_participation / _culture_appreciation / _wellbeing
(figshare 10.6084/m9.figshare.23614611). Romanian administration (telephone survey, Cluj).

Cheap case: the deposit ships the questionnaire in Romanian and in the authors' own English
translation; data/petrovici_2025_cultural_participation.py stems(lang) reads both by item code (A1, B1,
C1 ...), the deposit's own column names. The English in *_translated is the authors' translation, not
IRW's. The B block's codebook says 1 Yes / 0 No but the file holds 1 and 2; 2 is shipped with option
text "Nu"/"No" on the reading that it is the No code (every B item is 1/2/99 only).
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("petrovici_2025_cultural_participation")
A_OPT = {6: ("De cinci sau mai multe ori", "Five or more times"), 5: ("De patru ori", "Four times"),
         4: ("De trei ori", "Three times"), 3: ("De două ori", "Twice"), 2: ("O dată", "Once"), 1: ("Niciodată", "Never")}
B_OPT = {1: ("Da", "Yes"), 2: ("Nu", "No")}
C_OPT = {1: ("Acord total", "Total agreement"), 2: ("Acord parțial", "Partial agreement"),
         3: ("Dezacord parțial", "Partial disagreement"), 4: ("Dezacord total", "Totally disagree")}
META = {
    "petrovici_2025_cultural_participation": (mod.A, A_OPT, "Cultural participation (Cultural Consumption Barometer / Holt)",
        "În ultimele 12 luni, cât de des ați desfășurat următoarele activități (indiferent dacă în localitatea unde locuiți sau altundeva):",
        "In the last 12 months, how often did you carry out the following activities (whether in the locality where you live or elsewhere):"),
    "petrovici_2025_culture_appreciation": (mod.B, B_OPT, "Cultural appraisal index (associations with art and cultural experiences)",
        "Cu care dintre următoarele aspecte asociați arta și experiențele culturale?",
        "With which of the following do you associate art and cultural experiences?"),
    "petrovici_2025_wellbeing": (mod.C, C_OPT, "Personal Wellbeing Score (Benson et al., 2019), four items",
        "În ce măsură sunteți de acord cu următoarele afirmații?",
        "To what extent do you agree with the following statements?"),
}


def main():
    ro, en = mod.stems("ro"), mod.stems("en")
    for table, (items, opts, instrument, prompt_ro, prompt_en) in META.items():
        rows = [row(table, f"{table}_1", c, instrument, "Romanian", r, ro[c], option_text=opts[r][0],
                    section_prompt=prompt_ro, item_text_tr=en[c], option_text_tr=opts[r][1], section_prompt_tr=prompt_en)
                for c in items for r in sorted(opts)]
        write(table, rows)


if __name__ == "__main__":
    main()
