#!/usr/bin/env python3
"""Item text for izquierdo_lopez_2026_eosp (Zenodo 10.5281/zenodo.22308208). Spanish administration;
teacher ratings of pupils.

Cheap case: the .sav variable labels (identical to the deposit's codebook) are the Spanish stems, read by
data/izquierdo_lopez_2026_eosp.py stems() under the deposit's own column names. No value labels on the
items, so the nine points carry blank option_text. Four sections = the EOSP's four areas. English in
item_text_translated is an IRW translation.
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("izquierdo_lopez_2026_eosp")
TABLE = "izquierdo_lopez_2026_eosp"
INSTR = "Escala Observacional de Superdotación para Profesorado (EOSP)"
SECTIONS = {"A": "Área académica", "B": "Área de personalidad", "C": "Área de comportamiento interpersonal",
            "D": "Área de intereses y actitudes"}
SECTIONS_EN = {"A": "Academic area", "B": "Personality area", "C": "Interpersonal behaviour area",
               "D": "Interests and attitudes area"}
EN = {
    "ACI_A1": "LEVEL OF EXPRESSION: Ability to express themselves orally and in writing",
    "ACI_A2": "LEVEL OF VOCABULARY: Uses a rich and appropriate vocabulary. Good command of language",
    "ACI_A3": "LEVEL OF PROBLEM SOLVING: Ability to solve problems in the curricular domain",
    "ACI_A4": "LEVEL OF REASONING: Ability to reason in depth. Establishes complex relationships between ideas",
    "ACI_A5": "LEVEL OF CREATIVITY OR ORIGINALITY: Ability to generate something new, whether useful or beautiful",
    "ACI_A6": "LEVEL OF MEMORY: Ability to store, integrate and handle information appropriately",
    "ACI_A7": "LEVEL OF LEARNING: Ability to acquire knowledge and skills",
    "ACI_A8": "LEVEL OF ORGANISATION: Ability to plan their academic activities",
    "ACI_A9": "LEVEL OF PERFORMANCE: Capacity for work, making the most of the teaching-learning process",
    "ACI_B1": "IS ENTERPRISING: Accepts challenges and takes on tasks",
    "ACI_B2": "IS PERSISTENT: Perseveres in purposes and tasks",
    "ACI_B3": "IS OBSERVANT: Attentive to details, examines carefully",
    "ACI_B4": "IS RESPONSIBLE: Completes their tasks, takes care in doing them",
    "ACI_B5": "SHOWS INDEPENDENT JUDGEMENT: Presents and defines their ideas and opinions, is critical",
    "ACI_B6": "HAS A SENSE OF HUMOUR: Shows a subtle sense of humour, sometimes about situations that others do not notice",
    "ACI_B7": "IS SENSITIVE: Is moved by other people's problems, concerned about others",
    "ACI_B8": "HAS AN ETHICAL SENSE: Their conduct is moral, they side with \"the good\". Concerned about justice",
    "ACI_B9": "IS ENTHUSIASTIC: Is highly stimulated. Shows great interest and motivation for knowledge",
    "ACI_C1": "PREFERENCE FOR RELATING TO OLDER PEOPLE: Tends to relate to older peers and adults",
    "ACI_C2": "LEADERSHIP ABILITY: Inclined to coordinate (organises, guides, leads)",
    "ACI_C3": "IS RESPECTED BY PEERS: Is popular. Their opinions are accepted and respected by peers, though they sometimes cause surprise",
    "ACI_C4": "HAS SOCIAL SKILLS: Has the skills to interact and handle situations",
    "ACI_C5": "IS CONSIDERED INTELLIGENT BY PEERS: Peers consider them clever, capable",
    "ACI_C6": "IS SELF-SUFFICIENT: Able to carry out tasks without help",
    "ACI_C7": "HAS A STRONG CHARACTER: Firm, spirited, hard-working",
    "ACI_C8": "IS LIVELY WITH PEERS: Cheerful, fun, with a sense of humour",
    "ACI_C9": "HAS INITIATIVE: A personal quality that inclines them to be active, diligent",
    "ACI_D1": "IS CURIOUS: Is interested in knowing, asks questions",
    "ACI_D2": "KNOWS WHAT THEY WANT: Has clear goals",
    "ACI_D3": "INTEREST IN THEIR SURROUNDINGS: Inclined towards knowledge in diverse fields",
    "ACI_D4": "SELF-MOTIVATED: Committed to school activity, likes to learn",
    "ACI_D5": "QUESTIONS THE RULES: Reviews what is established, the rules, the teachers' statements",
    "ACI_D6": "HAS MANY PROJECTS: Has diverse plans, a reflection of their interests",
    "ACI_D7": "OPEN TO EXPLORATION: Likes to examine, find out, in diverse fields",
    "ACI_D8": "HAS MANY HOBBIES: Inclined towards diverse areas or activities not always present in the curriculum",
    "ACI_D9": "LIKES TO STUDY: Likes to learn and shows application",
}


def main():
    rows = []
    for code, stem in mod.stems():
        area = code[4]
        for r in range(1, 10):
            rows.append(row(TABLE, f"{TABLE}_{area}", code, INSTR, "Spanish", r, stem,
                            section_prompt=SECTIONS[area], item_text_tr=EN[code], section_prompt_tr=SECTIONS_EN[area]))
    write(TABLE, rows)


if __name__ == "__main__":
    main()
